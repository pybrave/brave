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
    Column("analysis_key", String(255)),
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
    Column("parse_analysis_module", String(255))
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
    Column("analysis_id", Integer),
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
# meta.create_all(engine)