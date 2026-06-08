import{r as p,j as e,T as c,B as i,i as _,S as d,k as g,g as h}from"./index-C6GJdTQl.js";import{A as y}from"./index-DNYGKUta.js";import"./index-CJkY_2Qg.js";import"./index-C6E7TNRc.js";import"./index-rzQilsbl.js";import"./useMergedState-Bk9ED7XV.js";import"./ColorPicker-DTj9C9v5.js";import"./Steps-CET20QEY.js";import"./index-D4F4mIyd.js";import"./addEventListener-CK75kOq2.js";import"./index-CUWDS_la.js";import"./Tree-DaEBZsiY.js";import"./CaretDownFilled-DQmCQKzf.js";import"./Slider-dWjC2uFa.js";import"./ZoomOutOutlined-CBcSnfDw.js";import"./Pagination-DWpMRqT3.js";import"./index-BbnkuI7K.js";import"./createForOfIteratorHelper-DTHKNOo4.js";import"./DeploymentUnitOutlined-BnsIMESi.js";import"./ApartmentOutlined-C4p7fUGr.js";import"./UserSwitchOutlined-CMmEBwEV.js";import"./ClearOutlined-CT7898ko.js";import"./ExperimentOutlined-BOG-0SUy.js";import"./CodeOutlined-DzXWONeZ.js";import"./Upload-C7cqrE9R.js";import"./DeleteOutlined-DFutYCzo.js";import"./DownloadOutlined-DTidZHln.js";import"./ExportOutlined-LnAf6U0q.js";import"./FileAddOutlined-DnyGuR8G.js";import"./TableOutlined-DMv1wQti.js";import"./MinusCircleOutlined-TdsZtRrH.js";import"./NodeIndexOutlined-DBAXk4fg.js";import"./PlusCircleOutlined-B9YvnpOR.js";import"./RedoOutlined-NAONw5hp.js";import"./ReloadOutlined-B00s2TmV.js";import"./UndoOutlined-ufGfyFYW.js";import"./index-D2Hly2cy.js";import"./index-CJF8qUsm.js";import"./index-DB_YvGzs.js";import"./QuestionCircleOutlined-FVNNsfdT.js";import"./MinusCircleOutlined-DXFY5sFX.js";import"./PlusOutlined-l9buKO5c.js";import"./index-DoedwNGm.js";import"./Table-DhRNq3hm.js";import"./index-BRL_NuU8.js";import"./index-BhPGxQzJ.js";import"./index-CKTgCJvi.js";import"./Pagination-DnLovDkv.js";import"./index-CFF1bLBO.js";import"./index-DzMCJ80X.js";import"./index-Dvb1RMm7.js";import"./progress-BAOu_cTc.js";import"./index-BA8iZVcw.js";import"./DownOutlined-BAKiaSwk.js";import"./CloudUploadOutlined-Do5Apu5j.js";import"./EditOutlined-CRhn6hHK.js";import"./DeleteOutlined-CDkaQaq_.js";import"./RedoOutlined-lJ3y5JtZ.js";import"./PlusCircleOutlined-CmznuYhU.js";import"./FileOutlined-DKe8LF1z.js";import"./index-aa1SuQra.js";import"./index-MU_2sHxN.js";import"./index-BDi61Hwp.js";import"./index-DE00T6yA.js";import"./Breadcrumb-FedSvJLx.js";import"./index-BhrgObLV.js";import"./DownloadOutlined-Di59GjeK.js";import"./ReloadOutlined-xted-eYR.js";import"./index-BlIGsXn8.js";import"./edit-params-DWC0zxT8.js";import"./create-or-update-parsms-CTiQc92j.js";import"./invokeV2-DLHTSLD5.js";import"./ClearOutlined-Bv1Wi3jj.js";import"./index-BLJdr5vq.js";import"./code-Dfsmvf0O.js";import"./index-BJftxGOQ.js";import"./index-D29Y8D7w.js";import"./index-5Ic7fb2D.js";import"./index-DPUs6QmO.js";import"./index-DX_DbKUb.js";import"./index-CVUQhrVR.js";import"./index-BrBop8vR.js";import"./study-page-B2qGwXe6.js";import"./usePagination-khpiCi1C.js";import"./CloseOutlined-DEUy3mQa.js";import"./index-DFufQxsn.js";import"./index-yaDGJwqH.js";import"./callSuper-vBX2pDyK.js";import"./useLLMARG-j33EGcp8.js";import"./ExportOutlined-DuSs1Uis.js";import"./index-8hiVl_Ys.js";import"./LineChartOutlined-CJQfaXGJ.js";import"./index-DfQLa4Kj.js";const f=({record:t,plot:r,setHtmlUrl:u,cleanDom:s,resultTableList:m,form:l})=>{const[a,n]=p.useState();return e.jsx(e.Fragment,{children:e.jsx(c,{onChange:s,items:[{key:"1",label:"多样本分析",children:e.jsxs(e.Fragment,{children:[e.jsx(i,{type:"primary",onClick:()=>{r({saveAnalysisMethod:"mutations_gene",moduleName:"circos_plot_mutations",params:{file_path:"/ssd1/wy/workspace2/leipu/leipu_workspace2/output/breseq/OSP-6/data/OSP-6.count"},formDom:e.jsx(e.Fragment,{children:e.jsx(_.Item,{name:"list_files",label:"选择样本",children:e.jsx(d,{mode:"multiple",style:{maxWidth:"20rem"},allowClear:!0,options:m.breseq?m.breseq.map(o=>({label:`${o.sample_name} (${o.content.reference})`,value:`${o.sample_name}#${o.content.annotated_tsv}`})):[]})})}),tableDesc:`
+ 选择样本说明:
    + 下拉框样本的命名格式为: 样本名 (参考基因组)

                                `})},children:"基因突变圈图"}),e.jsx(i,{type:"primary",onClick:()=>{r({sampleGroupJSON:!0,formJson:[{name:"genome",label:"基因组",rules:[{required:!0,message:"该字段不能为空!"}],type:"FilterFieldSelect",field:o=>o.content.reference,clear:["sites"]},{name:"group_field",label:"分组列",rules:[{required:!0,message:"该字段不能为空!"}],type:"GroupFieldSelect"},{name:"sites",label:"部位",rules:[{required:!0,message:"该字段不能为空!"}],type:"GroupSelectSampleButton",group:"group_field",filter:[{name:"genome",method:o=>o.content.reference}]}],sampleGroupApI:!1,saveAnalysisMethod:"snv_phylogenetic_tree",moduleName:"snv_phylogenetic_tree",sampleSelectComp:!1,tableDesc:" ",name:"基于SNV系统发育树"})},children:"基于SNV系统发育树"})]})},{key:"2",label:e.jsxs(e.Fragment,{children:["单样本分析(",t&&e.jsxs(e.Fragment,{children:[t==null?void 0:t.analysis_name,"-",t==null?void 0:t.sample_name]}),")"]}),disabled:!t,children:e.jsxs(e.Fragment,{children:[e.jsx(i,{onClick:()=>{r({url:g(t.content.index_html),tableDesc:`
+ [结果说明文档](https://gensoft.pasteur.fr/docs/breseq/0.35.0/output.html#html-human-readable-output)

![](https://gensoft.pasteur.fr/docs/breseq/0.35.0/_images/snp_2.png)
> 在 ychE 和 oppA 基因之间的基因间区域，用一个 G 替换了位于 1,298,712 位的参考 T。该基因突变在 ychE 的下游 674 个碱基（因为该基因的位置在 ychE 之前，且在参考文献的顶链上），在 oppA 的上游 64 个碱基（因为该基因的位置在 oppA 之后，且也在基因组的顶链上）。                        `})},children:"查看报告"}),e.jsx(i,{onClick:()=>{r({moduleName:"tsv",params:{file_path:t.content.annotated_tsv},tableDesc:`
## locus_tag的解释(OSI-5为例)
+ 对于gyrB/gyrA、PPIEBLPA_00087/PPIEBLPA_00088, 这类locus_tag对应的mutation_category包括
    + snp_intergenic: snp位点发生在基因间区，/ 前的两个基因代表突变位点的上游和下游的基因
    + small_indel: indel位点发生在基因间区，/ 前的两个基因代表突变位点的上游和下游的基因        
    + large_deletion: large deletion位点发生在基因间区，/ 前的两个基因代表突变位点的上游和下游的基因      
+ 对于PPIEBLPA_01703|PPIEBLPA_01704，突变位点1711867同时发生在两个基因上
    + rhaR_2: 1711442	1711870
    + malL_1: 1711861	1713489                             
+ 对于[PPIEBLPA_00342]–[PPIEBLPA_00343]代表large deletion跨越了两个基因
+ 对于[PPIEBLPA_00863]代表large deletion发生在基因区，以及该基因的基因间区

> 在分析中可以使用df.query("~locus_tag.str.contains('/') & ~locus_tag.str.contains('[') & ~locus_tag.str.contains('|') & ~locus_tag.str.contains('–')")将上述locus_tag排除,
这样做方便将新的基因注释结果与变异位点相匹配。

## 字段解释

| 字段                                           | 含义                                         |
| -------------------------------------------- | ------------------------------------------ |
| "type": "SNP"                              | 变异类型为单碱基突变（Single Nucleotide Polymorphism） |
| "position": 18936                          | 突变在参考序列上的位置（从1开始）                          |
| "ref_seq": "G"                             | 参考基因组中的碱基是 G                               |
| "new_seq": "T"                             | 变异后读到的是 T                                  |
| "snp_type": "nonsynonymous"                | 非同义突变（导致氨基酸改变）                             |
| "gene_name": "rplI"                        | 受影响的基因名称                                   |
| "gene_product": "50S ribosomal protein L9" | 基因对应的蛋白产品                                  |
| "gene_position": "196"                     | 变异在基因内的位置（碱基坐标）                            |
| "gene_strand": ">"                         | 基因所在链为正链                                   |
| "codon_ref_seq": "GTC"                     | 参考密码子（突变前）为 GTC（编码 Val）                    |
| "codon_new_seq": "TTC"                     | 突变后密码子为 TTC（编码 Phe）                        |
| "aa_ref_seq": "V"                          | 原氨基酸是 V（Val）                               |
| "aa_new_seq": "F"                          | 突变后为 F（Phe）                                |
| "aa_position": "66"                        | 受影响的氨基酸位置是第 66 个                           |
| "codon_number": "66"                       | 对应第 66 个密码子                                |
| "codon_position": "1"                      | 突变发生在密码子的第1位（G→T）                          |
| "mutation_category": "snp_nonsynonymous"   | 更详细的突变分类                                   |
| "locus_tag": "PPIEBLPA_00018"              | 对应注释中的 locus tag                           |
| "locus_tags_overlapping": "PPIEBLPA_00018" | 与该突变重叠的 locus                              |
| "new_read_count": 661                     | 支持新突变的测序读数数目                               |
| "ref_read_count": 0                        | 支持参考序列的读数数量（说明突变已固定或非常纯）                   |
| "seq_id": "Chr"                            | 突变发生在哪条序列上（例如染色体或质粒）                       |
                `})},children:"查看表格"}),e.jsx(i,{onClick:()=>{r({moduleName:"breseq_statistic",params:{file_path:t.content.annotated_count},tableDesc:`
                `})},children:"变异统计"})]})}]})})},it=()=>{const[t,r]=p.useState([]),[u,s]=p.useState(!1),m=async()=>{s(!0);const a=await h.get("/api/mutation");console.log(a),s(!1),r(a.data)};p.useEffect(()=>{m()},[]);const l=[{title:"参考基因组",dataIndex:"reference",key:"reference",ellipsis:!0,render:(a,n)=>{var o;return e.jsx(e.Fragment,{children:(o=n==null?void 0:n.content)==null?void 0:o.reference})}}];return e.jsx(e.Fragment,{children:e.jsx(c,{items:[{label:"breseq",key:"breseq",children:e.jsx(y,{appendSampleColumns:l,analysisMethod:[{name:"breseq",label:"breseq",inputKey:["breseq"],mode:"multiple"}],analysisType:"sample",children:e.jsx(f,{})})}]})})};export{it as default};
