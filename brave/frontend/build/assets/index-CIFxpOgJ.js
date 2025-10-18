import{j as o,B as i}from"./main-CoRdKxM6.js";import{A as r}from"./index-mV1N3V4H.js";import{T as n}from"./index-BHj1h2oY.js";import"./index-Bzqqa-Nl.js";import"./index-DeUYg7UX.js";import"./index-LdYoExsQ.js";import"./index-U82OZ9hL.js";import"./UpOutlined-CjGJavdL.js";import"./index-Dm3E-_FQ.js";import"./index-mKsixq-F.js";import"./Table-C-94KlQV.js";import"./addEventListener-BYJT43cw.js";import"./Dropdown-MRVofdb8.js";import"./index-Cww7bxT4.js";import"./index-COT9qJ9K.js";import"./index-DbEsz9wv.js";import"./index-3Hfn-eC3.js";import"./index-Cl14Vxoo.js";import"./index-BlGESwK1.js";import"./index-DD8IFb_f.js";import"./index-BZOaq6gR.js";import"./study-page-D9BlhB0m.js";import"./usePagination-P-dGKUc-.js";import"./RedoOutlined-CtyAtPBD.js";import"./index-BdK9PNzv.js";import"./callSuper-tBPAaQ6e.js";import"./DownloadOutlined-DnjYLYJT.js";import"./index-BFM7er4q.js";import"./index-DC2UGVbx.js";import"./index-CIQpBAFN.js";import"./DeleteOutlined-LAT7OMWc.js";import"./index-2BxIOf55.js";import"./rgb-BwIoVOhg.js";import"./index-C0mKHvkr.js";const a=({record:t,plot:e})=>o.jsx(o.Fragment,{children:t&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{e({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:t.content.annotations,input_faa:t.content.input_faa},tableDesc:`
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
