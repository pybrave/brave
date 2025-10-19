import{j as o,B as i}from"./main-Cq64AMgN.js";import{A as r}from"./index-BJST9lB3.js";import{T as n}from"./index-BN2NQmSZ.js";import"./index-Bq5sU7Ue.js";import"./index-CV_PF3zW.js";import"./index-D9Ce2rPi.js";import"./index-D_LHLpHX.js";import"./UpOutlined-N62njhpo.js";import"./index-DU9NA8Xs.js";import"./index-Dc_dGIGZ.js";import"./Table-DbGD-iom.js";import"./addEventListener-03R2NaZ8.js";import"./Dropdown-DGv8Lzr0.js";import"./index-YruvF9S2.js";import"./react-window-DpKRCTYM.js";import"./RedoOutlined-BJVNqlNz.js";import"./index-DrGnLT3n.js";import"./index-TR_hznsr.js";import"./index-CUv6-i-x.js";import"./index-KwMfgfH8.js";import"./index-BCygBs-J.js";import"./index-B_gcWTWk.js";import"./index-BvhyI6vI.js";import"./study-page-CXLh4DrE.js";import"./usePagination-xTCetvq7.js";import"./index-CVXeocLt.js";import"./callSuper-o7Rw3Goj.js";import"./DownloadOutlined-B_Zvv-ib.js";import"./index-DrhzxsvP.js";import"./index-FKJzyWmI.js";import"./index-JK_QJgFc.js";import"./DeleteOutlined-Sal5uBtx.js";import"./index-B0ALkuS7.js";import"./rgb-BwIoVOhg.js";import"./index-CF7gNIRN.js";const a=({record:t,plot:e})=>o.jsx(o.Fragment,{children:t&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{e({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:t.content.annotations,input_faa:t.content.input_faa},tableDesc:`
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
