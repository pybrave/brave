import os
from brave.api.enum.component_script import ScriptName
from brave.api.llm.schemas.llm import ChatRequest
from brave.api.schemas.chat_history import CreateChatHistory
from brave.api.service import analysis_service, chat_history_service
from brave.api.service import analysis_result_service
import brave.api.service.pipeline as  pipeline_service
from brave.api.config.db import get_engine
from_json_schema = """
- For example, if the tool is a "箱线图工具", the script from json schema could be:
{
  "formJson": [
    {
      "name": "input_file",
      "label": "Input Table",
      "component_id": "75087620-2ff8-4045-8694-a0c19aac12fc",
      "db": true,
      "group": "group_field",
      "type": "CollectedSampleSelect",
      "columns": [
        "x_var",
        "group1_vars",
        "group2_vars"
      ],
      "modes": [
        0,
        1,
        1
      ],
      "columns_rules": [
        1,
        1,
        1
      ],
      "rules": [
        {
          "required": true,
          "message": "This field cannot be empty!"
        }
      ]
    },
    {
      "name": "sig_mode",
      "label": "Significance calculation method",
      "type": "BaseSelect",
      "initialValue": "exist",
      "required": true,
      "rules": [
        {
          "required": true,
          "message": "Please select a significance calculation method"
        }
      ],
      "data": [
        {
          "label": "exist",
          "value": "exist"
        },
        {
          "label": "t-test",
          "value": "t-test"
        },
        {
          "label": "wilcox",
          "value": "wilcox"
        }
      ]
    },
    {
      "name": "qvalue_method",
      "label": "Qvalue adjust method",
      "type": "BaseSelect",
      "initialValue": "BH",
      "depends": {
        "or": [
          {
            "name": "sig_mode",
            "value": "t-test"
          },
          {
            "name": "sig_mode",
            "value": "wilcox"
          }
        ]
      },
      "data": [
        {
          "label": "none",
          "value": "none"
        },
        {
          "label": "BH",
          "value": "BH"
        },
        {
          "label": "bonferroni",
          "value": "bonferroni"
        },
        {
          "label": "holm",
          "value": "holm"
        },
        {
          "label": "BY",
          "value": "BY"
        }
      ]
    },
    {
      "name": "input_file",
      "label": "Input Table",
      "depends": [   
        {
          "name": "sig_mode",
          "value": "exist"
        }
      ],
      "component_id": "75087620-2ff8-4045-8694-a0c19aac12fc",
      "group": "group_field",
      "type": "CollectedColumnsSelect",
      "columns": [
        "p_col",
        "q_col"
      ],
      "modes": [
        0,
        0
      ],
      "columns_rules": [
        1,
        1
      ],
      "rules": [
        {
          "required": true,
          "message": "This field cannot be empty!"
        }
      ]
    },
   
    {
      "name": "plot_type",
      "label": "Plot Type",
      "type": "BaseSelect",
      "initialValue": "violin",
      "required": true,
      "rules": [
        {
          "required": true,
          "message": "Please select a plot type"
        }
      ],
      "data": [
        {
          "label": "Violin",
          "value": "violin"
        },
        {
          "label": "Scatter",
          "value": "scatter"
        },
        {
          "label": "Half Violin + Scatter (ggdist)",
          "value": "half_violin_scatter"
        },
        {
          "label": "Boxplot",
          "value": "boxplot"
        }
      ]
    },
    {
      "name": "panel_type",
      "label": "Panel Type",
      "type": "BaseSelect",
      "initialValue": "free_x",
      "required": true,
      "rules": [
        {
          "required": true,
          "message": "Please select a Panel type"
        }
      ],
      "data": [
        {
          "label": "free_x",
          "value": "free_x"
        },
        {
          "label": "split",
          "value": "split"
        },
        {
          "label": "none",
          "value": "none"
        }
      ]
    },
    {
      "name": "input_file",
      "label": "Input Table",
      "depends": {
        "or": [
          {
            "name": "panel_type",
            "value": "split"
          },
          {
            "name": "panel_type",
            "value": "free_x"
          }
        ]
      },
      "component_id": "75087620-2ff8-4045-8694-a0c19aac12fc",
      "group": "group_field",
      "type": "CollectedColumnsSelect",
      "columns": [
        "panel_var"
      ],
      "modes": [
        0
      ],
      "columns_rules": [
        1
      ],
      "rules": [
        {
          "required": true,
          "message": "This field cannot be empty!"
        }
      ]
    },
    {
      "type": "Divider",
      "text": "统计标注参数"
    },
    {
      "name": "show_stats",
      "label": "Show Statistical Labels",
      "type": "BaseSwitch",
      "initialValue": true
    },
    {
      "name": "stat_label",
      "label": "Statistical Label",
      "type": "BaseSelect",
      "initialValue": "p",
      "depends": [
        {
          "name": "show_stats",
          "value": true
        }
      ],
      "data": [
        {
          "label": "P value",
          "value": "p"
        },
        {
          "label": "Q value",
          "value": "q"
        },
        {
          "label": "Both P and Q",
          "value": "both"
        }
      ]
    },
    {
      "name": "stat_display",
      "label": "Stat Display",
      "type": "BaseSelect",
      "initialValue": "value",
      "depends": [
        {
          "name": "show_stats",
          "value": true
        }
      ],
      "data": [
        {
          "label": "p=XXX / q=XXX",
          "value": "value"
        },
        {
          "label": "Significance Stars",
          "value": "star"
        }
      ]
    },
    {
      "name": "stat_value_digits",
      "label": "Stat Decimal Places",
      "type": "BaseSelect",
      "initialValue": "3",
      "depends": [
        {
          "name": "show_stats",
          "value": true
        },
        {
          "name": "stat_display",
          "value": "value"
        }
      ],
      "data": [
        {
          "label": "none",
          "value": "none"
        },
        {
          "label": "0",
          "value": "0"
        },
        {
          "label": "1",
          "value": "1"
        },
        {
          "label": "2",
          "value": "2"
        },
        {
          "label": "3",
          "value": "3"
        },
        {
          "label": "4",
          "value": "4"
        },
        {
          "label": "5",
          "value": "5"
        },
        {
          "label": "6",
          "value": "6"
        },
        {
          "label": "7",
          "value": "7"
        },
        {
          "label": "8",
          "value": "8"
        }
      ]
    },
    {
      "name": "stat_position",
      "label": "Stat Position",
      "type": "BaseSelect",
      "initialValue": "group_top",
      "depends": [
        {
          "name": "show_stats",
          "value": true
        }
      ],
      "data": [
        {
          "label": "Each Group Top",
          "value": "group_top"
        },
        {
          "label": "Uniform Top",
          "value": "uniform_top"
        }
      ]
    },
    {
      "name": "stat_text_size",
      "label": "Stat Text Size",
      "type": "BaseInputNumber",
      "initialValue": 3,
      "depends": [
        {
          "name": "show_stats",
          "value": true
        }
      ],
      "col": 12
    },
    {
      "name": "stat_offset_ratio",
      "label": "Stat Y Offset Ratio",
      "type": "BaseInputNumber",
      "initialValue": 0,
      "depends": [
        {
          "name": "show_stats",
          "value": true
        }
      ],
      "col": 12
    },
    {
      "name": "stat_bold",
      "label": "Stat Bold",
      "type": "BaseSwitch",
      "initialValue": false,
      "depends": [
        {
          "name": "show_stats",
          "value": true
        }
      ]
    },
    {
      "type": "Divider",
      "text": "点与画布参数"
    },
    {
      "name": "point_size",
      "label": "Point Size",
      "type": "BaseInputNumber",
      "initialValue": 4,
      "col": 12
    },
    {
      "name": "plot_width",
      "label": "Plot Width",
      "type": "BaseInputNumber",
      "depends": {
        "or": [
          {
            "name": "panel_type",
            "value": "none"
          },
          {
            "name": "panel_type",
            "value": "free_x"
          }
        ]
      },
      "initialValue": 12,
      "col": 12
    },
    {
      "name": "plot_height",
      "label": "Plot Height",
      "type": "BaseInputNumber",
      "initialValue": 7,
      "depends": [
        {
          "name": "panel_type",
          "value": "split"
        }
      ],
      "col": 12
    },
    {
      "name": "split_width_min",
      "label": "Split Min Width",
      "type": "BaseInputNumber",
      "initialValue": 6,
      "depends": [
        {
          "name": "panel_type",
          "value": "split"
        }
      ],
      "col": 12
    },
    {
      "name": "split_width_max",
      "label": "Split Max Width",
      "type": "BaseInputNumber",
      "initialValue": 12,
      "depends": [
        {
          "name": "panel_type",
          "value": "split"
        }
      ],
      "col": 12
    },
    {
      "name": "split_width_base",
      "label": "Split Width Base",
      "type": "BaseInputNumber",
      "initialValue": 0,
      "depends": [
        {
          "name": "panel_type",
          "value": "split"
        }
      ],
      "col": 12
    },
    {
      "name": "split_width_step",
      "label": "Split Width Step Per Feature",
      "type": "BaseInputNumber",
      "initialValue": 0,
      "depends": [
        {
          "name": "panel_type",
          "value": "split"
        }
      ],
      "col": 12
    },
    {
      "type": "Divider",
      "text": "坐标轴样式"
    },
    {
      "name": "x_text_angle",
      "label": "X Axis Text Angle",
      "type": "BaseInputNumber",
      "initialValue": 45,
      "col": 12
    },
    {
      "name": "point_alpha",
      "label": "Point Alpha",
      "type": "BaseInputNumber",
      "initialValue": 0.7,
      "col": 12
    },
    {
      "name": "axis_text_size",
      "label": "Axis Text Size",
      "type": "BaseInputNumber",
      "initialValue": 10,
      "col": 12
    },
    {
      "name": "axis_title_size",
      "label": "Axis Title Size",
      "type": "BaseInputNumber",
      "initialValue": 12,
      "col": 12
    },
    {
      "type": "Divider",
      "text": "图例参数"
    },
    {
      "name": "legend_text_size",
      "label": "Legend Text Size",
      "type": "BaseInputNumber",
      "initialValue": 9,
      "col": 12
    },
    {
      "name": "legend_title_size",
      "label": "Legend Title Size",
      "type": "BaseInputNumber",
      "initialValue": 10,
      "col": 12
    },
    {
      "name": "legend_title_text",
      "label": "Legend Title Text",
      "type": "BaseInput",
      "initialValue": "Group"
    },
    {
      "name": "legend_group1_text",
      "label": "Legend Group1 Text",
      "type": "BaseInput",
      "required": true,
      "col": 12,
      "initialValue": "group1"
    },
    {
      "name": "legend_group2_text",
      "label": "Legend Group2 Text",
      "type": "BaseInput",
      "required": true,
      "col": 12,
      "initialValue": "group2"
    },
    {
      "name": "legend_other_text",
      "label": "Legend Other Text",
      "type": "BaseInput",
      "initialValue": "other"
    },
    
    {
      "name": "group1_color",
      "label": "Group1 Color",
      "required": true,
      "type": "BaseColorPicker",
      "col": 12
    },
    {
      "name": "group2_color",
      "label": "Group2 Color",
      "required": true,
      "type": "BaseColorPicker",
      "col": 12
    },
    {
      "type": "Divider",
      "text": "坐标标签与变换"
    },
    {
      "name": "x_label",
      "label": "X label",
      "type": "BaseInput"
    },
    {
      "name": "y_label",
      "label": "Y label",
      "type": "BaseInput"
    },
    {
      "name": "y_transform",
      "label": "Y Axis Transform",
      "type": "BaseSelect",
      "initialValue": "none",
      "data": [
        {
          "label": "None",
          "value": "none"
        },
        {
          "label": "Log10",
          "value": "log10"
        },
        {
          "label": "Log2",
          "value": "log2"
        },
        {
          "label": "Natural Log",
          "value": "ln"
        }
      ]
    },
    {
      "name": "y_axis_digits",
      "label": "Y Axis Decimal Places",
      "type": "BaseSelect",
      "initialValue": "none",
      "data": [
        {
          "label": "none",
          "value": "none"
        },
        {
          "label": "2",
          "value": "2"
        }
      ]
    },
    {
      "name": "y_log_offset",
      "label": "Y Log Offset",
      "type": "BaseInputNumber",
      "initialValue": 1e-06,
      "depends": {
        "or": [
          {
            "name": "y_transform",
            "value": "log10"
          },
          {
            "name": "y_transform",
            "value": "log2"
          },
          {
            "name": "y_transform",
            "value": "ln"
          }
        ]
      },
      "col": 12
    },
    {
      "type": "Divider",
      "text": "标题与图例位置"
    },
    {
      "name": "title",
      "label": "Plot Title",
      "type": "BaseInput"
    },
    {
      "name": "title_size",
      "label": "Title Size",
      "type": "BaseInputNumber",
      "initialValue": 14,
      "col": 12
    },
    {
      "name": "title_position",
      "label": "Title Position",
      "type": "BaseSelect",
      "initialValue": "left",
      "data": [
        {
          "label": "Left",
          "value": "left"
        },
        {
          "label": "Center",
          "value": "center"
        },
        {
          "label": "Right",
          "value": "right"
        }
      ]
    },
    {
      "name": "legend_position",
      "label": "Legend Position",
      "type": "BaseSelect",
      "initialValue": "top",
      "data": [
        {
          "label": "Top",
          "value": "top"
        },
        {
          "label": "Bottom",
          "value": "bottom"
        },
        {
          "label": "Left",
          "value": "left"
        },
        {
          "label": "Right",
          "value": "right"
        },
        {
          "label": "Hide",
          "value": "none"
        }
      ]
    },
    {
      "type": "Divider",
      "text": "输出参数"
    },
    {
      "name": "output_name",
      "label": "Output File Name",
      "type": "BaseInput",
      "initialValue": "boxplot",
      "rules": [
        {
          "required": true,
          "message": "Output file name is required"
        }
      ]
    },{
        "name":"x_feature",
        "label":"Delete x feature",
        "type":"BaseTextAreaNum",
        "required":"true",
        "initialValue":""
    }
  ]
}

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schemas/form.schema.json",
  "title": "Pipeline Form Config Schema",
  "type": "object",
  "required": ["formJson"],
  "properties": {
    "formJson": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "label", "type"],
        "properties": {
          "name": { "type": "string", "minLength": 1 },
          "label": { "type": "string", "minLength": 1 },
          "type": {
            "type": "string",
            "enum": [
              "GroupFieldSelect",
              "CollectedSampleSelect",
              "BaseSelect",
              "BaseSwitch",
              "BaseInput",
              "BaseInputNumber",
              "BaseTextAreaNum",
              "Input"
            ]
          },
          "component_id": { "type": "string" },
          "db": { "type": "boolean" },
          "group": { "type": "string" },
          "col": { "type": "integer", "minimum": 1, "maximum": 24 },
          "required": { "type": "boolean" },
          "initialValue": {},
          "columns": {
            "type": "array",
            "items": { "type": "string" }
          },
          "modes": {
            "type": "array",
            "items": { "type": "integer", "enum": [0, 1] }
          },
          "columns_rules": {
            "type": "array",
            "items": { "type": "integer", "enum": [0, 1] }
          },
          "depends": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "value"],
              "properties": {
                "name": { "type": "string" },
                "value": {}
              },
              "additionalProperties": false
            }
          },
          "rules": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "required": { "type": "boolean" },
                "message": { "type": "string" }
              },
              "additionalProperties": true
            }
          },
          "data": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["label", "value"],
              "properties": {
                "label": { "type": "string" },
                "value": {}
              },
              "additionalProperties": true
            }
          }
        },
        "additionalProperties": true
      }
    }
  },
  "additionalProperties": false
}
"""

script_example = """
- script form json example, 注意 name 是 input_file, 
- 生成的`params.json` 的文件路径就是 params$input_file$content
{
  "formJson": [
    {
      "name": "input_file",
      "label": "Input Table",
      "component_id": "75087620-2ff8-4045-8694-a0c19aac12fc",
      "db": true,
      "group": "group_field",
      "type": "CollectedSampleSelect",
      "columns": [
        "x_var",
        "group1_vars",
        "group2_vars"
      ],
      "modes": [
        0,
        1,
        1
      ],
      "columns_rules": [
        1,
        1,
        1
      ],
      "rules": [
        {
          "required": true,
          "message": "This field cannot be empty!"
        }
      ]
    }
  ]
}


根据上述form json生成的`params.json`的内容如下：

{
  "input_file": {
    "id": 7000,
    "analysis_result_id": "117658b5-c836-4f84-804e-d815a4d52845",
    "sample_id": null,
    "file_name": "KO基因_CM_SM",
    "component_id": "75087620-2ff8-4045-8694-a0c19aac12fc",
    "file_type": "collected",
    "content": "/opt/brave_prod/workspace/analysis/3ab6cf0a-d53d-4637-a039-ea347e0d435f/99ffdb15-fa10-4a31-a12f-34e8d7656789/b12aac19-4dab-4504-ac09-dd9bfe0b38b6/output/KO基因_CM_SM.tsv",
    "file": 7000,
    "x_var": {
      "id": 7000,
      "sample_name": "Row.names",
      "analysis_result_id": "117658b5-c836-4f84-804e-d815a4d52845",
      "columns_name": "Row.names"
    },
    "group1_vars": [
      {
        "id": 7000,
        "sample_name": "cm135",
        "analysis_result_id": "117658b5-c836-4f84-804e-d815a4d52845",
        "columns_name": "cm135"
      },
      {
        "id": 7000,
        "sample_name": "cm172",
        "analysis_result_id": "117658b5-c836-4f84-804e-d815a4d52845",
        "columns_name": "cm172"
      }
     
    ],
    "group2_vars": [
      {
        "id": 7000,
        "sample_name": "Sm170",
        "analysis_result_id": "117658b5-c836-4f84-804e-d815a4d52845",
        "columns_name": "Sm170"
      },
      {
        "id": 7000,
        "sample_name": "sm162",
        "analysis_result_id": "117658b5-c836-4f84-804e-d815a4d52845",
        "columns_name": "sm162"
      }
    ],
    "p_col": {
      "id": 7000,
      "sample_name": "P_value",
      "analysis_result_id": "117658b5-c836-4f84-804e-d815a4d52845",
      "columns_name": "P_value"
    },
    "form_type": "CollectedSampleSelect",
    "groups": [
      "x_var",
      "group1_vars",
      "group2_vars",
      "p_col",
      "q_col",
      "panel_var"
    ]
  }
}

R脚本是根据form json 生成的`params.json`中的内容来读取输入文件的，示例如下：

library(tidyverse)
## 输入文件从`"params.json`中读取，文件路径在`input_file`字段中
params <- jsonlite::fromJSON("params.json", simplifyVector = FALSE)
file_path <- params$input_file$content
df <- readr::read_tsv(file_path, show_col_types = FALSE)



## 输出tsv或png需要写入当前目录下的outpot文件夹，输出文件名可以使用具体图片名称或者使用`output_name`字段指定的文件名
long_tsv_path <- file.path("output", "boxplot_long.tsv")
readr::write_tsv(long_df, long_tsv_path)
message(sprintf("Long table saved to: %s", long_tsv_path))

pdf(file = str_glue("output/heatmap.pdf") , width =heatmap_width,height =heatmap_height, family = "Arial")
pheatmap(
  corr_matrix ,
  display_numbers = sig_matrix,
  color = colorRampPalette(c("#9BBBE1", "#FFFFFF", "#F09BA0"))(100),
)
dev.off()

ggsave(filename = "output/boxplot_plot.png", plot = panel_plot, width = panel_plot_width, height = plot_height, dpi = 300)

"""

async def build_prompt(req: ChatRequest, system_prompt: str, template: str,queue) -> str:
    async def emit(msg):
        if queue:
            await queue.put(msg)
    biz_id = req.biz_id
    biz_type= req.biz_type
    project_id= req.project_id
    context =""
    code =""
    data =""
    with get_engine().begin() as conn:
        if biz_type=="tools":
            find_relation = pipeline_service.find_relation_component_prompt_by_id(conn, biz_id)
            if find_relation:
                tool_name = find_relation["name"]
                await emit({"title":f"Fetch Tool Info","content":f"Fetching tool {tool_name} information..."})
                if find_relation["prompt"]:
                    context = find_relation["prompt"]
                if find_relation["content"]:
                    from_prompt = """
                    The following is a JSON form used when inputting scripts.
                    """
                    data = from_prompt+"\n"+find_relation["content"]
                
                component_script = pipeline_service.find_component_module(find_relation,ScriptName.main)['path']
                if os.path.exists(component_script):
                    with open(component_script, "r") as f:
                        code = f.read()
                    await emit({"title":f"Fetch Tool Script","content":f"Fetching tool {tool_name} script..."})

        elif biz_type=="script":
            component = pipeline_service.find_component_by_id(conn, biz_id)
            if component:
                if component["prompt"]:
                    context = component["prompt"]
                if component["content"]:
                    from_prompt = """
                    The following is a JSON form used when inputting scripts.
                    """
                    data = from_prompt+"\n"+component["content"]
                
                component_script = pipeline_service.find_component_module(component,ScriptName.main)['path']
                if os.path.exists(component_script):
                    with open(component_script, "r") as f:
                        code = f.read()
        elif biz_type =="file":
            component = pipeline_service.find_component_by_id(conn, biz_id)
            # find_result = analysis_result_service.find_component_and_analysis_result_by_analysis_result_id(conn, biz_id)
            if component:

                # file_type = component["file_type"]
                # file_content = component["content"]
                prompt = component["prompt"]
                if prompt:
                    context = prompt
                content = component["content"]
                if content:
                    data = content
        elif biz_type =="analysis_result":
            find_result = analysis_result_service.find_component_and_analysis_result_by_analysis_result_id(conn, biz_id)
            if find_result:
                
                file_type = find_result["file_type"]
                file_content = find_result["content"]
                component_prompt = find_result["component_prompt"]
                if component_prompt:
                    context = component_prompt

                if file_type =="collected" and os.path.exists(file_content):
                    with open(file_content, "r") as f:
                        data = "".join([line for _, line in zip(range(100), f)])
                else:
                    data = file_content
                    


        elif biz_type =="analysis":
            find_analysis = analysis_service.find_analysis_and_component_by_id(conn, biz_id)
            if  find_analysis:
                analysis_name = find_analysis["analysis_name"]
                await emit({"title":f"Fetch Analysis Info","content":f"Fetching analysis {analysis_name} information..."})
                # raise HTTPException(status_code=404, detail="Analysis not found")
                output_dir = find_analysis["output_dir"]
                prompt = f"{output_dir}/output/prompt.ai"
                if find_analysis["relation_prompt"]:
                    context = find_analysis["relation_prompt"]
                if os.path.exists(prompt):
                    prompt0 = "The analysis results are as follows:\n"
                    with open(prompt, "r") as f:
                        data =  prompt0 + f.read()
                    await emit({"title":f"Fetch Analysis Prompt","content":f"Read {analysis_name} prompt.ai file..."})
                if find_analysis["pipeline_script"]:
                    component_script = find_analysis["pipeline_script"]
                    if os.path.exists(component_script):
                        with open(component_script, "r") as f:
                            code = f.read()
                        await emit({"title":f"Fetch Analysis Script","content":f"Fetching analysis {analysis_name} script..."})

        
        content = template.format(context=context,
                                code=code,
                                script_example=script_example,
                                from_json_schema=from_json_schema,
                                data=data)
        create_chatHistory = CreateChatHistory(
                user_id=None,
                session_id=None,
                biz_id=biz_id,
                biz_type=biz_type,
                role="user",
                content=req.message,
                project_id=project_id,
            )
            # system_prompt=system_prompt,
            # user_prompt=content,
        if req.is_save_prompt:
            create_chatHistory.system_prompt=content
            # create_chatHistory.user_prompt=content
        chat_history_service.insert_chat_history(conn, create_chatHistory)
    return content