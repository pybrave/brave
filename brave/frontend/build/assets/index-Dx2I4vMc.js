import{j as o,B as i}from"./main-D6qHus43.js";import{A as r}from"./index-1laYOQoJ.js";import{T as m}from"./index-gg_8jVgT.js";import"./index-CXgqoLfI.js";import"./index-CjmxhRai.js";import"./index-DOQLu3Xz.js";import"./index-CqzThpCE.js";import"./UpOutlined-DC7OgFJP.js";import"./DeleteOutlined-5gHEV1Sl.js";import"./index-BLl0dAbY.js";import"./Dropdown-CMUlroR_.js";import"./Table-Pcm8h2F_.js";import"./addEventListener-TTc5ki3v.js";import"./index-CScjzpru.js";import"./index-DUjGi303.js";import"./createForOfIteratorHelper-Cwfr5VEp.js";import"./DeploymentUnitOutlined-Bm7mxWYi.js";import"./UserSwitchOutlined-DxcFBqrp.js";import"./AudioOutlined-CPyhrC5-.js";import"./ClearOutlined-sPRC32yu.js";import"./TableOutlined-CS-DfnXV.js";import"./NodeIndexOutlined-GDqggOsJ.js";import"./RedoOutlined-DIIHLGCK.js";import"./UndoOutlined-CVmeWyj0.js";import"./react-window-CDDJu4Rx.js";import"./index-D7dvcYwa.js";import"./index-CoiYZhLe.js";import"./index-CYPnvC5G.js";import"./index-CkLVmzff.js";import"./index-oyOmkC6S.js";import"./index-WNIwdokR.js";import"./index-D0Z8XcmH.js";import"./index-CSAVJvIu.js";import"./study-page-CTl0wbzh.js";import"./usePagination-C3C4V5nb.js";import"./index-C4HNXQqg.js";import"./index-ChzQGd2Q.js";import"./index-DyK7Pyu1.js";import"./callSuper-BOdF8PPo.js";import"./index-DjsvXEZy.js";import"./index-DIOsMt1p.js";import"./rgb-BwIoVOhg.js";import"./index-ytJ9UBRy.js";const n=({record:t,plot:e})=>o.jsx(o.Fragment,{children:t&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{e({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:t.content.annotations,input_faa:t.content.input_faa},tableDesc:`
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
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),W=()=>o.jsxs(o.Fragment,{children:[o.jsx(m,{items:[{key:"eggnog",label:"eggnog",children:o.jsx(o.Fragment,{children:o.jsx(r,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:o.jsx(n,{})})})}]}),o.jsx("p",{})]});export{W as default};
