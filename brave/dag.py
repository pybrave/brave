import os
import re
import json
import time
import uuid
import hashlib
import threading
import subprocess
import concurrent.futures

from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Any, Set, Optional


# ============================================================
# Utils
# ============================================================

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def now_ts() -> float:
    return time.time()


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


# ============================================================
# Data Models
# ============================================================

@dataclass
class EdgeConfig:
    from_node: str
    to_node: str


@dataclass
class NodeConfig:
    node_id: str
    name: str
    template: str
    outputs: Dict[str, str] = field(default_factory=dict)


@dataclass
class TaskResult:
    node_id: str
    name: str
    workdir: Path
    exit_code: int
    outputs: Dict[str, str] = field(default_factory=dict)


@dataclass
class TaskContext:
    params: Dict[str, Any]
    upstream_results: Dict[str, TaskResult]
    node: NodeConfig
    workdir: Path


# ============================================================
# Workflow Config
# ============================================================

class WorkflowConfig:
    def __init__(self, nodes: Dict[str, NodeConfig], edges: List[EdgeConfig]):
        self.nodes = nodes
        self.edges = edges

        self.graph: Dict[str, List[str]] = defaultdict(list)
        self.reverse_graph: Dict[str, List[str]] = defaultdict(list)

        for node_id in nodes:
            self.graph[node_id] = []
            self.reverse_graph[node_id] = []

        for e in edges:
            if e.from_node not in nodes:
                raise ValueError(f"Unknown source node in edge: {e.from_node}")
            if e.to_node not in nodes:
                raise ValueError(f"Unknown target node in edge: {e.to_node}")
            self.graph[e.from_node].append(e.to_node)
            self.reverse_graph[e.to_node].append(e.from_node)

    @classmethod
    def from_json(cls, path: Path) -> "WorkflowConfig":
        data = read_json(path)

        nodes: Dict[str, NodeConfig] = {}
        for item in data.get("nodes", []):
            node_id = item["id"]
            if node_id in nodes:
                raise ValueError(f"Duplicate node id: {node_id}")
            nodes[node_id] = NodeConfig(
                node_id=node_id,
                name=item.get("name", node_id),
                template=item["template"],
                outputs=item.get("outputs", {}),
            )

        edges = [
            EdgeConfig(from_node=e["from"], to_node=e["to"])
            for e in data.get("edges", [])
        ]

        return cls(nodes=nodes, edges=edges)

    def has_cycle(self) -> bool:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False


# ============================================================
# Template Renderer
# 支持:
#   {{params.xxx}}
#   {{inputs.A.a_txt}}
#   {{workdir}}
# ============================================================

class TemplateRenderer:
    _pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")

    def render(self, template: str, ctx: TaskContext) -> str:
        def replace(match: re.Match) -> str:
            expr = match.group(1)
            return self.resolve(expr, ctx)

        return self._pattern.sub(replace, template)

    def resolve(self, expr: str, ctx: TaskContext) -> str:
        parts = expr.split(".")
        root = parts[0]

        if root == "params":
            return self._resolve_params(parts[1:], ctx.params, expr)

        if root == "inputs":
            return self._resolve_inputs(parts[1:], ctx.upstream_results, expr)

        if root == "workdir":
            if len(parts) != 1:
                raise ValueError(f"Invalid workdir expression: {expr}")
            return str(ctx.workdir)

        raise ValueError(f"Unsupported template expression: {expr}")

    def _resolve_params(self, parts: List[str], params: Dict[str, Any], expr: str) -> str:
        cur: Any = params
        for p in parts:
            if not isinstance(cur, dict) or p not in cur:
                raise KeyError(f"Cannot resolve template expression: {expr}")
            cur = cur[p]
        return str(cur)

    def _resolve_inputs(self, parts: List[str], upstream_results: Dict[str, TaskResult], expr: str) -> str:
        if len(parts) < 2:
            raise ValueError(f"Invalid inputs expression: {expr}")

        node_id = parts[0]
        output_key = parts[1]

        if node_id not in upstream_results:
            raise KeyError(f"Upstream node not found in expression: {expr}")

        result = upstream_results[node_id]
        if output_key not in result.outputs:
            raise KeyError(f"Output key not found in expression: {expr}")

        return str(result.outputs[output_key])


# ============================================================
# WorkDir Manager
# ============================================================

class WorkDirManager:
    def __init__(self, root: Path):
        self.root = root
        ensure_dir(self.root)

    def create_task_dir(self, node_id: str, fingerprint: str) -> Path:
        short_hash = sha1_text(f"{node_id}:{fingerprint}:{uuid.uuid4().hex}")[:12]
        path = self.root / f"{node_id}_{short_hash}"
        ensure_dir(path)
        return path


# ============================================================
# Task Runner
# ============================================================

class TaskRunner:
    def __init__(self, renderer: TemplateRenderer):
        self.renderer = renderer

    def run(self, ctx: TaskContext) -> TaskResult:
        node = ctx.node
        workdir = ctx.workdir

        command_sh = workdir / ".command.sh"
        stdout_file = workdir / ".stdout"
        stderr_file = workdir / ".stderr"
        exitcode_file = workdir / ".exitcode"
        status_file = workdir / ".status.json"

        rendered_script = self.renderer.render(node.template, ctx)
        write_text(command_sh, rendered_script)
        os.chmod(command_sh, 0o755)

        status = {
            "node_id": node.node_id,
            "name": node.name,
            "workdir": str(workdir),
            "status": "RUNNING",
            "start_time": now_ts(),
            "end_time": None,
            "exit_code": None,
            "thread": threading.current_thread().name,
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
                f"Node {node.node_id} failed with exit code {exit_code}. "
                f"See stderr: {stderr_file}"
            )

        outputs: Dict[str, str] = {}
        for key, rel_path in node.outputs.items():
            outputs[key] = str((workdir / rel_path).resolve())

        return TaskResult(
            node_id=node.node_id,
            name=node.name,
            workdir=workdir,
            exit_code=exit_code,
            outputs=outputs,
        )


# ============================================================
# Parallel DAG Engine
# 参考你给的 DAG.execute() 改造
# ============================================================

class DAGEngine:
    def __init__(self, workflow: WorkflowConfig, params: Dict[str, Any], work_root: Path):
        self.workflow = workflow
        self.params = params
        self.work_root = work_root

        self.workdir_manager = WorkDirManager(work_root)
        self.renderer = TemplateRenderer()
        self.runner = TaskRunner(self.renderer)

        self.results: Dict[str, TaskResult] = {}
        self.results_lock = threading.Lock()

    def _build_fingerprint(self, node_id: str) -> str:
        dep_outputs = {}
        for dep in self.workflow.reverse_graph[node_id]:
            dep_outputs[dep] = self.results[dep].outputs

        payload = {
            "node_id": node_id,
            "params": self.params,
            "dep_outputs": dep_outputs,
        }
        return json.dumps(payload, sort_keys=True, ensure_ascii=False)

    def _run_one_node(self, node_id: str) -> TaskResult:
        node = self.workflow.nodes[node_id]

        with self.results_lock:
            upstream_results = {
                dep: self.results[dep]
                for dep in self.workflow.reverse_graph[node_id]
            }

        fingerprint = self._build_fingerprint(node_id)
        workdir = self.workdir_manager.create_task_dir(node_id, fingerprint)

        print(f"[engine] preparing node={node_id}, workdir={workdir}")

        ctx = TaskContext(
            params=self.params,
            upstream_results=upstream_results,
            node=node,
            workdir=workdir,
        )

        result = self.runner.run(ctx)
        return result

    def _update_dependents(self, completed_node: str, in_degree: Dict[str, int], queue: deque) -> None:
        for neighbor in self.workflow.graph[completed_node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    def execute(self, max_workers: int = 4) -> Dict[str, TaskResult]:
        if self.workflow.has_cycle():
            raise ValueError("Cannot execute workflow with cycles.")

        in_degree = {
            node_id: len(self.workflow.reverse_graph[node_id])
            for node_id in self.workflow.nodes
        }
        ready_queue = deque([node_id for node_id, deg in in_degree.items() if deg == 0])

        print(f"[engine] start execution with max_workers={max_workers}")
        print(f"[engine] initial ready nodes={list(ready_queue)}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures: Dict[concurrent.futures.Future, str] = {}

            while ready_queue or futures:
                # 1. 提交所有 ready 节点
                while ready_queue:
                    node_id = ready_queue.popleft()
                    print(f"[engine] submitting node={node_id}")
                    future = executor.submit(self._run_one_node, node_id)
                    futures[future] = node_id

                if not futures:
                    break

                # 2. 等待任意一个完成
                done, _ = concurrent.futures.wait(
                    futures.keys(),
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )

                for future in done:
                    node_id = futures.pop(future)
                    try:
                        result = future.result()
                        with self.results_lock:
                            self.results[node_id] = result
                        print(f"[engine] completed node={node_id}, outputs={result.outputs}")
                    except Exception as e:
                        print(f"[engine] node failed: {node_id}, error={e}")
                        # 这里直接抛错，整个 workflow 失败
                        raise

                    self._update_dependents(node_id, in_degree, ready_queue)

        if len(self.results) != len(self.workflow.nodes):
            missing = set(self.workflow.nodes) - set(self.results)
            raise RuntimeError(f"Workflow finished but some nodes were not executed: {missing}")

        return self.results


# ============================================================
# Main
# ============================================================

def main() -> None:
    params = read_json(Path("brave/mini_nextflow/params.json"))
    workflow = WorkflowConfig.from_json(Path("brave/mini_nextflow/workflow.json"))

    work_root = Path(params.get("output_root", "./work")).resolve()
    ensure_dir(work_root)

    engine = DAGEngine(
        workflow=workflow,
        params=params,
        work_root=work_root,
    )

    results = engine.execute(max_workers=4)

    print("\n=== FINAL RESULTS ===")
    for node_id, result in results.items():
        print(f"{node_id}:")
        print(f"  workdir   = {result.workdir}")
        print(f"  exit_code = {result.exit_code}")
        print(f"  outputs   = {result.outputs}")


if __name__ == "__main__":
    main()