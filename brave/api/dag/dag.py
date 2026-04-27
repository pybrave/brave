
from collections import defaultdict
import json
from typing import Any, Dict, List, Tuple
import uuid
import re

# 本文件负责把前端 DAG 定义 + 运行参数，展开为可调度的 runtime 节点与边：
# 1) 节点分类（sample / aggregate）
# 2) 按 sample 维度实例化节点
# 3) 计算输入、预填输出、构建边映射
# 4) 生成 analysis_nodes / analysis_edges 入库结构


def _as_dict(value: Any) -> Dict[str, Any]:
	"""确保值为 dict，统一处理 None / 非 dict 场景。"""
	if isinstance(value, dict):
		return value
	return {}


def _node_key(node: Dict[str, Any]) -> str:
	"""返回 DAG 节点唯一键（优先 id，回退 name）。"""
	return str(node.get("id") or node.get("name") or "")


def _node_name(node: Dict[str, Any]) -> str:
	"""返回节点展示名，用于 runtime node_id 的前缀。"""
	return str(node.get("name") or node.get("id") or "node")


def _node_id_base(node: Dict[str, Any]) -> str:
	"""返回用于 node_id 的基名：将空白字符规范化为下划线。"""
	return re.sub(r"\s+", "_", _node_name(node).strip())


def _build_node_id(node_id_base: str, sample_label: str = "") -> str:
	"""统一生成 runtime node_id。"""
	if sample_label:
		sample_label = re.sub(r"\s+", "_", sample_label.strip())
	return f"{node_id_base}_{sample_label}" if sample_label else node_id_base


def _script_id(node: Dict[str, Any]) -> str:
	"""返回脚本标识，用于运行时和默认参数匹配。"""
	return str(node.get("script_id") or node.get("name") or node.get("id") or "")


def _sample_label(sample: Dict[str, Any], index: int) -> str:
	"""为 sample 生成稳定标签（例如 S1/S2），用于 sample 节点实例命名。"""
	node_name = None
	file_name = None
	if sample.get("node_name"):
		node_name = sample.get("node_name")
	if  sample.get("file_name"):
		file_name = sample.get("file_name")
	if node_name and file_name:
		return f"{node_name} ({file_name}) ({index + 1})".strip()
	elif file_name:
		return f"{file_name} ({index + 1})".strip()
	elif node_name:
		return f"{node_name} ({index + 1})".strip()
	else:
		analysis_result_id = sample.get("analysis_result_id")
		return f"{analysis_result_id} ({index + 1})".strip()
	
	
	# file_name = str(sample.get("file_name") or ).strip()
	# if file_name:
	# 	return f"{file_name}_{index + 1}"
		# if "_" in file_name:
		# 	token = file_name.split("_")[-1].strip()
		# 	if token:
		# 		return token.upper()
		# if file_name[-1:].isdigit():
		# 	digits = ""
		# 	for ch in reversed(file_name):
		# 		if ch.isdigit():
		# 			digits = ch + digits
		# 		else:
		# 			break
		# 	if digits:
		# 		return f"S{digits}"

	analysis_result_id = 	sample.get("analysis_result_id")
	# return f"{analysis_result_id} ({index + 1})"


def _sample_value(sample: Dict[str, Any], handle: str) -> Any:
	"""从 sample 数据中按 handle 取值，支持弱规范化键名匹配。"""
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


def _sample_extra_meta(sample: Dict[str, Any], input_handles: List[str]) -> Dict[str, Any]:
	"""提取 sample 中未被输入句柄消费的字段，用于 resolved_inputs.meta。"""
	def _norm_key(key: str) -> str:
		return re.sub(r"[^a-z0-9]", "", key.lower())

	consumed_norm_keys = {_norm_key(handle) for handle in input_handles}
	extra: Dict[str, Any] = {}
	for key, value in sample.items():
		if value is None:
			continue
		if _norm_key(str(key)) in consumed_norm_keys:
			continue
		extra[str(key)] = value
	return extra


def _schema_type(schema: Dict[str, Any]) -> str:
	"""读取 schema 的 type 字段并标准化。"""
	return str(schema.get("type") or "").strip().lower()


def _scatter_field(node: Dict[str, Any]) -> str:
	"""解析节点 scatter 配置，仅支持 mode=each。"""
	scatter = _as_dict(node.get("scatter"))
	if str(scatter.get("mode") or "").strip().lower() != "each":
		return ""
	return str(scatter.get("field") or "").strip()


def _gather_field(node: Dict[str, Any]) -> str:
	"""解析节点 gather 配置，仅支持 mode=list。"""
	gather = _as_dict(node.get("gather"))
	if str(gather.get("mode") or "").strip().lower() != "list":
		return ""
	return str(gather.get("field") or "").strip()


def _derive_upstream_sample_labels(
	nid: str,
	incoming: Dict[str, List[Dict[str, Any]]],
	node_kind: Dict[str, str],
	node_labels: Dict[str, List[str]],
) -> List[str]:
	"""推导当前节点应实例化的 sample 标签集合。

	策略：优先取所有 sample 上游标签交集；若交集为空，回退并集。
	"""
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
	"""提取 object schema 内标记 required=true 的属性名。"""
	return [
		str(name)
		for name, cfg in _as_dict(schema.get("properties")).items()
		if bool(_as_dict(cfg).get("required"))
	]


def _collect_required_input_errors(input_handle: str, input_schema: Dict[str, Any], value: Any) -> List[str]:
	"""基于 schema 校验 required 输入，返回错误列表。"""
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
	"""按输入 schema 投影字段，避免把无关字段注入 params/resolved_inputs。"""
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
	"""兼容 camelCase/snake_case 两种 edge 字段风格。"""
	return str(edge.get(camel) or edge.get(snake) or "")


def _render_output_pattern(pattern: str, sample: Dict[str, Any], sample_label: str) -> str:
	"""渲染输出路径模板中的 {sample}。"""
	sample_name = str(sample.get("file_name") or sample.get("sample_id") or sample_label)
	return pattern.replace("{sample}", sample_name)


def _build_node_name(name: str, sample_label: str) -> str:
	"""构建节点展示名，格式为 #name:sample_label。"""
	# sym_value = str(sym or "node")
	label_value = str(sample_label or "merged")
	return f"{label_value} ({name})"


def _topology(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[str]:
	"""返回拓扑顺序；若图中存在环，则回退原始节点顺序。"""
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
	"""将节点分类为 sample / singleton / aggregate。

	规则摘要：
	- 配置 gather(mode=list) 的节点 -> aggregate
	- 配置 scatter(mode=each) 的节点 -> sample
	- 其余节点若依赖 sample 上游 -> sample
	- 否则视为 singleton（单例配置节点）
	"""
	node_map = {_node_key(n): n for n in nodes}
	incoming = defaultdict(list)
	for edge in edges:
		incoming[str(edge.get("target") or "")].append(edge)

	order = _topology(nodes, edges)
	kind: Dict[str, str] = {}
	for nid in order:
		node = node_map[nid]
		if _gather_field(node):
			kind[nid] = "aggregate"
			continue
		if _scatter_field(node):
			kind[nid] = "sample"
			continue

		has_sample_upstream = any(
			kind.get(str(edge.get("source") or "")) == "sample"
			for edge in incoming.get(nid, [])
		)
		kind[nid] = "sample" if has_sample_upstream else "singleton"
	return kind


def _decorate_runtime_graph(analysis_id: str, analysis_nodes: List[Dict[str, Any]], analysis_edges: List[Dict[str, Any]]) -> None:
	"""补齐入库前 runtime 字段：
	- 为边规范化 handle 字段命名
	- 为节点补 analysis_id、analysis_node_id、默认状态
	- 计算 upstream_ids/downstream_ids
	"""
	upstream = defaultdict(set)
	downstream = defaultdict(set)

	for idx, edge in enumerate(analysis_edges):
		# 每条边写回 analysis 归属和稳定主键。
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
		# 节点入库前统一补默认字段，避免后续调度判断缺字段。
		node_id = str(node.get("node_id") or "")
		node["analysis_id"] = analysis_id
		node["analysis_node_id"] = node.get("analysis_node_id") or str(uuid.uuid4())

		for key, value in now_defaults.items():
			if node.get(key) is None:
				node[key] = value

		node["upstream_ids"] = sorted(list(upstream.get(node_id, set())))
		node["downstream_ids"] = sorted(list(downstream.get(node_id, set())))


def build_runtime_tasks(analysis_id: str, params: Dict[str, Any], dag_definition: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
	"""将 DAG 定义展开成 runtime 节点/边。

	核心阶段：
	1) 拓扑排序 + 节点分类
	2) sample 节点按样本实例化，aggregate 节点按汇总实例化
	3) 解析输入、预渲染输出、构建输出缓存
	4) 生成边并做最终图装饰
	"""
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
		node_id_base = _node_id_base(node)
		script_id = _script_id(node)
		node_params_defaults = _as_dict(params.get("node_params")).get(script_id)
		if node_params_defaults is None:
			node_params_defaults = _as_dict(params.get("node_params")).get(name)
		if node_params_defaults is None:
			node_params_defaults = _as_dict(node.get("params"))

		inputs = _as_dict(node.get("inputs"))
		outputs = _as_dict(node.get("outputs"))

		if node_kind.get(nid) == "sample":
			# sample 节点：一份样本对应一个 runtime 节点实例（例如 fastp_S1）。
			scatter_field = _scatter_field(node)
			node_samples: List[Dict[str, Any]] = []
			node_sample_labels: List[str] = []

			if scatter_field:
				# 显式 scatter：直接按 params[scatter_field] 展开。
				raw_samples = params.get(scatter_field)
				if not isinstance(raw_samples, list):
					return {
						"analysis_nodes": [],
						"analysis_edges": [],
					}
				node_samples = [dict(item) for item in raw_samples if isinstance(item, dict)]
				node_sample_labels = [_sample_label(sample, i) for i, sample in enumerate(node_samples)]
			else:
				# 非显式 scatter：优先继承 sample 上游标签，保证样本链路连续。
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
					# node_sample_labels is params.analysis_name or [""]
					node_sample_labels = [params.get("analysis_name", "")] if node_samples else []

			node_labels[nid] = list(node_sample_labels)
			node_samples_map[nid] = {
				label: dict(node_samples[idx])
				for idx, label in enumerate(node_sample_labels)
			}

			for i, sample in enumerate(node_samples):
				sample_label = node_sample_labels[i]
				node_instance = _build_node_id(node_id_base, sample_label)
				node_name = _build_node_name(name, sample_label)
				
				node_params = dict(_as_dict(node_params_defaults))
				resolved_inputs: Dict[str, Any] = {}
				input_validation_errors: List[str] = []

				for input_handle in inputs.keys():
					# 优先从入边上游输出缓存取值；取不到时回退到样本直传值。
					input_schema = _as_dict(inputs.get(input_handle))
					in_edge_match = next(
						(e for e in incoming[nid] if _edge_value(e, "targetHandle", "target_handle") == input_handle),
						None,
					)
					if in_edge_match:
						src = str(in_edge_match.get("source"))
						source_id_base = _node_id_base(node_map[src])
						source_handle = _edge_value(in_edge_match, "sourceHandle", "source_handle")

						resolved_value = None
						source_instance = _build_node_id(source_id_base, sample_label)
						resolved_value = output_cache.get((source_instance, source_handle, sample_label))
						if resolved_value is None:
							resolved_value = output_cache.get((source_id_base, source_handle, ""))
						if resolved_value is None:
							resolved_value = output_cache.get((source_id_base, source_handle, "aggregate"))

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
					else:
						io_type = input_schema.get("type")
						if io_type and io_type=="CollectedSampleSelect":
							node_params[input_handle] = sample
							resolved_inputs[input_handle] = sample
							continue


					input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, None))

				
				extra_meta = _sample_extra_meta(sample, list(inputs.keys()))
				if extra_meta and "meta" not in resolved_inputs:
					resolved_inputs["meta"] = extra_meta

				node_resolved_outputs: Dict[str, Any] = {}
				has_input_errors = len(input_validation_errors) > 0
				for output_handle, output_cfg in outputs.items():
					# 输入有错误时输出保持 None，避免错误数据继续传播。
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
						"node_name": node_name,
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
				# 展开 sample 出边：
				# - 目标是 sample 节点时，按 label 对齐连边
				# - 目标是 aggregate 节点时，所有 sample 实例汇聚到目标节点
				target = str(e.get("target"))
				target_id_base = _node_id_base(node_map[target])
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
						source_node_id = _build_node_id(node_id_base, src_label)
						if target_scatter_field:
							candidate_target_labels = [src_label] if src_label and src_label in target_labels else target_labels
							for dst_label in candidate_target_labels:
								analysis_edges.append(
									{
										"analysis_id": analysis_id,
										"source_node": source_node_id,
										"target_node": _build_node_id(target_id_base, dst_label),
										"source_handle": source_handle,
										"target_handle": target_handle,
									}
								)
						else:
							target_node_id = _build_node_id(target_id_base, src_label)
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
						source_node_id = _build_node_id(node_id_base, src_label)
						analysis_edges.append(
							{
								"analysis_id": analysis_id,
								"source_node": source_node_id,
								"target_node": target_id_base,
								"source_handle": source_handle,
								"target_handle": target_handle,
							}
						)

		else:
			# singleton / aggregate 节点：只生成一个实例。
			is_aggregate = node_kind.get(nid) == "aggregate"
			node_instance = _build_node_id(node_id_base)
			instance_label = "merged" if is_aggregate else str(params.get("analysis_name") or "")
			node_name = _build_node_name(name, instance_label)
			node_params = dict(_as_dict(node_params_defaults))
			gather_field = _gather_field(node)
			resolved_inputs: Dict[str, Any] = {}
			input_validation_errors: List[str] = []

			for input_handle in inputs.keys():
				# 收集所有匹配入边值；multiple 或多值时按 list 写入。
				values: List[Any] = []
				input_schema = _as_dict(inputs.get(input_handle))
				for in_edge in incoming[nid]:
					if _edge_value(in_edge, "targetHandle", "target_handle") != input_handle:
						continue
					src = str(in_edge.get("source"))
					source_id_base = _node_id_base(node_map[src])
					source_kind = node_kind.get(src, "sample")
					source_handle = _edge_value(in_edge, "sourceHandle", "source_handle")

					if source_kind == "sample":
						source_labels = node_labels.get(src)
						if source_labels is None:
							source_labels = [""]
						for sample_label in source_labels:
							source_instance = _build_node_id(source_id_base, sample_label)
							values.append(output_cache.get((source_instance, source_handle, sample_label)))
					elif source_kind == "singleton":
						values.append(output_cache.get((source_id_base, source_handle, "")))
					else:
						values.append(output_cache.get((source_id_base, source_handle, "aggregate")))

				values = [v for v in values if v is not None]
				is_list = is_aggregate and bool(gather_field) and input_handle == gather_field
				if is_list:
					node_params[input_handle] = values
					resolved_inputs[input_handle] = values
					input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, values))
				elif values:
					node_params[input_handle] = values[0]
					resolved_inputs[input_handle] = values[0]
					input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, values[0]))
				else:
					direct_value = params.get(input_handle) if isinstance(params, dict) else None
					if direct_value is not None:
						direct_value = _project_input_value_by_schema(direct_value, input_schema)
						node_params[input_handle] = direct_value
						resolved_inputs[input_handle] = direct_value
						input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, direct_value))
					else:
						input_validation_errors.extend(_collect_required_input_errors(input_handle, input_schema, None))

			node_resolved_outputs: Dict[str, Any] = {}
			has_input_errors = len(input_validation_errors) > 0
			for output_handle, output_cfg in outputs.items():
				# aggregate 输出中的 {sample} 固定渲染为 merged；singleton 使用分析名渲染。
				output_value = None
				if not has_input_errors:
					output_value = node_params.get(output_handle)
				if not has_input_errors and isinstance(output_cfg, dict):
					pattern = output_cfg.get("pattern")
					if isinstance(pattern, str) and pattern:
						if is_aggregate:
							output_value = pattern.replace("{sample}", "merged")
						else:
							output_value = _render_output_pattern(pattern, params, instance_label)
				node_resolved_outputs[output_handle] = output_value
				cache_scope = "aggregate" if is_aggregate else ""
				output_cache[(node_instance, output_handle, cache_scope)] = output_value

			analysis_nodes.append(
				{
					"analysis_id": analysis_id,
					"node_id": node_instance,
					"node_name": node_name,
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
				# singleton/aggregate 出边：
				# - 指向 sample 节点时，复制到目标的每个 sample 实例
				# - 指向非 sample 节点时，保持单条边
				target = str(e.get("target"))
				target_id_base = _node_id_base(node_map[target])
				target_kind = node_kind.get(target, "sample")
				source_handle = _edge_value(e, "sourceHandle", "source_handle")
				target_handle = _edge_value(e, "targetHandle", "target_handle")
				target_scatter_field = _scatter_field(node_map[target])
				target_raw_samples = params.get(target_scatter_field) if target_scatter_field else None

				if target_kind == "sample":
					if isinstance(target_raw_samples, list):
						target_labels = [
							_sample_label(sample, i)
							for i, sample in enumerate(target_raw_samples)
							if isinstance(sample, dict)
						]
					else:
						target_labels = _derive_upstream_sample_labels(target, incoming, node_kind, node_labels)

					for dst_label in target_labels:
						analysis_edges.append(
							{
								"analysis_id": analysis_id,
								"source_node": node_instance,
								"target_node": _build_node_id(target_id_base, dst_label),
								"source_handle": source_handle,
								"target_handle": target_handle,
							}
						)
				else:
					analysis_edges.append(
						{
							"analysis_id": analysis_id,
							"source_node": node_instance,
							"target_node": target_id_base,
							"source_handle": source_handle,
							"target_handle": target_handle,
						}
					)

	_decorate_runtime_graph(analysis_id, analysis_nodes, analysis_edges)

	return {
		"analysis_nodes": analysis_nodes,
		"analysis_edges": analysis_edges,
	}
