import asyncio
import json
import os
import shutil
import signal
import time
from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends, HTTPException

from brave.api.config.config import get_settings
from brave.api.config.db import get_engine
from brave.api.core.evenet_bus import EventBus
from brave.api.schemas.store import CreateStore
from  brave.api.service import store_service 

from brave.api.service.sse_service import SSESessionService
from brave.app_container import AppContainer

store_api = APIRouter()
DOWNLOAD_TASKS = {}

def acquire_lock(lock_file):
    if os.path.exists(lock_file):
        return False
    with open(lock_file, "w") as f:
        json.dump({"status": "pending", "pid": None}, f)
    return True


def update_lock(lock_file, lock_data: dict):
    with open(lock_file, "w") as f:
        json.dump(lock_data, f)


def read_lock(lock_file):
    if not os.path.exists(lock_file):
        return None
    try:
        with open(lock_file, "r") as f:
            return json.load(f)
    except Exception:
        # Backward compatibility with old plain-text lock content.
        with open(lock_file, "r") as f:
            return {"status": f.read().strip(), "pid": None}

def release_lock(lock_file):
    if os.path.exists(lock_file):
        os.remove(lock_file)


def stop_process(pid: int):
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return "not_found"
    except PermissionError as e:
        raise HTTPException(status_code=500, detail=f"Cannot terminate process {pid}: {str(e)}")

    # Give process a brief chance to exit gracefully, then force kill.
    for _ in range(5):
        time.sleep(0.2)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return "terminated"

    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return "terminated"
    except PermissionError as e:
        raise HTTPException(status_code=500, detail=f"Cannot kill process {pid}: {str(e)}")

    return "killed"


def write_repo_config(target_path: str, url: str):
    config_file = f"{target_path}/.config"
    config_data = {"git_url": url}
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)


def create_store_record(name: str, url: str, status: str, log: str = None, store_id: str = None):
    with get_engine().begin() as conn:
        payload = CreateStore(
            store_id=store_id,
            name=name,
            url=url,
            status=status,
            log=log,
        )
        return store_service.create_store_db(conn, payload)


def update_store_record(store_id: str, status: str, log: str = None):
    with get_engine().begin() as conn:
        store_service.update_store_db(conn, store_id, CreateStore(status=status, log=log))


def delete_store_record(store_id: str):
    with get_engine().begin() as conn:
        store_service.delete_store_db(conn, store_id)


def build_git_log(stdout: bytes = b"", stderr: bytes = b"", error: str = None):
    stdout_text = (stdout or b"").decode(errors="ignore")
    stderr_text = (stderr or b"").decode(errors="ignore")
    parts = []
    if error:
        parts.append(error)
    if stdout_text:
        parts.append(f"stdout:\n{stdout_text}")
    if stderr_text:
        parts.append(f"stderr:\n{stderr_text}")
    return "\n\n".join(parts) if parts else None


async def monitor_clone_process(proc, lock_file, timeout=60):
    lock_data = read_lock(lock_file) or {}
    store_id = lock_data.get("store_id")
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        lock_data = read_lock(lock_file) or lock_data
        store_id = lock_data.get("store_id")
        git_log = build_git_log(stdout, stderr)
        if proc.returncode == 0:
            target_path = lock_data.get("target_path")
            url = lock_data.get("url")
            if target_path and url and os.path.isdir(target_path):
                write_repo_config(target_path, url)
            if store_id:
                update_store_record(store_id=store_id, status="done", log=git_log)
        elif store_id:
            delete_store_record(store_id)

        result = {
            "code": proc.returncode,
            "pid": proc.pid,
            "stdout": stdout.decode(errors="ignore"),
            "stderr": stderr.decode(errors="ignore"),
        }
        print(f"clone task finished: {result}")
        return result
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        if store_id:
            delete_store_record(store_id)
        result = {
            "error": "timeout",
            "pid": proc.pid,
        }
        print(f"clone task timeout: {result}")
        return result
    except asyncio.CancelledError:
        # Stop endpoint may cancel the monitor task after killing process.
        if store_id:
            delete_store_record(store_id)
        raise
    except Exception:
        if store_id:
            delete_store_record(store_id)
        raise
    finally:
        DOWNLOAD_TASKS.pop(lock_file, None)
        release_lock(lock_file)


async def monitor_pull_process(proc, lock_file, timeout=60):
    lock_data = read_lock(lock_file) or {}
    store_id = lock_data.get("store_id")
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        git_log = build_git_log(stdout, stderr)
        if proc.returncode == 0:
            if store_id:
                update_store_record(store_id=store_id, status="done", log=git_log)
        elif store_id:
            delete_store_record(store_id)
        result = {
            "code": proc.returncode,
            "pid": proc.pid,
            "stdout": stdout.decode(errors="ignore"),
            "stderr": stderr.decode(errors="ignore"),
        }
        print(f"pull task finished: {result}")
        return result
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        if store_id:
            delete_store_record(store_id)
        result = {
            "error": "timeout",
            "pid": proc.pid,
        }
        print(f"pull task timeout: {result}")
        return result
    except asyncio.CancelledError:
        if store_id:
            delete_store_record(store_id)
        raise
    except Exception:
        if store_id:
            delete_store_record(store_id)
        raise
    finally:
        DOWNLOAD_TASKS.pop(lock_file, None)
        release_lock(lock_file)

@store_api.post("/create-store",tags=['pipeline'])
@inject
async def create_store(createStore: CreateStore,
                        evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) ):
    settings = get_settings()
    store_path = f"{settings.STORE_DIR}"
    url = createStore.url
    force = createStore.force
    filename = url.split("/")[-1]

    
    target_path = f"{store_path}/{filename.replace('.git','')}"
    lock_file = f"{target_path}.lock"

    if not acquire_lock(lock_file):
        raise HTTPException(status_code=500, detail=f"Another download task is running for {filename}, please try again later!")
    if os.path.exists(target_path):
        if force:
            shutil.rmtree(target_path)
        else:
            release_lock(lock_file)
            return {
                "message": "success",
                "target_path": target_path,
                "cmd": f"git clone {url} {target_path}",
                "info": {
                    "message": f"Store {target_path} already exists! If you want to overwrite it, please set force to true.",
                    "pid": None,
                },
            }

    store_id = create_store_record(
        name=filename.replace('.git', ''),
        url=url,
        status="running",
        log=f"git clone {url} {target_path}",
    )

    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            url,
            target_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as e:
        delete_store_record(store_id)
        release_lock(lock_file)
        raise HTTPException(status_code=500, detail=f"Git clone failed: {str(e)}")

    update_lock(
        lock_file,
        {
            "status": "running",
            "pid": proc.pid,
            "url": url,
            "target_path": target_path,
            "store_id": store_id,
            "operation": "clone",
        },
    )

    monitor_task = asyncio.create_task(monitor_clone_process(proc, lock_file))
    DOWNLOAD_TASKS[lock_file] = monitor_task

    return {
        "message": "success",
        "target_path": target_path,
        "cmd": f"git clone {url} {target_path}",
        "info": {
            "status": "submitted",
            "pid": proc.pid,
        },
    }

@store_api.post("/git-stop", tags=['pipeline'])
@inject
async def git_stop(createStore: CreateStore,
                    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) ):
    
    settings = get_settings()
    store_path = f"{settings.STORE_DIR}"
    url = createStore.url
    filename = url.split("/")[-1]
    target_path = f"{store_path}/{filename.replace('.git','')}"
    lock_file = f"{target_path}.lock"

    lock_data = read_lock(lock_file)
    if not lock_data:
        raise HTTPException(status_code=404, detail=f"Lock file not found for {filename}")

    pid = lock_data.get("pid")
    process_status = "pid_missing"
    if pid:
        process_status = stop_process(int(pid))

    task = DOWNLOAD_TASKS.pop(lock_file, None)
    if task and not task.done():
        task.cancel()

    release_lock(lock_file)
    return {
        "message": "success",
        "target_path": target_path,
        "lock_file": lock_file,
        "pid": pid,
        "process_status": process_status,
    }



                        
@store_api.post("/git-pull", tags=['pipeline'])
@inject
async def git_pull(createStore: CreateStore,
                    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus])):
    settings = get_settings()
    store_path = f"{settings.STORE_DIR}"
    url = createStore.url
    filename = url.split("/")[-1]
    target_path = f"{store_path}/{filename.replace('.git','')}"
    lock_file = f"{target_path}.lock"

    if not acquire_lock(lock_file):
        raise HTTPException(status_code=500, detail=f"Another task is running for {filename}, please try again later!")

    if not os.path.exists(target_path):
        release_lock(lock_file)
        raise HTTPException(status_code=404, detail=f"Store {target_path} not found!")
    if not os.path.isdir(target_path):
        release_lock(lock_file)
        raise HTTPException(status_code=400, detail=f"Store path {target_path} is not a directory!")

    store_id = create_store_record(
        name=filename.replace('.git', ''),
        url=url,
        status="running",
        log=f"git -C {target_path} pull",
    )
    
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "-C",
            target_path,
            "pull",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        update_lock(
            lock_file,
            {
                "status": "running",
                "pid": proc.pid,
                "url": url,
                "target_path": target_path,
                "store_id": store_id,
                "operation": "pull",
            },
        )

        monitor_task = asyncio.create_task(monitor_pull_process(proc, lock_file))
        DOWNLOAD_TASKS[lock_file] = monitor_task

        return {
            "message": "success",
            "target_path": target_path,
            "cmd": f"git -C {target_path} pull",
            "info": {
                "status": "submitted",
                "pid": proc.pid,
            },
        }
    except Exception as e:
        delete_store_record(store_id)
        release_lock(lock_file)
        raise HTTPException(status_code=500, detail=f"Git pull failed: {str(e)}")

