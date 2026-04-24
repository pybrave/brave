
import asyncio
import json
import os
import shutil
import signal
from dependency_injector.wiring import inject
from fastapi import HTTPException
from brave.api.config.config import get_settings
from brave.api.config.db import get_engine
from brave.api.core.evenet_bus import EventBus
from brave.api.core.routers.analysis_executer_router import AnalysisExecutorRouter
from dependency_injector.wiring import inject, Provide
from brave.api.core.routers.git_executer_router import GitExecuterRouter
from brave.api.core.routers_name import RoutersName
from brave.api.dag.runtime_dag_queue_scheduler import RuntimeDagQueueScheduler
from brave.api.dag.running_dag_registry import running_dag_registry
from brave.api.executor.base import JobExecutor
from brave.api.schemas.analysis import AnalysisExecuterModal
from brave.api.service import analysis_node_service, analysis_runtime_engine_service, analysis_service
from brave.app_container import AppContainer
from brave.api.core.event import GitExecutorEvent, WorkflowEvent
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.executor.models import JobSpec, LocalJobSpec, DockerJobSpec
from brave.api.service.realtime_service import RealtimeService
from brave.api.service.result_parse.analysis_manage import AnalysisManage
from brave.api.executor.local_executor import LocalExecutor
from  brave.api.service import store_service 



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


async def stop_process(pid: int):
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return "not_found"
    except PermissionError as e:
        raise HTTPException(status_code=500, detail=f"Cannot terminate process {pid}: {str(e)}")

    # Give process a brief chance to exit gracefully, then force kill.
    for _ in range(5):
        await asyncio.sleep(0.2)
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





# def delete_store_record(store_id: str):
#     with get_engine().begin() as conn:
#         store_service.delete_store_db(conn, store_id)


async def monitor_clone_process(proc, lock_file, sse_service: RealtimeService = None, timeout=60):
    async def push_clone_sse(status: str, reason: str = None):
        if not sse_service or not store_id:
            return
        data = {
            "action": "component.invoke",
            "payload": {
                "category": "store",
                "id": store_id,
                "method": "clone",
                "args": {
                    "status": status,
                    "id": store_id,
                },
            },
        }
        if reason:
            data["payload"]["args"]["reason"] = reason
        await sse_service.push_message({"group": "default", "data": json.dumps(data)})

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
                # update_store_record(store_id=store_id, status="done", log=git_log)
                config_file = f"{target_path}/metadata.json"
                category = None
                if os.path.exists(config_file):
                    with open(config_file, "r") as f:
                        config_data = json.load(f)
                    if "category" in config_data:
                        category = config_data["category"]
                    # update_store_record(store_id=store_id, status="done", log=git_log, url=git_url)
                    category = config_data.get("category")
                store_service.update_store_status_db(store_id, "done", category=category)
                await push_clone_sse("done","clone_finished")

        elif store_id:
            await push_clone_sse("failed", "clone_nonzero_exit")
            store_service.delete_store_db(store_id)

        result = {
            "code": proc.returncode,
            "pid": proc.pid,
            "stdout": stdout.decode(errors="ignore"),
            "stderr": stderr.decode(errors="ignore"),
        }
        print(f"clone task finished: {result}")
        # await push_clone_sse("done", "clone_finished")

        return result
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        if store_id:
            await push_clone_sse("failed", "timeout")
            store_service.delete_store_db(store_id)
        result = {
            "error": "timeout",
            "pid": proc.pid,
        }
        print(f"clone task timeout: {result}")
        return result
    except asyncio.CancelledError:
        # Stop endpoint may cancel the monitor task after killing process.
        latest_lock_data = read_lock(lock_file) or {}
        if latest_lock_data.get("status") == "stopped":
            raise
        if store_id:
            # await push_clone_sse("failed", "cancelled")
            store_service.delete_store_db(store_id)
        raise
    except Exception:
        if store_id:
            # await push_clone_sse("failed", "exception")
            store_service.delete_store_db(store_id)
        raise
    finally:
        DOWNLOAD_TASKS.pop(lock_file, None)
        release_lock(lock_file)


async def monitor_pull_process(sse_service, proc, lock_file, timeout=60):
    async def pull_sse(status: str, reason: str = None):
        if not sse_service or not store_id:
            return
        data = {
            "action": "component.invoke",
            "payload": {
                "category": "store",
                "id": store_id,
                "method": "pull",
                "args": {
                    "status": status,
                    "id": store_id,
                },
            },
        }
        if reason:
            data["payload"]["args"]["reason"] = reason
        await sse_service.push_message({"group": "default", "data": json.dumps(data)})
    lock_data = read_lock(lock_file) or {}
    store_id = lock_data.get("store_id")
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        git_log = build_git_log(stdout, stderr)
        if proc.returncode == 0:
            if store_id:
                # update_store_record(store_id=store_id, status="done", log=git_log)
                store_service.update_store_status_db(store_id,"done")
        elif store_id:
            store_service.delete_store_db(store_id)
        result = {
            "code": proc.returncode,
            "pid": proc.pid,
            "stdout": stdout.decode(errors="ignore"),
            "stderr": stderr.decode(errors="ignore"),
        }
        print(f"pull task finished: {result}")
        await pull_sse("done", "pull_finished")
        return result
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        if store_id:
            store_service.delete_store_db(store_id)
        result = {
            "error": "timeout",
            "pid": proc.pid,
        }
        # await pull_sse("failed", "timeout")
        print(f"pull task timeout: {result}")
        return result
    except asyncio.CancelledError:
        latest_lock_data = read_lock(lock_file) or {}
        if latest_lock_data.get("status") == "stopped":
            raise
        if store_id:
            store_service.delete_store_db(store_id)
        # await pull_sse("failed", "cancelled")
        raise
    except Exception:
        
        if store_id:
            store_service.delete_store_db(store_id)
        # await pull_sse("failed", "exception")
        raise
    finally:
        DOWNLOAD_TASKS.pop(lock_file, None)
        release_lock(lock_file)


@inject
def setup_handlers(
    evenet_bus:EventBus  = Provide[AppContainer.event_bus],
    router:GitExecuterRouter  = Provide[AppContainer.git_executer_router],
    # job_executor:JobExecutor = Provide[AppContainer.job_executor_selector],
    sse_service:RealtimeService = Provide[AppContainer.sse_service]):
    
    evenet_bus.register_router(RoutersName.GIT_EXECUTER_ROUTER,router)


    @router.on_event(GitExecutorEvent.ON_GIT_CLONE)
    async def on_git_clone(payload:dict):
        print(f"🚀 [on_git_clone] ")
        store_id = payload.get("store_id")
        target_path = payload.get("target_path")
        url = payload.get("url")
        # exec git clone in subprocess
        settings = get_settings()
        store_dir = str(settings.STORE_DIR)
        lock_file = f"{target_path}.lock"
        if not acquire_lock(lock_file):
            raise HTTPException(status_code=500, detail=f"Another download task is running for {target_path}, please try again later!")
        if os.path.exists(target_path):
            if target_path.startswith(store_dir):
                shutil.rmtree(target_path)
            else:
                raise HTTPException(status_code=500, detail=f"Target path {target_path} already exists and is not under store directory!")
        
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
            # delete_store_record(store_id)
            store_service.delete_store_db(store_id)
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
        monitor_task = asyncio.create_task(monitor_clone_process(proc, lock_file, sse_service=sse_service))
        DOWNLOAD_TASKS[lock_file] = monitor_task
    
    @router.on_event(GitExecutorEvent.ON_GIT_PULL)
    async def on_git_pull(payload:dict):
        print(f"🚀 [on_git_pull] ")
        target_path = payload.get("target_path")
        url = payload.get("url")
        store_id = payload.get("store_id")
        lock_file = f"{target_path}.lock"
        if not acquire_lock(lock_file):
            raise HTTPException(status_code=500, detail=f"Another task is running for {target_path}, please try again later!")
        if not os.path.exists(target_path):
            release_lock(lock_file)
            raise HTTPException(status_code=404, detail=f"Store {target_path} not found!")
        if not os.path.isdir(target_path):
            release_lock(lock_file)
            raise HTTPException(status_code=400, detail=f"Store path {target_path} is not a directory!")
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

            monitor_task = asyncio.create_task(monitor_pull_process(sse_service, proc, lock_file))
            DOWNLOAD_TASKS[lock_file] = monitor_task


        except Exception as e:
            store_service.delete_store_db(store_id)
            release_lock(lock_file)
            raise HTTPException(status_code=500, detail=f"Git pull failed: {str(e)}")



    
    @router.on_event(GitExecutorEvent.ON_GIT_PUSH)
    async def on_git_push(payload:dict):
        print(f"🚀 [on_git_push] ")
    
    @router.on_event(GitExecutorEvent.ON_GIT_STOP)
    async def on_git_stop(payload:dict):
        print(f"🚀 [on_git_stop] ")
        target_path = payload.get("target_path")
        lock_file = f"{target_path}.lock"
        lock_data = read_lock(lock_file)
        if not lock_data:
            store_service.update_store_status_db(payload.get("store_id"), "done")
            raise HTTPException(status_code=404, detail=f"Lock file not found for {target_path}")

        store_id = lock_data.get("store_id")
        operation = lock_data.get("operation") or "clone"
        pid = lock_data.get("pid")
        process_status = "pid_missing"

        update_lock(
            lock_file,
            {
                **lock_data,
                "status": "stopped",
            },
        )

        if pid:
            process_status = await stop_process(int(pid))

        task = DOWNLOAD_TASKS.pop(lock_file, None)
        if task and not task.done():
            task.cancel()

        if store_id:
            store_service.update_store_status_db(store_id, "done")
            data = {
                "action": "component.invoke",
                "payload": {
                    "category": "store",
                    "id": store_id,
                    "method": "stop",
                    "args": {
                        "status": "done",
                        "id": store_id,
                        "process_status": process_status,
                    },
                },
            }
            await sse_service.push_message({"group": "default", "data": json.dumps(data)})

        release_lock(lock_file)

