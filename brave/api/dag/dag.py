
from collections import defaultdict
import json
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


def _schema_type(schema: Dict[str, Any]) -> str:
	return str(schema.get("type") or "").strip().lower()


def _scatter_field(node: Dict[str, Any]) -> str:
	scatter = _as_dict(node.get("scatter"))
	if str(scatter.get("mode") or "").strip().lower() != "each":
		return ""
	return str(scatter.get("field") or "").strip()


def _derive_upstream_sample_labels(
	nid: str,
	incoming: Dict[str, List[Dict[str, Any]]],
	node_kind: Dict[str, str],
	node_labels: Dict[str, List[str]],
) -> List[str]:
	label_sets: List[List[str]] = []
	for in_edge in incoming.get(nid, []):
		src = str(in_edge.get("source"))
		if node_kind.get(src) != "sample":
			continue
		src_labels = list(node_labels.get(src) or [])
		if src_labels:
			label_sets.append(src_labels)

	if not label_sets:
		return []

	ordered_base = label_sets[0]
	for labels in label_sets[1:]:
		allowed = set(labels)
		ordered_base = [label for label in ordered_base if label in allowed]

	if ordered_base:
		return ordered_base

	merged: List[str] = []
	for labels in label_sets:
		for label in labels:
			if label not in merged:
				merged.append(label)
	return merged


def _required_property_names(schema: Dict[str, Any]) -> List[str]:
	return [
		str(name)
		for name, cfg in _as_dict(schema.get("properties")).items()
		if bool(_as_dict(cfg).get("required"))
	]


def _collect_required_input_errors(input_handle: str, input_schema: Dict[str, Any], value: Any) -> List[str]:
	errors: List[str] = []
	schema_type = _schema_type(input_schema)

	if schema_type == "object":
		if not isinstance(value, dict):
			if bool(input_schema.get("required")):
				errors.append(f"missing required input: {input_handle}")
			return errors
		for prop in _required_property_names(input_schema):
			if value.get(prop) is None:
				errors.append(f"missing required input: {input_handle}.{prop}")
		return errors

	if schema_type == "list":
		item_schema = _as_dict(input_schema.get("items"))
		if _schema_type(item_schema) != "object":
			if bool(input_schema.get("required")) and value is None:
				errors.append(f"missing required input: {input_handle}")
			return errors

		if not isinstance(value, dict):
			if bool(input_schema.get("required")):
				errors.append(f"missing required input: {input_handle}")
			return errors

		for prop in _required_property_names(item_schema):
			if value.get(prop) is None:
				errors.append(f"missing required input: {input_handle}.{prop}")
		return errors

	if bool(input_schema.get("required")) and value is None:
		errors.append(f"missing required input: {input_handle}")

	return errors


def _project_input_value_by_schema(value: Any, input_schema: Dict[str, Any]) -> Any:
	schema_type = _schema_type(input_schema)

	if schema_type == "object":
		properties = _as_dict(input_schema.get("properties"))
		if isinstance(value, dict):
			return {key: value.get(key) for key in properties.keys() if value.get(key) is not None}
		return value

	if schema_type == "list":
		item_schema = _as_dict(input_schema.get("items"))
		if _schema_type(item_schema) != "object":
			return value
		properties = _as_dict(item_schema.get("properties"))
		if isinstance(value, dict):
			return {key: value.get(key) for key in properties.keys() if value.get(key) is not None}
		return value

	return value


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
	with open("debug_dag_definition.json", "w") as f:
		json.dump(dag_definition, f, indent=2)
	with open("debug_dag_params.json", "w") as f:
		json.dump(params, f, indent=2)
		
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

	output_cache: Dict[Tuple[str, str, str], Any] = {}
	node_labels: Dict[str, List[str]] = {}
	node_samples_map: Dict[str, Dict[str, Dict[str, Any]]] = {}

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
			scatter_field = _scatter_field(node)
			node_samples: List[Dict[str, Any]] = []
			node_sample_labels: List[str] = []

			if scatter_field:
				raw_samples = params.get(scatter_field)
				if not isinstance(raw_samples, list):
					return {
						"analysis_nodes": [],
						"analysis_edges": [],
					}
				node_samples = [dict(item) for item in raw_samples if isinstance(item, dict)]
				node_sample_labels = [_sample_label(sample, i) for i, sample in enumerate(node_samples)]
			else:
				upstream_labels = _derive_upstream_sample_labels(nid, incoming, node_kind, node_labels)
				if upstream_labels:
					node_sample_labels = list(upstream_labels)
					for label in node_sample_labels:
						sample_payload: Dict[str, Any] = dict(params) if isinstance(params, dict) else {}
						for in_edge in incoming.get(nid, []):
							src = str(in_edge.get("source"))
							if node_kind.get(src) != "sample":
								continue
							src_samples = node_samples_map.get(src, {})
							if label in src_samples:
								sample_payload = dict(src_samples[label])
								break
						node_samples.append(sample_payload)
				else:
					node_samples = [dict(params)] if isinstance(params, dict) else []
					node_sample_labels = [""] if node_samples else []

			node_labels[nid] = list(node_sample_labels)
			node_samples_map[nid] = {
				label: dict(node_samples[idx])
				for idx, label in enumerate(node_sample_labels)
			}

			for i, sample in enumerate(node_samples):
				sample_label = node_sample_labels[i]
				node_instance = f"{name}_{sample_label}" if sample_label else name
				node_params = dict(_as_dict(node_params_defaults))
				resolved_inputs: Dict[str, Any] = {}
				input_validation_errors: List[str] = []

				for input_handle in inputs.keys():
					input_schema = _as_dict(inputs.get(input_handle))
					in_edge_match = next(
						(e for e in incoming[nid] if _edge_value(e, "targetHandle", "target_handle") == input_handle),
						None,
					)
					if in_edge_match:
						src = str(in_edge_match.get("source"))
						source_name = _node_name(node_map[src])
						source_handle = _edge_value(in_edge_match, "sourceHandle", "source_handle")

						resolved_value = None
						source_instance = f"{source_name}_{sample_label}" if sample_label else source_name
						resolved_value = output_cache.get((source_instance, source_handle, sample_label))
						if resolved_value is None:
							resolved_value = output_cache.get((source_name, source_handle, ""))

						resolved_value = _project_input_value_by_schema(resolved_value, input_schema)
						node_params[input_handle] = resolved_value
						resolved_inputs[input_handle] = resolved_value
						input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, resolved_value))
						continue

					direct_value = _sample_value(sample, input_handle)
					if direct_value is not None:
						direct_value = _project_input_value_by_schema(direct_value, input_schema)
						node_params[input_handle] = direct_value
						resolved_inputs[input_handle] = direct_value
						input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, direct_value))
						continue

					input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, None))

				node_resolved_outputs: Dict[str, Any] = {}
				has_input_errors = len(input_validation_errors) > 0
				for output_handle, output_cfg in outputs.items():
					output_value = None
					if not has_input_errors:
						output_value = node_params.get(output_handle)
					if not has_input_errors and isinstance(output_cfg, dict):
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
						"input_validation_errors": input_validation_errors,
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
				target_scatter_field = _scatter_field(node_map[target])
				target_raw_samples = params.get(target_scatter_field) if target_scatter_field else None
				target_labels: List[str] = []
				if isinstance(target_raw_samples, list):
					target_labels = [_sample_label(sample, i) for i, sample in enumerate(target_raw_samples) if isinstance(sample, dict)]

				current_labels = list(node_sample_labels) if node_sample_labels else [""]

				if target_kind == "sample":
					for src_label in current_labels:
						source_node_id = f"{name}_{src_label}" if src_label else name
						if target_scatter_field:
							candidate_target_labels = [src_label] if src_label and src_label in target_labels else target_labels
							for dst_label in candidate_target_labels:
								analysis_edges.append(
									{
										"analysis_id": analysis_id,
										"source_node": source_node_id,
										"target_node": f"{target_name}_{dst_label}",
										"source_handle": source_handle,
										"target_handle": target_handle,
									}
								)
						else:
							target_node_id = f"{target_name}_{src_label}" if src_label else target_name
							analysis_edges.append(
								{
									"analysis_id": analysis_id,
									"source_node": source_node_id,
									"target_node": target_node_id,
									"source_handle": source_handle,
									"target_handle": target_handle,
								}
							)
				else:
					for src_label in current_labels:
						source_node_id = f"{name}_{src_label}" if src_label else name
						analysis_edges.append(
							{
								"analysis_id": analysis_id,
								"source_node": source_node_id,
								"target_node": target_name,
								"source_handle": source_handle,
								"target_handle": target_handle,
							}
						)

		else:
			node_instance = name
			node_params = dict(_as_dict(node_params_defaults))
			resolved_inputs: Dict[str, Any] = {}
			input_validation_errors: List[str] = []

			for input_handle in inputs.keys():
				values: List[Any] = []
				input_schema = _as_dict(inputs.get(input_handle))
				for in_edge in incoming[nid]:
					if _edge_value(in_edge, "targetHandle", "target_handle") != input_handle:
						continue
					src = str(in_edge.get("source"))
					source_name = _node_name(node_map[src])
					source_kind = node_kind.get(src, "sample")
					source_handle = _edge_value(in_edge, "sourceHandle", "source_handle")

					if source_kind == "sample":
						source_labels = node_labels.get(src)
						if source_labels is None:
							source_labels = [""]
						for sample_label in source_labels:
							source_instance = f"{source_name}_{sample_label}" if sample_label else source_name
							values.append(output_cache.get((source_instance, source_handle, sample_label)))
					else:
						values.append(output_cache.get((source_name, source_handle, "aggregate")))

				values = [v for v in values if v is not None]
				input_cfg = _as_dict(inputs.get(input_handle))
				is_list = bool(input_cfg.get("multiple")) or len(values) > 1
				if is_list:
					node_params[input_handle] = values
					resolved_inputs[input_handle] = values
					input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, values))
				elif values:
					node_params[input_handle] = values[0]
					resolved_inputs[input_handle] = values[0]
					input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, values[0]))
				else:
					input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, None))

			node_resolved_outputs: Dict[str, Any] = {}
			has_input_errors = len(input_validation_errors) > 0
			for output_handle, output_cfg in outputs.items():
				output_value = None
				if not has_input_errors:
					output_value = node_params.get(output_handle)
				if not has_input_errors and isinstance(output_cfg, dict):
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
					"input_validation_errors": input_validation_errors,
					"executor": str(params.get("executor") or ""),
					"max_retry": int(node.get("max_retry") or 3),
				}
			)

	_decorate_runtime_graph(analysis_id, analysis_nodes, analysis_edges)

	return {
		"analysis_nodes": analysis_nodes,
		"analysis_edges": analysis_edges,
	}
