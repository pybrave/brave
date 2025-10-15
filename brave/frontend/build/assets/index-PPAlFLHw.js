import{j as o,B as i}from"./main-DXywrSBF.js";import{A as n}from"./index-DN1I0-xZ.js";import{T as r}from"./index-qwSUrHIR.js";import"./index-BUctlgPj.js";import"./index-DjoHMCCX.js";import"./index-C4p1iVpj.js";import"./index-K-Wj2x7K.js";import"./UpOutlined-7MciF88_.js";import"./index-BwawJwES.js";import"./Table-DFI76zEx.js";import"./addEventListener-DnTxgold.js";import"./Dropdown-CgdcCv_B.js";import"./index-CWc1_CU5.js";import"./index-Bs08SC_0.js";import"./index-D7hxl_LK.js";import"./index-CqFY2fF-.js";import"./index-DKfe01fJ.js";import"./index-Bc2PCwt1.js";import"./index-BT58XBAc.js";import"./index-gpGOOqTj.js";import"./study-page-BYtG-saP.js";import"./usePagination-D0YIndB3.js";import"./RedoOutlined-CU0rkWuz.js";import"./index-CGxiMSah.js";import"./callSuper-DcWcRBJA.js";import"./DownloadOutlined-CSSEbxCr.js";import"./index-D6JX2Tsl.js";import"./index-CcKUnay2.js";import"./index-bhQSPbmK.js";import"./DeleteOutlined-B1cYCZg-.js";import"./index-CM-5c5Hl.js";import"./rgb-BwIoVOhg.js";import"./index-oPzbxqGz.js";const a=({record:e,plot:t})=>o.jsx(o.Fragment,{children:e&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{t({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:e.content.annotations,input_faa:e.content.input_faa},tableDesc:`
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

                    `})},children:" 查看注释结果"}),o.jsx(i,{type:"primary",onClick:()=>{t({saveAnalysisMethod:"eggnog_kegg_table",moduleName:"eggnog_kegg",params:{file_path:e.content.annotations},tableDesc:`
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),q=()=>o.jsxs(o.Fragment,{children:[o.jsx(r,{items:[{key:"eggnog",label:"eggnog",children:o.jsx(o.Fragment,{children:o.jsx(n,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:o.jsx(a,{})})})}]}),o.jsx("p",{})]});export{q as default};
