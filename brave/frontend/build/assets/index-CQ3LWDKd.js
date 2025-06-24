import{j as e,B as s,T as g,A as t}from"./index-s57B3ha7.js";const o=({record:n,plot:a})=>e.jsx(e.Fragment,{children:n&&e.jsxs(e.Fragment,{children:[e.jsx(s,{type:"primary",onClick:()=>{a({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:n.content.annotations,input_faa:n.content.input_faa},tableDesc:`
| 列                      | 含义                                 |
| ---------------------- | ---------------------------------- |
| #query                 | 查询序列的 ID                           |
| seed_eggNOG_ortholog | 种子同源物（最匹配的 EggNOG 同源群）             |
| seed_ortholog_evalue | 种子同源物的比对 E 值                       |
| seed_ortholog_score  | 比对分数                               |
| eggNOG_OGs            | 所属的 EggNOG 同源群（多个可能）               |
| max_annot_lvl        | 最大注释等级（例如 arCOG, COG, NOG 等）       |
| COG_category          | 功能分类（一个或多个字母，详见 EggNOG 分类）         |
| Preferred_name        | 推荐的基因名称                            |
| GOs                    | GO（Gene Ontology）注释                |
| EC                     | 酶编号（Enzyme Commission number）      |
| KEGG_ko               | KEGG 通路编号                          |
| KEGG_Pathway          | KEGG 所属路径                          |
| KEGG_Module           | KEGG 功能模块                          |
| KEGG_Reaction         | KEGG 化学反应编号                        |
| KEGG_rclass           | KEGG 反应类别                          |
| BRITE                  | KEGG BRITE 分类信息                    |
| KEGG_TC               | KEGG Transporter Classification 编号 |
| CAZy                   | 碳水化合物活性酶分类                         |
| BiGG_Reaction         | BiGG 化学反应编号                        |
| PFAMs                  | 蛋白结构域信息（来自 Pfam 数据库）               |

                    `})},children:" 查看注释结果"}),e.jsx(s,{type:"primary",onClick:()=>{a({saveAnalysisMethod:"eggnog_kegg_table",moduleName:"eggnog_kegg",params:{file_path:n.content.annotations},tableDesc:`
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),l=()=>e.jsxs(e.Fragment,{children:[e.jsx(g,{items:[{key:"eggnog",label:"eggnog",children:e.jsx(e.Fragment,{children:e.jsx(t,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:e.jsx(o,{})})})}]}),e.jsx("p",{})]});export{l as default};
