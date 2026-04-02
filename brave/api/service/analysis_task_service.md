params 示例：
```json
{
  "reads": [
    {
      "sample_id": "61a0c60e-a5a3-4e2b-8783-181d4b5cec89",
      "file_name": "test_s2",
      "fastq1": "/data/wangyang/NGS_TEST/test-data/test_s2_1.fastq.gz",
      "fastq2": "/data/wangyang/NGS_TEST/test-data/test_s2_2.fastq.gz","-"
    },
    {
      "sample_id": "7470f852-f80f-4585-8fb9-7a0c1b89a4dd",
      "file_name": "test_s1",
      "fastq1": "/data/wangyang/NGS_TEST/test-data/test_s1_1.fastq.gz",
      "fastq2": "/data/wangyang/NGS_TEST/test-data/test_s1_2.fastq.gz",
   
    }
  ]
}
```

dag_definition 示例：
```json
{
  "pipeline_id": "rna_seq_01",
  "name": "RNA-seq Alignment Pipeline",
  "nodes": [
    {
      "id": "n1",
      "script_name": "fastqc",
      "script_id": "cbd1a1cc-ca62-46da-8713-b0e868a2d44f",
      "params": {
        "threads": 4,
        "input_r1": "{r1}",
        "input_r2": "{r2}"
      },
      "position": {
        "x": 120,
        "y": 240
      }
    },
    {
      "id": "n2",
      "script_name": "bwa_align",
      "script_id": "7d005aeb-0c7f-44a4-89cf-3ccaaf58316b",
      "parents": [
        "n1"
      ],
      "params": {
        "threads": 8
      },
      "position": {
        "x": 380,
        "y": 240
      }
    },
    {
      "id": "n3",
      "script_id": "joint_calling",
      "params": {},
      "parents": [
        "n2"
      ],
      "sample_aware": false
    }
  ]
}
```

run-time tasks:
```
task_id
sample_id
analysis_id
task_name
node_id
parents
```