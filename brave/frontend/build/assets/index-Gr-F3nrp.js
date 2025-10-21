import{j as o,B as i}from"./main-B2jPVJuc.js";import{A as r}from"./index-gjkdKVOt.js";import{T as n}from"./index-bd5EV77p.js";import"./index-CL1TtC2i.js";import"./index-D5lQbqN-.js";import"./index-ROS2ditM.js";import"./index-umuRLg26.js";import"./UpOutlined-BLGU6aq-.js";import"./DeleteOutlined-7aDqphvw.js";import"./index-D94Q12AR.js";import"./index-01a6DBbv.js";import"./Table-D1zuQkUf.js";import"./addEventListener-BtkycpkD.js";import"./Dropdown-DxVuU2Kw.js";import"./index-IGtn9UM1.js";import"./react-window-DDxMxsOy.js";import"./index-DI5YvQtd.js";import"./RedoOutlined-B2jLc-U5.js";import"./index-BJqJD7sV.js";import"./index-Dc0kVygC.js";import"./index-CFkosLO7.js";import"./index-CwSQOIN4.js";import"./index-JnpnusFw.js";import"./index-Bi5GN48q.js";import"./index-CVH_8gwK.js";import"./study-page-BuxTE7mG.js";import"./usePagination-BFzen1kl.js";import"./index-CjBmKVj7.js";import"./index-Dusr40e4.js";import"./index-ClcbhDbg.js";import"./callSuper--xQhnHMR.js";import"./index-CVcxCOCs.js";import"./index-Ctd2Wq2c.js";import"./rgb-BwIoVOhg.js";import"./index-De5gFR_d.js";const a=({record:t,plot:e})=>o.jsx(o.Fragment,{children:t&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{e({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:t.content.annotations,input_faa:t.content.input_faa},tableDesc:`
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
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),S=()=>o.jsxs(o.Fragment,{children:[o.jsx(n,{items:[{key:"eggnog",label:"eggnog",children:o.jsx(o.Fragment,{children:o.jsx(r,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:o.jsx(a,{})})})}]}),o.jsx("p",{})]});export{S as default};
