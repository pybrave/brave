from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple
import uuid
import re


def _as_dict(value: Any) -> Dict[str, Any]:
	if isinstance(value, dict):
		return value
	return {}


def _node_key(node: Dict[str, Any]) -> str:
	return str(node.get("id") or node.get("name") or "")


def _node_name(node: Dict[str, Any]) -> str:
	return str(node.get("name") or node.get("id") or "node")


def _script_id(node: Dict[str, Any]) -> str:
	return str(node.get("script_id") or node.get("name") or node.get("id") or "")


def _sample_label(sample: Dict[str, Any], index: int) -> str:
	file_name = str(sample.get("file_name") or "").strip()
	if file_name:
		if "_" in file_name:
			token = file_name.split("_")[-1].strip()
			if token:
				return token.upper()
		if file_name[-1:].isdigit():
			digits = ""
			for ch in reversed(file_name):
				if ch.isdigit():
					digits = ch + digits
				else:
					break
			if digits:
				return f"S{digits}"
	return f"S{index + 1}"


def _sample_value(sample: Dict[str, Any], handle: str) -> Any:
	def _norm_key(key: str) -> str:
		return re.sub(r"[^a-z0-9]", "", key.lower())

	candidates = [handle]

	for key in candidates:
		if key in sample:
			return sample.get(key)

	normalized_sample_map = {_norm_key(str(k)): v for k, v in sample.items()}
	for key in candidates:
		norm = _norm_key(str(key))
		if norm in normalized_sample_map:
			return normalized_sample_map[norm]

	return None


def _edge_value(edge: Dict[str, Any], camel: str, snake: str) -> str:
	return str(edge.get(camel) or edge.get(snake) or "")


def _render_output_pattern(pattern: str, sample: Dict[str, Any], sample_label: str) -> str:
	sample_name = str(sample.get("file_name") or sample.get("sample_id") or sample_label)
	return pattern.replace("{sample}", sample_name)


def _topology(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[str]:
	node_ids = [_node_key(n) for n in nodes]
	indegree = {nid: 0 for nid in node_ids}
	graph = defaultdict(list)
	for e in edges:
		src = str(e.get("source", ""))
		dst = str(e.get("target", ""))
		if src in indegree and dst in indegree:
			graph[src].append(dst)
			indegree[dst] += 1

	queue = [nid for nid, d in indegree.items() if d == 0]
	order: List[str] = []
	while queue:
		cur = queue.pop(0)
		order.append(cur)
		for nxt in graph[cur]:
			indegree[nxt] -= 1
			if indegree[nxt] == 0:
				queue.append(nxt)

	if len(order) != len(node_ids):
		return node_ids
	return order


def _classify_nodes(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, str]:
	incoming = defaultdict(list)
	outgoing = defaultdict(list)
	node_map = {_node_key(n): n for n in nodes}

	for e in edges:
		src = str(e.get("source", ""))
		dst = str(e.get("target", ""))
		incoming[dst].append(e)
		outgoing[src].append(e)

	kind: Dict[str, str] = {}
	for nid in node_map:
		if len(incoming[nid]) == 0:
			kind[nid] = "sample"

	order = _topology(nodes, edges)
	for nid in order:
		if nid in kind:
			continue
		node = node_map[nid]
		inputs = _as_dict(node.get("inputs"))
		in_edges = incoming[nid]

		has_multiple_input = False
		for ie in in_edges:
			target_handle = _edge_value(ie, "targetHandle", "target_handle")
			target_cfg = _as_dict(inputs.get(target_handle))
			if bool(target_cfg.get("multiple")):
				has_multiple_input = True
				break

		if has_multiple_input:
			kind[nid] = "aggregate"
			continue

		has_outgoing = len(outgoing[nid]) > 0
		if not has_outgoing:
			kind[nid] = "aggregate"
			continue

		parent_kinds = {kind.get(str(ie.get("source")), "sample") for ie in in_edges}
		if parent_kinds == {"sample"}:
			kind[nid] = "sample"
		else:
			kind[nid] = "aggregate"

	return kind


def _decorate_runtime_graph(analysis_id: str, analysis_nodes: List[Dict[str, Any]], analysis_edges: List[Dict[str, Any]]) -> None:
	upstream = defaultdict(set)
	downstream = defaultdict(set)

	for idx, edge in enumerate(analysis_edges):
		source_node = str(edge.get("source_node") or "")
		target_node = str(edge.get("target_node") or "")
		edge["analysis_id"] = analysis_id
		edge["analysis_edge_id"] = edge.get("analysis_edge_id") or str(uuid.uuid4())

		source_handle = edge.get("source_handle")
		if source_handle is None:
			source_handle = edge.get("sourceHandle")
		target_handle = edge.get("target_handle")
		if target_handle is None:
			target_handle = edge.get("targetHandle")

		edge["source_handle"] = source_handle
		edge["target_handle"] = target_handle
		edge.pop("sourceHandle", None)
		edge.pop("targetHandle", None)

		if source_node and target_node:
			upstream[target_node].add(source_node)
			downstream[source_node].add(target_node)

	now_defaults = {
		"status": "pending",
		"retry": 0,
		"max_retry": 3,
		"cache_hit": False,
		"input_validation_errors": [],
	}

	for node in analysis_nodes:
		node_id = str(node.get("node_id") or "")
		node["analysis_id"] = analysis_id
		node["analysis_node_id"] = node.get("analysis_node_id") or str(uuid.uuid4())

		for key, value in now_defaults.items():
			if node.get(key) is None:
				node[key] = value

		node["upstream_ids"] = sorted(list(upstream.get(node_id, set())))
		node["downstream_ids"] = sorted(list(downstream.get(node_id, set())))


def build_runtime_tasks(analysis_id: str, params: Dict[str, Any], dag_definition: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
	input_params = params.get("inputs") or []
	if not isinstance(input_params, list):
		input_params = []

	if len(input_params) ==0:
		return {
			"analysis_nodes": [],
			"analysis_edges": [],
		}
		

	nodes = dag_definition.get("nodes") or []
	edges = dag_definition.get("edges") or []
	node_map = {_node_key(n): n for n in nodes}
	node_kind = _classify_nodes(nodes, edges)

	incoming = defaultdict(list)
	outgoing = defaultdict(list)
	for e in edges:
		src = str(e.get("source", ""))
		dst = str(e.get("target", ""))
		incoming[dst].append(e)
		outgoing[src].append(e)

	sample_labels = [_sample_label(sample, i) for i, sample in enumerate(input_params)]
	output_cache: Dict[Tuple[str, str, str], Any] = {}

	analysis_nodes: List[Dict[str, Any]] = []
	analysis_edges: List[Dict[str, Any]] = []
	order = _topology(nodes, edges)

	for nid in order:
		node = node_map.get(nid)
		if not node:
			continue

		name = _node_name(node)
		script_id = _script_id(node)
		node_params_defaults = _as_dict(params.get("node_params")).get(script_id)
		if node_params_defaults is None:
			node_params_defaults = _as_dict(params.get("node_params")).get(name)
		if node_params_defaults is None:
			node_params_defaults = _as_dict(node.get("params"))

		inputs = _as_dict(node.get("inputs"))
		outputs = _as_dict(node.get("outputs"))

		if node_kind.get(nid) == "sample":
			for i, sample in enumerate(input_params):
				sample_label = sample_labels[i]
				node_instance = f"{name}_{sample_label}"
				node_params = dict(_as_dict(node_params_defaults))
				resolved_inputs: Dict[str, Any] = {}

				for input_handle in inputs.keys():
					direct_value = _sample_value(sample, input_handle)
					if direct_value is not None:
						node_params[input_handle] = direct_value
						resolved_inputs[input_handle] = direct_value
						continue

					in_edge_match = next(
						(e for e in incoming[nid] if _edge_value(e, "targetHandle", "target_handle") == input_handle),
						None,
					)
					if in_edge_match:
						src = str(in_edge_match.get("source"))
						source_name = _node_name(node_map[src])
						source_instance = f"{source_name}_{sample_label}"
						source_handle = _edge_value(in_edge_match, "sourceHandle", "source_handle")
						resolved_value = output_cache.get((source_instance, source_handle, sample_label))
						node_params[input_handle] = resolved_value
						resolved_inputs[input_handle] = resolved_value

				node_resolved_outputs: Dict[str, Any] = {}
				for output_handle, output_cfg in outputs.items():
					output_value = node_params.get(output_handle)
					if output_value is None:
						output_value = _sample_value(sample, output_handle)
					if isinstance(output_cfg, dict):
						pattern = output_cfg.get("pattern")
						if isinstance(pattern, str) and pattern:
							output_value = _render_output_pattern(pattern, sample, sample_label)
					node_resolved_outputs[output_handle] = output_value
					output_cache[(node_instance, output_handle, sample_label)] = output_value

				analysis_nodes.append(
					{
						"analysis_id": analysis_id,
						"sample_id": str(sample.get("sample_id") or ""),
						"node_id": node_instance,
						"script_id": script_id,
						"inputs_patterns": inputs,
						"resolved_inputs": resolved_inputs,
						"output_patterns": outputs,
						"resolved_outputs": node_resolved_outputs,
						"params": node_params,
						"executor": str(params.get("executor") or ""),
						"max_retry": int(node.get("max_retry") or 3),
					}
				)

			for e in outgoing[nid]:
				target = str(e.get("target"))
				target_name = _node_name(node_map[target])
				target_kind = node_kind.get(target, "sample")
				source_handle = _edge_value(e, "sourceHandle", "source_handle")
				target_handle = _edge_value(e, "targetHandle", "target_handle")

				if target_kind == "sample":
					for sample_label in sample_labels:
						analysis_edges.append(
							{
								"analysis_id": analysis_id,
								"source_node": f"{name}_{sample_label}",
								"target_node": f"{target_name}_{sample_label}",
								"source_handle": source_handle,
								"target_handle": target_handle,
							}
						)
				else:
					for sample_label in sample_labels:
						analysis_edges.append(
							{
								"analysis_id": analysis_id,
								"source_node": f"{name}_{sample_label}",
								"target_node": target_name,
								"source_handle": source_handle,
								"target_handle": target_handle,
							}
						)

		else:
			node_instance = name
			node_params = dict(_as_dict(node_params_defaults))
			resolved_inputs: Dict[str, Any] = {}

			for input_handle in inputs.keys():
				values: List[Any] = []
				for in_edge in incoming[nid]:
					if _edge_value(in_edge, "targetHandle", "target_handle") != input_handle:
						continue
					src = str(in_edge.get("source"))
					source_name = _node_name(node_map[src])
					source_kind = node_kind.get(src, "sample")
					source_handle = _edge_value(in_edge, "sourceHandle", "source_handle")

					if source_kind == "sample":
						for sample_label in sample_labels:
							source_instance = f"{source_name}_{sample_label}"
							values.append(output_cache.get((source_instance, source_handle, sample_label)))
					else:
						values.append(output_cache.get((source_name, source_handle, "aggregate")))

				values = [v for v in values if v is not None]
				input_cfg = _as_dict(inputs.get(input_handle))
				is_list = bool(input_cfg.get("multiple")) or len(values) > 1
				if is_list:
					node_params[input_handle] = values
					resolved_inputs[input_handle] = values
				elif values:
					node_params[input_handle] = values[0]
					resolved_inputs[input_handle] = values[0]

			node_resolved_outputs: Dict[str, Any] = {}
			for output_handle, output_cfg in outputs.items():
				output_value = node_params.get(output_handle)
				if isinstance(output_cfg, dict):
					pattern = output_cfg.get("pattern")
					if isinstance(pattern, str) and pattern:
						output_value = pattern.replace("{sample}", "merged")
				node_resolved_outputs[output_handle] = output_value
				output_cache[(node_instance, output_handle, "aggregate")] = output_value

			analysis_nodes.append(
				{
					"analysis_id": analysis_id,
					"node_id": node_instance,
					"script_id": script_id,
					"inputs_patterns": inputs,
					"resolved_inputs": resolved_inputs,
					"output_patterns": outputs,
					"resolved_outputs": node_resolved_outputs,
					"params": node_params,
					"executor": str(params.get("executor") or ""),
					"max_retry": int(node.get("max_retry") or 3),
				}
			)

	_decorate_runtime_graph(analysis_id, analysis_nodes, analysis_edges)

	return {
		"analysis_nodes": analysis_nodes,
		"analysis_edges": analysis_edges,
	}
