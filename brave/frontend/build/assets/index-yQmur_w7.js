import{j as o,B as i}from"./main-BwXC3IR-.js";import{A as r}from"./index-CA0cMVlS.js";import{T as n}from"./index-Ds-Cm03P.js";import"./index-C4BvvLXY.js";import"./index-DMfVbt3c.js";import"./index-CBMb1kgU.js";import"./index-CotDIsNu.js";import"./UpOutlined-BKYGFLNT.js";import"./index-8j16o04L.js";import"./index--JnjVdx_.js";import"./Table-iOXYhvzQ.js";import"./addEventListener-VtdiWBGV.js";import"./Dropdown-CtfTgCmR.js";import"./index-49RMhiY3.js";import"./react-window-CXMGAHD3.js";import"./index-BMDk0JWr.js";import"./DeleteOutlined-OZ71hyZZ.js";import"./RedoOutlined-E9lihzWT.js";import"./index-D2PUnlUD.js";import"./index-f7yPm_mY.js";import"./index-gdPfdXVC.js";import"./index-CAfjAvfF.js";import"./index-BPZgQyLF.js";import"./index-DxWRZDVa.js";import"./index-CZtBSYBQ.js";import"./study-page-C1kz4qO_.js";import"./usePagination-DDagBvBR.js";import"./index-cs3Gd2d7.js";import"./callSuper-C57L85fm.js";import"./DownloadOutlined-CPXLD1k8.js";import"./index-uUHnTTZD.js";import"./index-CaTpPA5T.js";import"./index-CtsN54S7.js";import"./index-G5d2OwBp.js";import"./rgb-BwIoVOhg.js";import"./index-Cw1XXBNm.js";const m=({record:t,plot:e})=>o.jsx(o.Fragment,{children:t&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{e({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:t.content.annotations,input_faa:t.content.input_faa},tableDesc:`
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

                    `})},children:" 查看注释结果"}),o.jsx(i,{type:"primary",onClick:()=>{e({saveAnalysisMethod:"eggnog_kegg_table",moduleName:"eggnog_kegg",params:{file_path:t.content.annotations},tableDesc:`
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),Z=()=>o.jsxs(o.Fragment,{children:[o.jsx(n,{items:[{key:"eggnog",label:"eggnog",children:o.jsx(o.Fragment,{children:o.jsx(r,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:o.jsx(m,{})})})}]}),o.jsx("p",{})]});export{Z as default};
