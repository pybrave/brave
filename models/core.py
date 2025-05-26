from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine

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
    Column("request_param", String(255)),
    Column("output_dir", String(255))
)

meta.create_all(engine)