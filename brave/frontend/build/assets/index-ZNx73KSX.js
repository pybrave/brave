import{j as o,B as i}from"./main-BzPVmAp-.js";import{A as n}from"./index-CkGaCd3X.js";import{T as r}from"./index-SGIbgpRk.js";import"./index-BF4b68Hp.js";import"./index-CSq209pq.js";import"./index-sAnz6zLe.js";import"./index-BQm1iTRH.js";import"./UpOutlined-B_NQN-zy.js";import"./index-7u0Bo8e4.js";import"./Table-kIlrKW-9.js";import"./addEventListener-CzbSevz3.js";import"./Dropdown-Clv_Pvnt.js";import"./index-BZ6Sq__j.js";import"./index-IijEf41L.js";import"./index-2r9flV8X.js";import"./index-B-RBPprY.js";import"./index-CDeD9lyT.js";import"./index-CUuSmggi.js";import"./index-Fy_dqHL_.js";import"./index-CUrh6kIn.js";import"./index-Djhsc5K4.js";import"./study-page-D4nenWxt.js";import"./usePagination-CGdUxo17.js";import"./RedoOutlined-d_QTXv-s.js";import"./index-Cl0Hi3Gl.js";import"./callSuper-CKCGYiRV.js";import"./index-RAxRq3bL.js";import"./index-D0tEL95I.js";import"./index-BfzdirmR.js";import"./DeleteOutlined-DoDR38qq.js";import"./index-5ngX0NHj.js";import"./rgb-BwIoVOhg.js";import"./index-CQOo18Hr.js";const a=({record:e,plot:t})=>o.jsx(o.Fragment,{children:e&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{t({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:e.content.annotations,input_faa:e.content.input_faa},tableDesc:`
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
