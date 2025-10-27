import{j as t,B as r,d as o}from"./main-DDCpF10P.js";import{A as n}from"./index-DpraPWZq.js";import{T as a}from"./index-3M1DwGQt.js";import{T as m}from"./index-UTRMrFLi.js";import"./index-Bb4U7fJr.js";import"./index-BLND9VNM.js";import"./index-DOr26GHb.js";import"./Dropdown-BENEu6xl.js";import"./Table-DSu9PW9f.js";import"./addEventListener-CeJuYbwj.js";import"./index-Bmw2VUkj.js";import"./index-36mrdQic.js";import"./index-DB4VWWzg.js";import"./index-CrxX4M_e.js";import"./createForOfIteratorHelper-CMm9xPXw.js";import"./DeploymentUnitOutlined-CQS9e9a3.js";import"./UserSwitchOutlined-ZboVIKUL.js";import"./AudioOutlined-DbeWwT6X.js";import"./ClearOutlined-ajVE4DvC.js";import"./DeleteOutlined-CIqb_GHe.js";import"./TableOutlined-D0jaCC3Y.js";import"./NodeIndexOutlined-Robcb9kt.js";import"./index-Fu9C-8S6.js";import"./RedoOutlined-CqafmfEh.js";import"./UndoOutlined-UutLNt3R.js";import"./UpOutlined-ChaI2Zov.js";import"./react-window-Y-oFBpKE.js";import"./index-DLKz2xoN.js";import"./index-B4mMhqXR.js";import"./index-BPF_Hiq5.js";import"./index-DsFkX-MR.js";import"./index-DGW0sY_C.js";import"./callSuper-4fofFJ9d.js";import"./index-pCtllbbx.js";import"./index-ZpuGP9__.js";import"./index-Cim_n-MI.js";import"./index-Bl0qQiB6.js";import"./index-Cv9-i3Hj.js";import"./index-6Y9fCObl.js";import"./index-BiDWVMji.js";import"./index-Cxp9-ht5.js";import"./study-page-B21sQcDR.js";import"./usePagination-HtfC8gwS.js";import"./index-vhO2SzV8.js";import"./index-DwXJtm3g.js";import"./index-xosOkNvu.js";import"./panel-6GQ0ZEfB.js";import"./index-4dfNDwEt.js";const p=({record:i,plot:e})=>t.jsx(t.Fragment,{children:i?t.jsxs(t.Fragment,{children:[t.jsx(r,{onClick:()=>{e({name:"基因预测统计",saveAnalysisMethod:"prokka_txt_plot",moduleName:"prokka_txt_plot",params:{file_path:i.content.txt}})},children:"基因预测统计"}),t.jsx(r,{onClick:()=>{e({moduleName:"genome_circos_plot_gbk",params:{file_path:i.content.gbk},tableDesc:`
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


                `})},children:"基因组圈图(gbk)"}),t.jsx(r,{onClick:()=>{e({moduleName:"genome_circos_plot_gff",params:{file_path:i.content.gff}})},children:"基因组圈图(gff)"}),t.jsx(r,{onClick:()=>{e({moduleName:"dna_features_viewer_gbk",params:{file_path:i.content.gbk},formDom:t.jsxs(t.Fragment,{children:[t.jsx(o.Item,{label:"REGION_START ",name:"REGION_START",initialValue:1e3,children:t.jsx(a,{})}),t.jsx(o.Item,{label:"REGION_END ",name:"REGION_END",initialValue:1e4,children:t.jsx(a,{})})]}),tableDesc:`
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
                `})},children:" 基因组区域基因(gbk)"}),t.jsx(r,{onClick:()=>{e({name:"prokka初步功能注释",saveAnalysisMethod:"prokka_annotation",moduleName:"prokka_annotation",params:{file_path:i.content.tsv},tableDesc:`
                `})},children:" prokka初步功能注释"})]}):t.jsx(t.Fragment,{children:t.jsx("p",{children:"选择一个样本开始分析"})})}),rt=()=>t.jsxs(t.Fragment,{children:[t.jsx(m,{items:[{key:"Prokka",label:"Prokka",children:t.jsx(t.Fragment,{children:t.jsx(n,{inputAnalysisMethod:[{name:"1",label:"基因组组装文件",inputKey:["ngs-individual-assembly","tgs_individual_assembly"],mode:"multiple",type:"GroupSelectSampleButton",groupField:"sample_group",rules:[{required:!0,message:"该字段不能为空!"}]}],analysisMethod:[{name:"1",label:"prokka",inputKey:["prokka"],mode:"multiple"}],analysisType:"sample",children:t.jsx(p,{})})})}]}),t.jsx("p",{})]});export{rt as default};
