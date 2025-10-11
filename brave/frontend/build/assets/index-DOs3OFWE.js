import{j as e,B as n}from"./main-DXb8rb93.js";import{A as i}from"./index-CIvrSkL7.js";import{T as r}from"./index-Cc4yTCQW.js";import"./index-C1SsfXwx.js";import"./Table-Dop9r612.js";import"./addEventListener-BOvmtz4c.js";import"./Dropdown-ClNMeq8P.js";import"./index-BaWKjIxw.js";import"./index-CTlwZfJX.js";import"./index-CtVuDZph.js";import"./index-KXj2g4Cn.js";import"./index-D122PzCT.js";import"./index-D6j9es1G.js";import"./index-C54HiVZI.js";import"./UpOutlined-D94vvVUq.js";import"./index-DIQD0cKY.js";import"./study-page-rPHJnQiw.js";import"./usePagination-gn6S2hbC.js";import"./PlusCircleOutlined-CRNzBXNP.js";import"./index-Cv0-7R_6.js";import"./index-ClyebFq2.js";import"./callSuper-BFEdxNFc.js";import"./index-D9WzkCY-.js";import"./index-hJnvZvPN.js";import"./index-BYUokkww.js";import"./DeleteOutlined-Ba-2K4N2.js";import"./index-CbdpOOR_.js";import"./rgb-BwIoVOhg.js";import"./index-DatT2CMj.js";const a=({record:o,plot:t})=>e.jsx(e.Fragment,{children:o&&e.jsxs(e.Fragment,{children:[e.jsx(n,{type:"primary",onClick:()=>{t({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:o.content.annotations,input_faa:o.content.input_faa},tableDesc:`
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
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),v=()=>e.jsxs(e.Fragment,{children:[e.jsx(r,{items:[{key:"eggnog",label:"eggnog",children:e.jsx(e.Fragment,{children:e.jsx(i,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:e.jsx(a,{})})})}]}),e.jsx("p",{})]});export{v as default};
