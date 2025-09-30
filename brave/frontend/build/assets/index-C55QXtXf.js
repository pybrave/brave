import{j as e,B as n}from"./main-DWRmJItp.js";import{A as a}from"./index-DjwZXGu8.js";import{T as i}from"./index-BL5qaRD0.js";import"./index-ByZxpDTB.js";import"./Table-CorKTwZX.js";import"./addEventListener-BBJtVQmZ.js";import"./Dropdown-CRhi--nO.js";import"./index-CRfZL3ek.js";import"./index-CIC2lPJU.js";import"./index-Boe5_PAQ.js";import"./index-CELUfxGL.js";import"./index-CD0H_sEz.js";import"./index-BEHP9AIO.js";import"./index-buf9Du1j.js";import"./UpOutlined-B9ArEpXu.js";import"./index-C6NESaM6.js";import"./index-CJtHLx1t.js";import"./callSuper-Cn0arcAG.js";import"./index-Br9XgThS.js";import"./index-ChbX2kGi.js";import"./index-B1xgCqcU.js";import"./usePagination-BbrBuRX4.js";import"./DeleteOutlined-CQr_HvF4.js";import"./index-vrokRTY_.js";import"./rgb-BwIoVOhg.js";import"./index-CSPO6T1X.js";const r=({record:o,plot:t})=>e.jsx(e.Fragment,{children:o&&e.jsxs(e.Fragment,{children:[e.jsx(n,{type:"primary",onClick:()=>{t({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:o.content.annotations,input_faa:o.content.input_faa},tableDesc:`
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
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),M=()=>e.jsxs(e.Fragment,{children:[e.jsx(i,{items:[{key:"eggnog",label:"eggnog",children:e.jsx(e.Fragment,{children:e.jsx(a,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:e.jsx(r,{})})})}]}),e.jsx("p",{})]});export{M as default};
