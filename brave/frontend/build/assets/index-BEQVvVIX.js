import{j as o,B as i}from"./main-DDCpF10P.js";import{A as r}from"./index-DpraPWZq.js";import{T as m}from"./index-UTRMrFLi.js";import"./index-Bb4U7fJr.js";import"./index-BLND9VNM.js";import"./index-DOr26GHb.js";import"./Dropdown-BENEu6xl.js";import"./Table-DSu9PW9f.js";import"./addEventListener-CeJuYbwj.js";import"./index-Bmw2VUkj.js";import"./index-36mrdQic.js";import"./index-DB4VWWzg.js";import"./index-3M1DwGQt.js";import"./UpOutlined-ChaI2Zov.js";import"./DeleteOutlined-CIqb_GHe.js";import"./index-CrxX4M_e.js";import"./createForOfIteratorHelper-CMm9xPXw.js";import"./DeploymentUnitOutlined-CQS9e9a3.js";import"./UserSwitchOutlined-ZboVIKUL.js";import"./AudioOutlined-DbeWwT6X.js";import"./ClearOutlined-ajVE4DvC.js";import"./TableOutlined-D0jaCC3Y.js";import"./NodeIndexOutlined-Robcb9kt.js";import"./index-Fu9C-8S6.js";import"./RedoOutlined-CqafmfEh.js";import"./UndoOutlined-UutLNt3R.js";import"./react-window-Y-oFBpKE.js";import"./index-DLKz2xoN.js";import"./index-B4mMhqXR.js";import"./index-BPF_Hiq5.js";import"./index-DsFkX-MR.js";import"./index-DGW0sY_C.js";import"./callSuper-4fofFJ9d.js";import"./index-pCtllbbx.js";import"./index-ZpuGP9__.js";import"./index-Cim_n-MI.js";import"./index-Bl0qQiB6.js";import"./index-Cv9-i3Hj.js";import"./index-6Y9fCObl.js";import"./index-BiDWVMji.js";import"./index-Cxp9-ht5.js";import"./study-page-B21sQcDR.js";import"./usePagination-HtfC8gwS.js";import"./index-vhO2SzV8.js";import"./index-DwXJtm3g.js";import"./index-xosOkNvu.js";import"./panel-6GQ0ZEfB.js";import"./index-4dfNDwEt.js";const n=({record:t,plot:e})=>o.jsx(o.Fragment,{children:t&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{e({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:t.content.annotations,input_faa:t.content.input_faa},tableDesc:`
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
                    `,name:"提取KEGG注释结果"})},children:"提取KEGG注释结果"})]})}),to=()=>o.jsxs(o.Fragment,{children:[o.jsx(m,{items:[{key:"eggnog",label:"eggnog",children:o.jsx(o.Fragment,{children:o.jsx(r,{analysisMethod:[{name:"eggnog",label:"eggnog",inputKey:["eggnog"],mode:"multiple"}],analysisType:"sample",children:o.jsx(n,{})})})}]}),o.jsx("p",{})]});export{to as default};
