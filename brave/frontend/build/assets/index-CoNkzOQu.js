import{j as o,B as i}from"./main-CuY7LwDi.js";import{A as n}from"./index-DLVZXepE.js";import{T as r}from"./index-qOmqaMb2.js";import"./index-BHv34jHO.js";import"./index-DQ88mTzX.js";import"./index-KrImrJYw.js";import"./index-BVW_ZuQG.js";import"./UpOutlined-DnwtgvX4.js";import"./index-BMhTxeKN.js";import"./Table-C4qk6tSP.js";import"./addEventListener-3f_zys3z.js";import"./Dropdown-BHbGj-Fl.js";import"./index-C59h2Yua.js";import"./index-BtCSA6Uf.js";import"./index-BGst5tb7.js";import"./index-C56i7L-C.js";import"./index-C3ZkAJoo.js";import"./index-CozlEGtu.js";import"./index-DFeHvYNt.js";import"./index-CMWrhJTm.js";import"./index-BHZG3skE.js";import"./study-page-B40m6mCQ.js";import"./usePagination-7P2VlRbv.js";import"./RedoOutlined-BNTfk6-k.js";import"./index-BYHgQKhy.js";import"./callSuper-C5M9W9Ql.js";import"./index-BTG2_cbq.js";import"./index-IVhR9oa8.js";import"./index-BEzmeFWl.js";import"./DeleteOutlined-Cq9E5-_a.js";import"./index-yDSewexe.js";import"./rgb-BwIoVOhg.js";import"./index-H2v9Gx9Q.js";const a=({record:e,plot:t})=>o.jsx(o.Fragment,{children:e&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{t({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:e.content.annotations,input_faa:e.content.input_faa},tableDesc:`
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
