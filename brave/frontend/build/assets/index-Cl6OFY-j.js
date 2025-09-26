import{j as e,B as n}from"./main-BFdXSxSk.js";import{A as a}from"./index-DEkgPIbe.js";import{T as i}from"./index-u54hlnBP.js";import"./index-BBEK43-c.js";import"./Table-CAzGvc6L.js";import"./addEventListener-CGGMUWeS.js";import"./Dropdown-CjWuFlcv.js";import"./index-CrFRXVOt.js";import"./index-Bu_8sAQb.js";import"./index-Xuhmhtyr.js";import"./index-CnfuLd-S.js";import"./index-CI0YXrM6.js";import"./index-B8u-5pkT.js";import"./index-CZ2lHT-7.js";import"./UpOutlined-CtyUmY8V.js";import"./index-KokPGa7l.js";import"./index-U2Qux_ly.js";import"./callSuper-oFdrjfx8.js";import"./index-g18VTZV4.js";import"./index-CqJakpDQ.js";import"./index-D9VVzYL-.js";import"./usePagination-D-1FogKP.js";import"./DeleteOutlined-ZGsgJzFv.js";import"./index-fiOldDlD.js";import"./rgb-BwIoVOhg.js";import"./index-BHxhgCsS.js";const r=({record:o,plot:t})=>e.jsx(e.Fragment,{children:o&&e.jsxs(e.Fragment,{children:[e.jsx(n,{type:"primary",onClick:()=>{t({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:o.content.annotations,input_faa:o.content.input_faa},tableDesc:`
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
