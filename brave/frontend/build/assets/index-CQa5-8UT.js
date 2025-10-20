import{j as o,B as i}from"./main-yPEfeT9f.js";import{A as r}from"./index-sNq0N1W8.js";import{T as n}from"./index-DWk5UzQP.js";import"./index-DpHfJKKa.js";import"./index-Bv2V4S_7.js";import"./index-CmYnMcha.js";import"./index-BN-A2AYH.js";import"./UpOutlined-BA6uNDge.js";import"./index-g3jGqZdZ.js";import"./index-DiBhs9OC.js";import"./Table-Ds-W4yE8.js";import"./addEventListener-xfTcUeJ_.js";import"./Dropdown-BbP99v9L.js";import"./index-6fbrPPXM.js";import"./react-window-CojtseHm.js";import"./index-DElqJASa.js";import"./index-BeIbeBzw.js";import"./DeleteOutlined-B-ExLEZC.js";import"./RedoOutlined-BC_aoZT6.js";import"./index-BoCvVzuf.js";import"./index-Bn_YYxlm.js";import"./index-BIvf0VpP.js";import"./index-CMCEc2V-.js";import"./index-BXBq3fyt.js";import"./index-Dh2aMPgI.js";import"./index-9ZzH-Rp_.js";import"./study-page-jQMWkMjr.js";import"./usePagination-DJtil0aa.js";import"./index-DFr1daPH.js";import"./callSuper-BnfznbVJ.js";import"./index-Dg2bbVCS.js";import"./index-BsvGrDsX.js";import"./index-Bnp4yvjP.js";import"./index-D-OxY-SA.js";import"./rgb-BwIoVOhg.js";import"./index-DR0jqTUB.js";const m=({record:t,plot:e})=>o.jsx(o.Fragment,{children:t&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{e({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:t.content.annotations,input_faa:t.content.input_faa},tableDesc:`
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
