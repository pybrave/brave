params 示例：
```json
{
  "inputs": [
    {
      "sample_id": "61a0c60e-a5a3-4e2b-8783-181d4b5cec89",
      "file_name": "test_s2",
      "r1": "/data/wangyang/NGS_TEST/test-data/test_s2_1.fastq.gz",
      "r2": "/data/wangyang/NGS_TEST/test-data/test_s2_2.fastq.gz","-"
    },
    {
      "sample_id": "7470f852-f80f-4585-8fb9-7a0c1b89a4dd",
      "file_name": "test_s1",
      "r1": "/data/wangyang/NGS_TEST/test-data/test_s1_1.fastq.gz",
      "r2": "/data/wangyang/NGS_TEST/test-data/test_s1_2.fastq.gz",
   
    }
  ]
}
```

dag_definition 示例：
```json
{
    "nodes": [
        {
            "name": "joint_calling",
            "id": "e3d00582-2a99-4b02-a687-65e556f7aefa",
            "inputs": {
                "bam": {
                    "type": "file",
                    "multiple": false,
                    "required": true
                }
            },
            "outputs": {
                "vcf": {
                    "type": "file",
                    "pattern": "{sample}_trimmed.fastq.gz"
                }
            },
            "color": "lime",
            "icon": "scissors",
            "script_id": "e3d00582-2a99-4b02-a687-65e556f7aefa",
            "position": {
                "x": 446.067415730337,
                "y": 68.53932584269663
            }
        },
        {
            "name": "bwa",
            "id": "cbd1a1cc-ca62-46da-8713-b0e868a2d44f",
            "inputs": {
                "r1": {
                    "type": "file",
                    "multiple": false,
                    "required": true
                },
                "r2": {
                    "type": "file",
                    "multiple": false,
                    "required": true
                }
            },
            "outputs": {
                "bam": {
                    "type": "file",
                    "pattern": "{sample}_trimmed.fastq.gz"
                }
            },
            "color": "green",
            "icon": "scissors",
            "script_id": "cbd1a1cc-ca62-46da-8713-b0e868a2d44f",
            "position": {
                "x": 244.943820224719,
                "y": 60.11235955056175
            }
        },
        {
            "name": "fastp",
            "id": "759d6899-e632-400f-9b11-6a8b7b6e2042",
            "inputs": {
                "r1": {
                    "type": "file",
                    "multiple": false,
                    "required": true
                },
                "r2": {
                    "type": "file",
                    "multiple": false,
                    "required": true
                }
            },
            "outputs": {
                "r1": {
                    "type": "file",
                    "multiple": false,
                    "required": true
                },
                "r2": {
                    "type": "file",
                    "multiple": false,
                    "required": true
                }
            },
            "color": "magenta",
            "icon": "scissors",
            "script_id": "759d6899-e632-400f-9b11-6a8b7b6e2042",
            "position": {
                "x": 8.988764044944006,
                "y": 97.19101123595505
            }
        }
    ],
    "edges": [
        {
            "source": "759d6899-e632-400f-9b11-6a8b7b6e2042",
            "sourceHandle": "r1",
            "target": "cbd1a1cc-ca62-46da-8713-b0e868a2d44f",
            "targetHandle": "r1",
            "id": "xy-edge__759d6899-e632-400f-9b11-6a8b7b6e2042r1-cbd1a1cc-ca62-46da-8713-b0e868a2d44fr1"
        },
        {
            "source": "759d6899-e632-400f-9b11-6a8b7b6e2042",
            "sourceHandle": "r2",
            "target": "cbd1a1cc-ca62-46da-8713-b0e868a2d44f",
            "targetHandle": "r2",
            "id": "xy-edge__759d6899-e632-400f-9b11-6a8b7b6e2042r2-cbd1a1cc-ca62-46da-8713-b0e868a2d44fr2"
        },
        {
            "source": "cbd1a1cc-ca62-46da-8713-b0e868a2d44f",
            "sourceHandle": "bam",
            "target": "e3d00582-2a99-4b02-a687-65e556f7aefa",
            "targetHandle": "bam",
            "id": "xy-edge__cbd1a1cc-ca62-46da-8713-b0e868a2d44fbam-e3d00582-2a99-4b02-a687-65e556f7aefabam"
        }
    ]
}
```
analsyis_node:
```
[
  {
    "analysis_id": "pipe_100",
    "node_id": "fastp_S1",
    "script_id": "fastp",
    "params": {
      "threads": 4,
      "r1": "/data/wangyang/NGS_TEST/test-data/test_s1_1.fastq.gz",
      "r2": "/data/wangyang/NGS_TEST/test-data/test_s1_2.fastq.gz"
    }
  },
  {
    "analysis_id": "pipe_100",
    "node_id": "fastp_S2",
    "script_id": "fastp",
    "params": {
      "threads": 4,
      "r1": "/data/wangyang/NGS_TEST/test-data/test_s2_1.fastq.gz",
      "r2": null
    }
  },
  {
    "analysis_id": "pipe_100",
    "node_id": "bwa_S1",
    "script_id": "bwa",
    "params": {
      "threads": 8,
      "r1": "/data/wangyang/NGS_TEST/test-data/test_s1_1.fastq.gz",
      "r2": "/data/wangyang/NGS_TEST/test-data/test_s1_2.fastq.gz"
    }
  },
  {
    "analysis_id": "pipe_100",
    "node_id": "bwa_S2",
    "script_id": "bwa",
    "params": {
      "threads": 8,
      "r1": "/data/wangyang/NGS_TEST/test-data/test_s2_1.fastq.gz",
      "r2": null
    }
  },
  {
    "analysis_id": "pipe_100",
    "node_id": "joint_calling",
    "script_id": "joint_calling",
    "params": {
      "method": "haplotypecaller",
      "bam_list": [
        "/data/wangyang/NGS_TEST/test-data/test_s1_1.bam",
        "/data/wangyang/NGS_TEST/test-data/test_s2_1.bam"
      ]
    }
  }
]
```
analsyis_edge
```
[
  {
    "analysis_id": "pipe_100",
    "source_node": "fastp_S1",
    "target_node": "bwa_S1",
    "sourceHandle": "r1",
    "targetHandle": "r1"
  },
  {
    "analysis_id": "pipe_100",
    "source_node": "fastp_S1",
    "target_node": "bwa_S1",
    "sourceHandle": "r2",
    "targetHandle": "r2"
  },
  {
    "analysis_id": "pipe_100",
    "source_node": "fastp_S2",
    "target_node": "bwa_S2",
    "sourceHandle": "r1",
    "targetHandle": "r1"
  },
  {
    "analysis_id": "pipe_100",
    "source_node": "fastp_S2",
    "target_node": "bwa_S2",
    "sourceHandle": "r2",
    "targetHandle": "r2"
  },
  {
    "analysis_id": "pipe_100",
    "source_node": "bwa_S1",
    "target_node": "joint_calling",
    "sourceHandle": "bam",
    "targetHandle": "bam_list"
  },
  {
    "analysis_id": "pipe_100",
    "source_node": "bwa_S2",
    "target_node": "joint_calling",
    "sourceHandle": "bam",
    "targetHandle": "bam_list"
  }
]
```