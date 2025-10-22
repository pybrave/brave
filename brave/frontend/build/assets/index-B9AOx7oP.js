import{j as o,B as i}from"./main-Bb36JT4B.js";import{A as r}from"./index-DOf8ABVN.js";import{T as m}from"./index-D01PGZ6m.js";import"./index-Cag_gRHe.js";import"./index-hepvEPhH.js";import"./index-Bj9IZtAf.js";import"./index-2YD7whTu.js";import"./UpOutlined-CAwxhdnf.js";import"./DeleteOutlined-e3cflAOk.js";import"./index-JTUypjtn.js";import"./Dropdown-DN1o0f1Q.js";import"./Table-BmozZZHG.js";import"./addEventListener-DVSeb2Tw.js";import"./index-CTSdT7in.js";import"./index-a5nKelg2.js";import"./createForOfIteratorHelper-BcXv2kSG.js";import"./DeploymentUnitOutlined-BloW4Lk-.js";import"./UserSwitchOutlined-DWZ6YS85.js";import"./AudioOutlined-DZYHLJmY.js";import"./ClearOutlined-C8EAuPHL.js";import"./TableOutlined-C9X6pdqB.js";import"./NodeIndexOutlined-BKFsG5mC.js";import"./RedoOutlined-BVTMzSmO.js";import"./UndoOutlined-CGI6NSgT.js";import"./react-window-C6u_-vN5.js";import"./index-CedmWet4.js";import"./index-DgyWQACD.js";import"./index-BqIgTZ86.js";import"./index-C-67I0me.js";import"./index-D34bYyXo.js";import"./index-Bu1BS6Wx.js";import"./index-DV2HUdkJ.js";import"./index-B37dTN1Q.js";import"./study-page-b5Sf5qcC.js";import"./usePagination-Z7YQ7URL.js";import"./index-CiEuomCZ.js";import"./index-B-_UFcBZ.js";import"./index-BXw3nVYM.js";import"./callSuper-Difh5VKN.js";import"./index-DxAaoR83.js";import"./index-ncwm7blR.js";import"./rgb-BwIoVOhg.js";import"./index-Dw9IGcMD.js";const n=({record:t,plot:e})=>o.jsx(o.Fragment,{children:t&&o.jsxs(o.Fragment,{children:[o.jsx(i,{type:"primary",onClick:()=>{e({name:"查看注释结果",saveAnalysisMethod:"print_gggnog",moduleName:"eggnog",params:{file_path:t.content.annotations,input_faa:t.content.input_faa},tableDesc:`
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
