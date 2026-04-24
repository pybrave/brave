from datetime import datetime
from sqlalchemy import Column, DateTime, Table
from sqlalchemy.sql.sqltypes import Integer, String,Boolean
from brave.api.config.db import meta
# from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import Text,Index,JSON
from sqlalchemy.dialects.mysql import LONGTEXT


t_project = Table(
    "t_project",
    meta,
    Column("id", Integer, primary_key=True),
    Column("project_id", String(255)),
    Column("project_name", String(255)),
    Column("metadata_form", Text),
    Column("research", Text().with_variant(LONGTEXT(), "mysql")),
    Column("parameter", Text().with_variant(LONGTEXT(), "mysql")),
    Column("description", Text().with_variant(LONGTEXT(), "mysql"))
)

samples = Table(
    "t_samples",
    meta,
    Column("id", Integer, primary_key=True),
    Column("sample_id", String(255)),
    Column("project", String(255)),
    # Column("sample_key", String(255)),
    # Column("analysis_key", String(255), unique=True),
    Column("sample_name", String(255)),
    # Column("sequencing_target", String(255)),
    # Column("sequencing_technique", String(255)),
    # Column("sample_composition", String(255)),
    # Column("library_name", String(255)),
    Column("sample_group", String(255)),
    # Column("sample_group_name", String(255)),
    # Column("sample_source", String(255)),
    # Column("host_disease", String(255)),
    # Column("sample_individual", String(255)),
    # Column("is_available", Integer),
    # Column("fastq1", String(255)),
    # Column("fastq2", String(255)),
    Column("metadata", Text)
)
analysis = Table(
    "nextflow",
    meta,
    Column("id", Integer, primary_key=True),
    Column("project", String(255)),
    Column("analysis_id", String(255)),
    Column("component_id", String(255)),
    Column("relation_id", String(255)),  # relation_pipeline_components id
    Column("analysis_name", String(255)),
    Column("input_file", String(255)),
    Column("analysis_method", String(255)),
    Column("work_dir", String(255)),
    Column("params_path", String(255)),
    Column("command_path", String(255)),
    Column("request_param", Text().with_variant(LONGTEXT(), "mysql")),
    Column("output_format", Text().with_variant(LONGTEXT(), "mysql")),
    Column("output_dir", String(255)),
    Column("pipeline_script", String(255)),
    Column("parse_analysis_module", String(255)),
    Column("trace_file", String(255)),
    Column("workflow_log_file", String(255)),
    Column("executor_log_file", String(255)),
    Column("process_id", String(255)),
    Column("script_config_file", String(255)),
    # Column("analysis_status", String(255)),
    Column("job_id", String(255)),
    Column("ports", String(255)),
    Column("url", String(255)),
    # Column("run_type", String(255)),
    # Column("job_id", String(255)),
    # Column("server_id", String(255)),
    Column("job_status", String(255)),
    Column("server_status", String(255)),
    # Column("tools_status", String(255)),


    Column("command_log_path", String(255)),
    Column("is_report", Boolean, default=False),
    Column("is_cache", Boolean, default=False),
    Column("used", Boolean, default=True),
    # Column("container_id", String(255)),
    # Column("sub_container_id", String(255)),
    Column("data_component_ids",Text),
    Column("extra_project_ids",Text().with_variant(LONGTEXT(), "mysql")),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, onupdate=datetime.now)
)


analyis_task = Table(
    "analysis_task",
    meta,
    Column("task_id", String(255)),
    Column("sample_id", String(255)),
    Column("analysis_id", String(255)),
    Column("task_name", String(255)),
    Column("node_id", String(255)),
    Column("parents", JSON),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, onupdate=datetime.now)
    # Column("task_type", String(255)),
    # Column("request_param", Text().with_variant(LONGTEXT(), "mysql")),
    # Column("status", String(255)),
    # Column("result_path", String(255)),
    # Column("error_message", Text().with_variant(LONGTEXT(), "mysql")),

)

analysis_nodes = Table(
    "analysis_nodes",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),

    # 基本信息
    Column("analysis_node_id", String(255)),   # 当前节点实例 ID (UUID)
    Column("analysis_id", String(255)),        # 整个 DAG 实例 ID
    Column("node_id", String(255)),            # DAG 定义中的节点 ID
    Column("node_name", String(255)),
    Column("sample_id", String(255)),
    Column("script_id", String(255)),

    # 输入输出
    Column("inputs_patterns", JSON),
    Column("resolved_inputs", JSON),
    Column("output_patterns", JSON),
    Column("resolved_outputs", JSON),

    # 参数
    Column("params", JSON),

    # 资源＆执行状态
    Column("cpu", Integer),
    Column("memory", String(64)),
    Column("disk", String(64)),
    Column("gpu", Integer),

    Column("status", String(64)),       # pending/running/done/failed/cached
    Column("server_status", String(64)),
    Column("pid", Integer),
    Column("job_id", String(255)),
    Column("executor", String(64)),

    # 调度相关
    Column("retry", Integer, default=0),
    Column("max_retry", Integer, default=3),
    Column("exit_code", Integer),
    Column("error_message", Text),

    # 缓存
    Column("input_hash", String(255)),
    Column("cache_hit", Boolean),

    # DAG 关系
    Column("upstream_ids", JSON),       # list
    Column("downstream_ids", JSON),
    Column("input_validation_errors", JSON),
    Column("output_validation_errors", JSON),

    # 日志与目录
    Column("log_path", String(255)),
    Column("workspace_dir", String(255)),
    Column("output_dir", String(255)),
    Column("command_path", String(255)),
    Column("params_path", String(255)),

    # 时间
    Column("started_at", DateTime),
    Column("finished_at", DateTime),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, onupdate=datetime.now),
)
# analysis_nodes = Table(
#     "analysis_nodes",
#     meta,
#     Column("id", Integer, primary_key=True, autoincrement=True),
#     Column("analysis_node_id", String(255)),
#     Column("analysis_id", String(255)),
#     Column("node_id", String(255)),
#     Column("script_id", String(255)),
#     Column("input_files", JSON),
#     Column("output_files", JSON),
#     Column("log_path", String(255)),
#     Column("workspace_dir", String(255)),
#     Column("status", String(255)),
#     Column("sample_id", String(255)),
#     Column("command_path", String(255)),
#     Column("params", JSON),
#     Column("created_at", DateTime, default=datetime.now),
#     Column("updated_at", DateTime, onupdate=datetime.now)
# )


analysis_edges = Table(
    "analysis_edges",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("analysis_edge_id", String(255)),
    Column("analysis_id", String(255)),
    Column("source_node", String(255)),
    Column("target_node", String(255)),
    Column("source_handle", String(255)),
    Column("target_handle", String(255)),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, onupdate=datetime.now)
)

Index("idx_analysis_nodes_analysis_id", analysis_nodes.c.analysis_id)
Index("idx_analysis_nodes_analysis_id_status", analysis_nodes.c.analysis_id, analysis_nodes.c.status)
Index("idx_analysis_nodes_analysis_id_node_id", analysis_nodes.c.analysis_id, analysis_nodes.c.node_id)

Index("idx_analysis_edges_analysis_id", analysis_edges.c.analysis_id)
Index("idx_analysis_edges_analysis_id_source", analysis_edges.c.analysis_id, analysis_edges.c.source_node)
Index("idx_analysis_edges_analysis_id_target", analysis_edges.c.analysis_id, analysis_edges.c.target_node)

analysis_result = Table(
    "analysis_result",
    meta,
    Column("id", Integer, primary_key=True),
    Column("analysis_result_id", String(255)),
    Column("sample_id", String(255)),
    Column("sample_source", String(255)),


    # Column("sample_name", String(255)),
    # Column("sample_key", String(255)),
    # Column("analysis_name", String(255)),
    Column("file_name", String(255)),
    Column("analysis_key", String(255)),
    Column("component_id", String(255)),
    Column("type", String(255)),  # 'folder','file'
    Column("parent_id", String(255)),
    # Column("analysis_method", String(255)),
    Column("software", String(255)),
    Column("content",Text().with_variant(LONGTEXT(), "mysql")),
    Column("analysis_version", String(255)),
    Column("content_type", String(255)),
    Column("analysis_id", String(255)),
    Column("project", String(255)),
    Column("request_param", String(255)),
    Column("analysis_type", String(255)),
    Column("create_date", String(255)),
    Column("analysis_result_hash", String(255))
)

literature = Table(
    "literature",
    meta,
    Column("id", Integer, primary_key=True),
    Column("literature_key", String(255)),
    Column("literature_type", String(255)),
    Column("title", String(255)),
    Column("url", String(255)),
    Column("content", Text),
    Column("translate", Text),
    Column("interpretation", Text),
    Column("img", Text),
    Column("journal", String(255)),
    Column("publish_date", String(255)),
    Column("keywords", String(255))

)


relation_literature = Table(
    "relation_literature",
    meta,
    Column("relation_id", Integer, primary_key=True),
    Column("literature_key", String(255)),
    Column("obj_key", String(255)),
    Column("obj_type", String(255))
)

# pipeline_type: pipelne analysis_software analysis_file  script_analysis
# 

# Workflow
#    |
#    |  (多个)
#    v
# WorkflowPipelineRelation  <-- ordered DAG / parallel execution
#    |
#    |  (1 对 1)
#    v
# Pipeline
#    |
#    +--> InputFiles / OutputFiles / Downstream
# pipeline,software,file,downstream
t_pipeline_components = Table(
    "pipeline_components",
    meta,
    Column("id", Integer, primary_key=True),
    Column("component_id", String(255)),
    Column("install_key", String(255)),
    Column("component_type", String(255)), 
    Column("component_name", String(255)), 
    Column("description", Text().with_variant(LONGTEXT(), "mysql")), 
    Column("component_ids",Text().with_variant(LONGTEXT(), "mysql")),
    Column("img", String(255)), 
    Column("container_id", String(255)),
    Column("tools_container_id", Text),
    Column("prompt",Text().with_variant(LONGTEXT(), "mysql")),
    Column("io_schema",Text().with_variant(LONGTEXT(), "mysql")),


    Column("sub_container_id", String(255)),
    Column("tags", String(255)), 
    Column("file_type", String(255)), 
    Column("script_type", String(255)), 
    Column("category", String(255), default="default"), 
    # Column("namespace", String(255)),
    Column("content", Text),
    Column("order_index", Integer),
    Column("position", Text),
    Column("edges", Text)

)
# relation_type: pipeline_software software_input_file  software_ouput_file  file_script
t_pipeline_components_relation = Table(
    "pipeline_components_relation",
    meta,
    Column("id", Integer, primary_key=True),
    Column("name", String(255)),
    Column("img", String(255)), 
    Column("tags", JSON), 
    Column("category", String(255), default="default"), 
    Column("description", Text().with_variant(LONGTEXT(), "mysql")),
    Column("prompt",Text().with_variant(LONGTEXT(), "mysql")),
    Column("dag_definition",Text().with_variant(LONGTEXT(), "mysql")),


    Column("relation_id", String(255)),
    Column("relation_type", String(255)), 
    Column("install_key", String(255)),
    # Column("pipeline_id", String(255)),
    Column("component_id", String(255)),
    Column("parent_component_id", String(255)),
    Column("input_component_ids",  JSON),
    Column("output_component_ids",  JSON),
    Column("order_index", Integer),
    # Column("namespace", String(255)),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, onupdate=datetime.now)

)

t_pipeline_components_edges = Table(
    "pipeline_components_edges",
    meta,
    Column("id", Integer, primary_key=True),
    Column("edge_id", String(255)),
    Column("source", String(255)),
    Column("sourceHandle", String(255)),
    Column("target", String(255)),
    Column("targetHandle", String(255)),
    Column("pipeline_id", String(255))
)

t_bio_database = Table(
    "bio_database",
    meta,
    Column("id", Integer, primary_key=True),
    Column("database_id", String(255)),
    Column("name", String(255)),
    Column("path", String(255)),
    Column("type", String(255)),
    Column("db_index", String(255))
)

t_namespace = Table(
    "t_namespace",
    meta,
    Column("id", Integer, primary_key=True),
    Column("namespace_id", String(255)),
    Column("name", String(255)),
    Column("volumes", Text().with_variant(LONGTEXT(), "mysql")),
    Column("resources", Text().with_variant(LONGTEXT(), "mysql")),
    Column("queue_size", Integer, default=10),
    Column("is_use",  Boolean, default=False),
)

# t_relation_pipeline_software = Table(
#     "relation_pipeline_software",
#     meta,
#     Column("relation_id", Integer, primary_key=True),
#     Column("pipeline_id", String(255)),
#     Column("analysis_software_id", String(255))
# )

# t_analysis_software = Table(
#     "analysis_software",
#     meta,
#     Column("id", Integer, primary_key=True),
#     Column("analysis_software_id", String(255)),
#     Column("content", Text)

# )
# t_relation_software_file = Table(
#     "relation_software_file",
#     meta,
#     Column("relation_id", Integer, primary_key=True),
#     Column("analysis_software_id", String(255)),
#     Column("analysis_file_id", String(255)),
#     Column("file_type", String(255)),
#     Column("content", Text)
# )


# t_analysis_file = Table(
#     "analysis_file",
#     meta,
#     Column("id", Integer, primary_key=True),
#     Column("analysis_file_id", String(255))

# )
# t_relation_file_script = Table(
#     "relation_file_script",
#     mata,
#     Column("relation_id", Integer, primary_key=True),
#     Column("analysis_file_id", String(255)),
#     Column("downstream_analysis_id", String(255))
# )
# t_downstream_analysis = Table(
#     "downstream_analysis",
#     meta,
#     Column("id", Integer, primary_key=True),
#     Column("downstream_analysis_id", String(255))
# )
# # meta.create_all(engine)



# t_application = Table(
#     "application",
#     meta,
#     Column("id", Integer, primary_key=True),
#     Column("application_id", String(255)),
#     Column("name", String(255)),
#     Column("image", String(255)),
#     Column("description", String(255)),
#     Column("created_at", DateTime, default=datetime.now),
#     Column("updated_at", DateTime, onupdate=datetime.now)
# )

t_container = Table(
    "container",
    meta,
    Column("id", Integer, primary_key=True),
    Column("container_id", String(255)),
    Column("container_key", String(255)),
    Column("name", String(255)),
    Column("image", String(255)),
    Column("img",  Text().with_variant(LONGTEXT(), "mysql")),
    Column("image_id", String(255)),
    Column("image_status", String(255)),
    Column("description", String(255)),
    Column("version", String(255)),
    # Column("namespace", String(255)),
    Column("envionment", String(255)),
    Column("command", String(255)),
    Column("port", String(255)),
    Column("labels", Text().with_variant(LONGTEXT(), "mysql")),
    Column("change_uid", Boolean, default=True),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, onupdate=datetime.now)
)


t_chat_history = Table(
    "chat_history",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String(255)),
    Column("session_id", String(255)),
    Column("chat_history_id", String(255)),
    Column("project_id", String(255)),
    Column("biz_type", String(255)),
    Column("biz_id", String(255)),
    Column("thought_chain", JSON),
    Column("role", String(16)),   # "user" / "assistant"
    Column("content", Text().with_variant(LONGTEXT(), "mysql")),
    Column("system_prompt", Text().with_variant(LONGTEXT(), "mysql")),
    Column("user_prompt", Text().with_variant(LONGTEXT(), "mysql")),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, onupdate=datetime.now)
)


t_store = Table(
    "store",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("store_id", String(255)),
    Column("name", String(255)),
    Column("url", String(255)),
    Column("status", String(255)),
    # Column("progress", Integer),
    Column("log", Text().with_variant(LONGTEXT(), "mysql")),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, onupdate=datetime.now)
)