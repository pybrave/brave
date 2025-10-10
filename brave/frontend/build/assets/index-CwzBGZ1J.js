import{j as e,B as n}from"./main-gLMaKCvr.js";import{A as i}from"./index-DUqcjVqJ.js";import{T as r}from"./index-ZwmWfN3I.js";import"./index-Ci9o3BMm.js";import"./Table-CWRWFg95.js";import"./addEventListener-BwXlid1p.js";import"./Dropdown-CSp8FTqG.js";import"./index-B-_sZvQI.js";import"./index-Jdu54dr5.js";import"./index-DEhiFitC.js";import"./index-CjYZg4K2.js";import"./index-B__zS0KG.js";import"./index-BrNLqRge.js";import"./index-ByQpjXWK.js";import"./UpOutlined-CEatmWIN.js";import"./index-DDpcHwmR.js";import"./study-page-BLC-2qgz.js";import"./usePagination-DK-N3QaW.js";import"./index-Das8pPKs.js";import"./index-CWqFacgc.js";import"./callSuper-DlyBkZi7.js";import"./index-BpTPZbHm.js";import"./index-D1xRfB3g.js";import"./index-D2XNTdXQ.js";import"./DeleteOutlined-CBRh7405.js";import"./index-B6vjdRJB.js";import"./rgb-BwIoVOhg.js";import"./index-4ifBGcWk.js";const a=({record:o,plot:t})=>e.jsx(e.Fragment,{children:o&&e.jsxs(e.Fragment,{children:[e.jsx(n,{type:"primary",onClick:()=>{t({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:o.content.annotations,input_faa:o.content.input_faa},tableDesc:`
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

                    `})},children:" 查看注释结果"}),e.jsx(n,{type:"primary",onClick:()=>{t({saveAnalysisMethod:"eggnog_kegg_table",moduleName:"eggnog_kegg",params:{file_path:o.content.annotations},tableDesc:`
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),R=()=>e.jsxs(e.Fragment,{children:[e.jsx(r,{items:[{key:"eggnog",label:"eggnog",children:e.jsx(e.Fragment,{children:e.jsx(i,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:e.jsx(a,{})})})}]}),e.jsx("p",{})]});export{R as default};
