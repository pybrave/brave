from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import Integer, String
from brave.api.config.db import meta
# from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import Text

samples = Table(
    "t_samples",
    meta,
    Column("id", Integer, primary_key=True),
    Column("project", String(255)),
    Column("sample_key", String(255)),
    Column("sample_name", String(255)),
    Column("sequencing_target", String(255)),
    Column("sequencing_technique", String(255)),
    Column("sample_composition", String(255)),
    Column("library_name", String(255)),
    Column("sample_group", String(255)),
    Column("sample_group_name", String(255)),
    Column("sample_source", String(255)),
    Column("host_disease", String(255)),
    Column("sample_individual", String(255)),
    Column("is_available", Integer),
    Column("fastq1", String(255)),
    Column("fastq2", String(255)),
)
analysis = Table(
    "nextflow",
    meta,
    Column("id", Integer, primary_key=True),
    Column("project", String(255)),
    Column("analysis_id", String(255)),
    Column("component_id", String(255)),
    Column("analysis_name", String(255)),
    Column("input_file", String(255)),
    Column("analysis_method", String(255)),
    Column("work_dir", String(255)),
    Column("params_path", String(255)),
    Column("command_path", String(255)),
    Column("request_param", Text),
    Column("output_format", Text),
    Column("output_dir", String(255)),
    Column("pipeline_script", String(255)),
    Column("parse_analysis_module", String(255)),
    Column("trace_file", String(255)),
    Column("workflow_log_file", String(255)),
    Column("executor_log_file", String(255)),
    Column("process_id", String(255)),
    Column("script_config_file", String(255))
)

analysis_result = Table(
    "analysis_result",
    meta,
    Column("id", Integer, primary_key=True),
    Column("sample_name", String(255)),
    Column("sample_key", String(255)),
    Column("analysis_name", String(255)),
    Column("analysis_key", String(255)),
    Column("analysis_method", String(255)),
    Column("software", String(255)),
    Column("content", String(255)),
    Column("analysis_version", String(255)),
    Column("content_type", String(255)),
    Column("analysis_id", String(255)),
    Column("project", String(255)),
    Column("request_param", String(255)),
    Column("analysis_type", String(255)),
    Column("create_date", String(255))
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

# pipeline_type: pipelne analysis_software analysis_file  downstream_analysis
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
    # Column("parent_pipeline_id", String(255)),
    Column("content", Text),
    Column("order_index", Integer)

)
# relation_type: pipeline_software software_input_file  software_ouput_file  file_downstream
t_pipeline_components_relation = Table(
    "pipeline_components_relation",
    meta,
    Column("relation_id", Integer, primary_key=True),
    Column("relation_type", String(255)), 
    Column("install_key", String(255)),
    # Column("pipeline_id", String(255)),
    Column("component_id", String(255)),
    Column("parent_component_id", String(255)),
    Column("order_index", Integer)

)


t_bio_database = Table(
    "bio_database",
    meta,
    Column("id", Integer, primary_key=True),
    Column("database_id", String(255)),
    Column("name", String(255)),
    Column("path", String(255)),
    Column("type", String(255))
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
# t_relation_file_downstream = Table(
#     "relation_file_downstream",
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

