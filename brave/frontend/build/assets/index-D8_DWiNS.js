import{j as t,B as o,i as e,t as m,T as p}from"./index-C6GJdTQl.js";import{A as a}from"./index-DNYGKUta.js";import"./index-CJkY_2Qg.js";import"./index-C6E7TNRc.js";import"./index-rzQilsbl.js";import"./useMergedState-Bk9ED7XV.js";import"./ColorPicker-DTj9C9v5.js";import"./Steps-CET20QEY.js";import"./index-D4F4mIyd.js";import"./addEventListener-CK75kOq2.js";import"./index-CUWDS_la.js";import"./Tree-DaEBZsiY.js";import"./CaretDownFilled-DQmCQKzf.js";import"./Slider-dWjC2uFa.js";import"./ZoomOutOutlined-CBcSnfDw.js";import"./Pagination-DWpMRqT3.js";import"./index-BbnkuI7K.js";import"./createForOfIteratorHelper-DTHKNOo4.js";import"./DeploymentUnitOutlined-BnsIMESi.js";import"./ApartmentOutlined-C4p7fUGr.js";import"./UserSwitchOutlined-CMmEBwEV.js";import"./ClearOutlined-CT7898ko.js";import"./ExperimentOutlined-BOG-0SUy.js";import"./CodeOutlined-DzXWONeZ.js";import"./Upload-C7cqrE9R.js";import"./DeleteOutlined-DFutYCzo.js";import"./DownloadOutlined-DTidZHln.js";import"./ExportOutlined-LnAf6U0q.js";import"./FileAddOutlined-DnyGuR8G.js";import"./TableOutlined-DMv1wQti.js";import"./MinusCircleOutlined-TdsZtRrH.js";import"./NodeIndexOutlined-DBAXk4fg.js";import"./PlusCircleOutlined-B9YvnpOR.js";import"./RedoOutlined-NAONw5hp.js";import"./ReloadOutlined-B00s2TmV.js";import"./UndoOutlined-ufGfyFYW.js";import"./index-D2Hly2cy.js";import"./index-CJF8qUsm.js";import"./index-DB_YvGzs.js";import"./QuestionCircleOutlined-FVNNsfdT.js";import"./MinusCircleOutlined-DXFY5sFX.js";import"./PlusOutlined-l9buKO5c.js";import"./index-DoedwNGm.js";import"./Table-DhRNq3hm.js";import"./index-BRL_NuU8.js";import"./index-BhPGxQzJ.js";import"./index-CKTgCJvi.js";import"./Pagination-DnLovDkv.js";import"./index-CFF1bLBO.js";import"./index-DzMCJ80X.js";import"./index-Dvb1RMm7.js";import"./progress-BAOu_cTc.js";import"./index-BA8iZVcw.js";import"./DownOutlined-BAKiaSwk.js";import"./CloudUploadOutlined-Do5Apu5j.js";import"./EditOutlined-CRhn6hHK.js";import"./DeleteOutlined-CDkaQaq_.js";import"./RedoOutlined-lJ3y5JtZ.js";import"./PlusCircleOutlined-CmznuYhU.js";import"./FileOutlined-DKe8LF1z.js";import"./index-aa1SuQra.js";import"./index-MU_2sHxN.js";import"./index-BDi61Hwp.js";import"./index-DE00T6yA.js";import"./Breadcrumb-FedSvJLx.js";import"./index-BhrgObLV.js";import"./DownloadOutlined-Di59GjeK.js";import"./ReloadOutlined-xted-eYR.js";import"./index-BlIGsXn8.js";import"./edit-params-DWC0zxT8.js";import"./create-or-update-parsms-CTiQc92j.js";import"./invokeV2-DLHTSLD5.js";import"./ClearOutlined-Bv1Wi3jj.js";import"./index-BLJdr5vq.js";import"./code-Dfsmvf0O.js";import"./index-BJftxGOQ.js";import"./index-D29Y8D7w.js";import"./index-5Ic7fb2D.js";import"./index-DPUs6QmO.js";import"./index-DX_DbKUb.js";import"./index-CVUQhrVR.js";import"./index-BrBop8vR.js";import"./study-page-B2qGwXe6.js";import"./usePagination-khpiCi1C.js";import"./CloseOutlined-DEUy3mQa.js";import"./index-DFufQxsn.js";import"./index-yaDGJwqH.js";import"./callSuper-vBX2pDyK.js";import"./useLLMARG-j33EGcp8.js";import"./ExportOutlined-DuSs1Uis.js";import"./index-8hiVl_Ys.js";import"./LineChartOutlined-CJQfaXGJ.js";import"./index-DfQLa4Kj.js";const n=({record:i,plot:r})=>t.jsx(t.Fragment,{children:i?t.jsxs(t.Fragment,{children:[t.jsx(o,{onClick:()=>{r({name:"基因预测统计",saveAnalysisMethod:"prokka_txt_plot",moduleName:"prokka_txt_plot",params:{file_path:i.content.txt}})},children:"基因预测统计"}),t.jsx(o,{onClick:()=>{r({moduleName:"genome_circos_plot_gbk",params:{file_path:i.content.gbk},tableDesc:`
+ GC skew 是一个用来衡量 DNA 序列中 鸟嘌呤（G）和胞嘧啶（C）含量不对称性 的指标，常用于分析细菌基因组的复制起点（oriC）和终点（terC）。
+ GC skew 通常定义为：
$$
GC skew=\\frac{G - C}{G + C}
$$
+ G：一个窗口内 G 的数量
+ C：一个窗口内 C 的数量
+ 值范围：[-1, 1]，值越大表示 G 多于 C，反之亦然。
+ 在基因组图上的意义
    + 在原核生物（如大肠杆菌）中，GC skew 通常沿着基因组有明显的变化。
    + 常用于推测复制起点（origin of replication，ori）和终点（terminus，ter）的位置。
        + ori 附近 GC skew 通常从负变正
        + ter 附近则从正变负


                `})},children:"基因组圈图(gbk)"}),t.jsx(o,{onClick:()=>{r({moduleName:"genome_circos_plot_gff",params:{file_path:i.content.gff}})},children:"基因组圈图(gff)"}),t.jsx(o,{onClick:()=>{r({moduleName:"dna_features_viewer_gbk",params:{file_path:i.content.gbk},formDom:t.jsxs(t.Fragment,{children:[t.jsx(e.Item,{label:"REGION_START ",name:"REGION_START",initialValue:1e3,children:t.jsx(m,{})}),t.jsx(e.Item,{label:"REGION_END ",name:"REGION_END",initialValue:1e4,children:t.jsx(m,{})})]}),tableDesc:`
## 关于基因名称注释
+ gff文件
    + 	1522	2661
    + positive strand
    + ID=PPIEBLPA_00002;
    + Name=dnaN;
    + db_xref=COG:COG0592;
    + gene=dnaN;
    + inference=ab initio prediction:Prodigal:002006,similar to AA sequence:UniProtKB:P05649;
    + locus_tag=PPIEBLPA_00002;
    + product=Beta sliding clamp
+ gkb文件
    + CDS
    +  /gene="dnaN"
    + /locus_tag="PPIEBLPA_00002"
    + /inference="ab initio prediction:Prodigal:002006"
    + /inference="similar to AA sequence:UniProtKB:P05649"
    + /codon_start=1
    + /transl_table=11
    + /product="Beta sliding clamp"
    + /db_xref="COG:COG0592"
    + /translation="MKFTVHRTAFIQYLNDVQRAI...PVRTV"
+ gff文件
    + 1576703	1577125	
    + positive strand
    + ID=PPIEBLPA_01577;
    + inference=ab initio prediction:Prodigal:002006;
    + locus_tag=PPIEBLPA_01577;
    + product=hypothetical protein
+ gkb文件
    + CDS             
    + 1576703..1577125
    + /locus_tag="PPIEBLPA_01577"
    + /inference="ab initio prediction:Prodigal:002006"
    + /codon_start=1
    + /transl_table=11
    + /product="hypothetical protein"
    + /translation="MSNDYRNSEGYPDPTAG...RYFTEECQEV"
                `})},children:" 基因组区域基因(gbk)"}),t.jsx(o,{onClick:()=>{r({name:"prokka初步功能注释",saveAnalysisMethod:"prokka_annotation",moduleName:"prokka_annotation",params:{file_path:i.content.tsv},tableDesc:`
                `})},children:" prokka初步功能注释"})]}):t.jsx(t.Fragment,{children:t.jsx("p",{children:"选择一个样本开始分析"})})}),Ht=()=>t.jsxs(t.Fragment,{children:[t.jsx(p,{items:[{key:"Prokka",label:"Prokka",children:t.jsx(t.Fragment,{children:t.jsx(a,{inputAnalysisMethod:[{name:"1",label:"基因组组装文件",inputKey:["ngs-individual-assembly","tgs_individual_assembly"],mode:"multiple",type:"GroupSelectSampleButton",groupField:"sample_group",rules:[{required:!0,message:"该字段不能为空!"}]}],analysisMethod:[{name:"1",label:"prokka",inputKey:["prokka"],mode:"multiple"}],analysisType:"sample",children:t.jsx(n,{})})})}]}),t.jsx("p",{})]});export{Ht as default};
