import os
import json
import time
import uuid
import shutil
import hashlib
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


# =========================
# Utilities
# =========================

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def now_ts() -> float:
    return time.time()


# =========================
# Task / Runtime Models
# =========================

@dataclass
class TaskResult:
    task_id: str
    name: str
    workdir: Path
    exit_code: int
    outputs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskContext:
    params: Dict[str, Any]
    upstream: Dict[str, TaskResult]
    task_name: str
    workdir: Path


class ProcessNode:
    """
    类似 Nextflow 的 process 定义：
    - name: 节点名
    - deps: 依赖哪些上游节点
    - script(ctx): 生成 .command.sh 内容
    - collect_outputs(ctx): 从任务工作目录提取输出给下游
    """

    def __init__(self, name: str, deps: Optional[List[str]] = None):
        self.name = name
        self.deps = deps or []

    def script(self, ctx: TaskContext) -> str:
        raise NotImplementedError

    def collect_outputs(self, ctx: TaskContext) -> Dict[str, Any]:
        return {}


# =========================
# Example Nodes: A -> B
# =========================

class NodeA(ProcessNode):
    def __init__(self):
        super().__init__(name="A", deps=[])

    def script(self, ctx: TaskContext) -> str:
        name = ctx.params.get("name", "unknown")
        message = ctx.params.get("message", "")
        out_file = ctx.workdir / "a.txt"

        # 注意：这里直接生成 bash 脚本内容
        return f"""#!/usr/bin/env bash
set -euo pipefail

echo "[A] start"
echo "name={name}" > "{out_file}"
echo "message={message}" >> "{out_file}"
echo "generated_by=A" >> "{out_file}"

echo "[A] wrote {out_file}"
echo "[A] done"
"""

    def collect_outputs(self, ctx: TaskContext) -> Dict[str, Any]:
        out_file = ctx.workdir / "a.txt"
        return {
            "a_txt": str(out_file),
        }


class NodeB(ProcessNode):
    def __init__(self):
        super().__init__(name="B", deps=["A"])

    def script(self, ctx: TaskContext) -> str:
        a_result = ctx.upstream["A"]
        a_txt = a_result.outputs["a_txt"]
        out_file = ctx.workdir / "b.txt"

        return f"""#!/usr/bin/env bash
set -euo pipefail

echo "[B] start"
echo "[B] reading upstream file: {a_txt}"

cat "{a_txt}" > "{out_file}"
echo "processed_by=B" >> "{out_file}"

echo "[B] wrote {out_file}"
echo "[B] done"
"""

    def collect_outputs(self, ctx: TaskContext) -> Dict[str, Any]:
        out_file = ctx.workdir / "b.txt"
        return {
            "b_txt": str(out_file),
        }


# =========================
# Work Directory Management
# =========================

class WorkDirManager:
    """
    模拟 Nextflow 的 work 目录：
    每个 task run 分配一个唯一目录，比如：
    work/A_<hash>
    work/B_<hash>
    """

    def __init__(self, root: Path):
        self.root = root
        ensure_dir(self.root)

    def create_task_dir(self, task_name: str, fingerprint: str) -> Path:
        short_hash = sha1_text(f"{task_name}:{fingerprint}:{uuid.uuid4().hex}")[:12]
        task_dir = self.root / f"{task_name}_{short_hash}"
        ensure_dir(task_dir)
        return task_dir


# =========================
# Task Runner
# =========================

class TaskRunner:
    def run(self, node: ProcessNode, ctx: TaskContext) -> TaskResult:
        workdir = ctx.workdir
        command_sh = workdir / ".command.sh"
        stdout_file = workdir / ".stdout"
        stderr_file = workdir / ".stderr"
        exitcode_file = workdir / ".exitcode"
        status_file = workdir / ".status.json"

        script_content = node.script(ctx)
        write_text(command_sh, script_content)
        os.chmod(command_sh, 0o755)

        status = {
            "task_name": node.name,
            "workdir": str(workdir),
            "status": "RUNNING",
            "start_time": now_ts(),
            "end_time": None,
            "exit_code": None,
        }
        write_text(status_file, json.dumps(status, indent=2, ensure_ascii=False))

        with stdout_file.open("w", encoding="utf-8") as out, stderr_file.open("w", encoding="utf-8") as err:
            proc = subprocess.run(
                ["bash", str(command_sh)],
                cwd=str(workdir),
                stdout=out,
                stderr=err,
                text=True,
                check=False,
            )
            exit_code = proc.returncode

        write_text(exitcode_file, str(exit_code))

        status["end_time"] = now_ts()
        status["exit_code"] = exit_code
        status["status"] = "COMPLETED" if exit_code == 0 else "FAILED"
        write_text(status_file, json.dumps(status, indent=2, ensure_ascii=False))

        if exit_code != 0:
            raise RuntimeError(
                f"Task {node.name} failed with exit code {exit_code}. "
                f"See: {stderr_file}"
            )

        outputs = node.collect_outputs(ctx)

        return TaskResult(
            task_id=node.name,
            name=node.name,
            workdir=workdir,
            exit_code=exit_code,
            outputs=outputs,
        )


# =========================
# DAG Engine
# =========================

class DAGEngine:
    def __init__(self, nodes: List[ProcessNode], params: Dict[str, Any], work_root: Path):
        self.params = params
        self.nodes: Dict[str, ProcessNode] = {n.name: n for n in nodes}
        self.workdir_manager = WorkDirManager(work_root)
        self.runner = TaskRunner()
        self.results: Dict[str, TaskResult] = {}

    def topological_sort(self) -> List[str]:
        visited = set()
        visiting = set()
        order: List[str] = []

        def dfs(name: str) -> None:
            if name in visited:
                return
            if name in visiting:
                raise ValueError(f"Cycle detected at node: {name}")

            visiting.add(name)
            node = self.nodes[name]
            for dep in node.deps:
                if dep not in self.nodes:
                    raise ValueError(f"Node {name} depends on unknown node {dep}")
                dfs(dep)
            visiting.remove(name)
            visited.add(name)
            order.append(name)

        for name in self.nodes:
            dfs(name)

        return order

    def build_fingerprint(self, node: ProcessNode) -> str:
        dep_outputs = {}
        for dep in node.deps:
            dep_result = self.results[dep]
            dep_outputs[dep] = dep_result.outputs

        payload = {
            "node": node.name,
            "params": self.params,
            "deps": dep_outputs,
        }
        return json.dumps(payload, sort_keys=True, ensure_ascii=False)

    def run(self) -> Dict[str, TaskResult]:
        order = self.topological_sort()
        print(f"[engine] execution order: {order}")

        for node_name in order:
            node = self.nodes[node_name]

            # 检查依赖是否完成
            upstream = {}
            for dep in node.deps:
                if dep not in self.results:
                    raise RuntimeError(f"Dependency {dep} for node {node_name} not completed")
                upstream[dep] = self.results[dep]

            fingerprint = self.build_fingerprint(node)
            workdir = self.workdir_manager.create_task_dir(node.name, fingerprint)

            print(f"[engine] preparing task {node.name} in {workdir}")

            ctx = TaskContext(
                params=self.params,
                upstream=upstream,
                task_name=node.name,
                workdir=workdir,
            )

            result = self.runner.run(node, ctx)
            self.results[node.name] = result

            print(f"[engine] task {node.name} completed, outputs={result.outputs}")

        return self.results


# =========================
# Main
# =========================

def load_params(params_file: str) -> Dict[str, Any]:
    with open(params_file, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    params = load_params("brave/mini_nextflow/params.json")
    work_root = Path(params.get("output_root", "./work")).resolve()

    if work_root.exists():
        ensure_dir(work_root)


    nodes: List[ProcessNode] = [
        NodeA(),
        NodeB(),
    ]

    engine = DAGEngine(nodes=nodes, params=params, work_root=work_root)
    results = engine.run()

    print("\n=== Final Results ===")
    for name, result in results.items():
        print(f"{name}:")
        print(f"  workdir   = {result.workdir}")
        print(f"  exit_code = {result.exit_code}")
        print(f"  outputs   = {result.outputs}")


if __name__ == "__main__":
    main()