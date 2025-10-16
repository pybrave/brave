import{j as o,B as i}from"./main-qdx71IeZ.js";import{A as r}from"./index-CQxAdf1U.js";import{T as n}from"./index-CssIxjBA.js";import"./index-BEz9x6qu.js";import"./index-enAFolCN.js";import"./index-B59g6Chu.js";import"./index-DypQT-Hh.js";import"./UpOutlined-W4L3zuBA.js";import"./index-EOZAs8C8.js";import"./Table-BlsL6kCC.js";import"./addEventListener-gnMpRr3K.js";import"./Dropdown-DsoEvqJ1.js";import"./index-DzNw07ei.js";import"./index-Dg2XgaQy.js";import"./index-XxT13G35.js";import"./index-RAPlm8xH.js";import"./index-DnAAkqW2.js";import"./index-BTiKGIIu.js";import"./index-DcRhgt6q.js";import"./index-CmvvgrfA.js";import"./study-page-Do4EjIyk.js";import"./usePagination-B91F5N18.js";import"./RedoOutlined-CpHCHwbd.js";import"./index-C_udHuuV.js";import"./index-Bz6urQ5j.js";import"./callSuper-D6RVTDYQ.js";import"./DownloadOutlined-lpdqma_y.js";import"./index-DdILmJpV.js";import"./index-B_yuV5-A.js";import"./index-DyzH6iix.js";import"./DeleteOutlined-CuopAM2r.js";import"./index-C6EkMtQe.js";import"./rgb-BwIoVOhg.js";import"./index-BDkAZgMv.js";const a=({record:t,plot:e})=>o.jsx(o.Fragment,{children:t&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{e({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:t.content.annotations,input_faa:t.content.input_faa},tableDesc:`
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
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),z=()=>o.jsxs(o.Fragment,{children:[o.jsx(n,{items:[{key:"eggnog",label:"eggnog",children:o.jsx(o.Fragment,{children:o.jsx(r,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:o.jsx(a,{})})})}]}),o.jsx("p",{})]});export{z as default};
