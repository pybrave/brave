import{j as e,B as r,d as a}from"./main-BzPVmAp-.js";import{A as n}from"./index-CkGaCd3X.js";import{T as o}from"./index-BQm1iTRH.js";import{T as s}from"./index-SGIbgpRk.js";import"./index-BF4b68Hp.js";import"./index-CSq209pq.js";import"./index-sAnz6zLe.js";import"./index-7u0Bo8e4.js";import"./Table-kIlrKW-9.js";import"./addEventListener-CzbSevz3.js";import"./Dropdown-Clv_Pvnt.js";import"./index-BZ6Sq__j.js";import"./index-IijEf41L.js";import"./index-2r9flV8X.js";import"./index-B-RBPprY.js";import"./index-CDeD9lyT.js";import"./index-CUuSmggi.js";import"./index-Fy_dqHL_.js";import"./index-CUrh6kIn.js";import"./index-Djhsc5K4.js";import"./study-page-D4nenWxt.js";import"./usePagination-CGdUxo17.js";import"./RedoOutlined-d_QTXv-s.js";import"./index-Cl0Hi3Gl.js";import"./callSuper-CKCGYiRV.js";import"./index-RAxRq3bL.js";import"./index-D0tEL95I.js";import"./index-BfzdirmR.js";import"./DeleteOutlined-DoDR38qq.js";import"./index-5ngX0NHj.js";import"./rgb-BwIoVOhg.js";import"./index-CQOo18Hr.js";import"./UpOutlined-B_NQN-zy.js";const l=({record:t,plot:i})=>e.jsx(e.Fragment,{children:t?e.jsxs(e.Fragment,{children:[e.jsx(r,{onClick:()=>{i({name:"基因预测统计",saveAnalysisMethod:"prokka_txt_plot",moduleName:"prokka_txt_plot",params:{file_path:t.content.txt}})},children:"基因预测统计"}),e.jsx(r,{onClick:()=>{i({moduleName:"genome_circos_plot_gbk",params:{file_path:t.content.gbk},tableDesc:`
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


                `})},children:"基因组圈图(gbk)"}),e.jsx(r,{onClick:()=>{i({moduleName:"genome_circos_plot_gff",params:{file_path:t.content.gff}})},children:"基因组圈图(gff)"}),e.jsx(r,{onClick:()=>{i({moduleName:"dna_features_viewer_gbk",params:{file_path:t.content.gbk},formDom:e.jsxs(e.Fragment,{children:[e.jsx(a.Item,{label:"REGION_START ",name:"REGION_START",initialValue:1e3,children:e.jsx(o,{})}),e.jsx(a.Item,{label:"REGION_END ",name:"REGION_END",initialValue:1e4,children:e.jsx(o,{})})]}),tableDesc:`
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
                `})},children:" 基因组区域基因(gbk)"}),e.jsx(r,{onClick:()=>{i({name:"prokka初步功能注释",saveAnalysisMethod:"prokka_annotation",moduleName:"prokka_annotation",params:{file_path:t.content.tsv},tableDesc:`
                `})},children:" prokka初步功能注释"})]}):e.jsx(e.Fragment,{children:e.jsx("p",{children:"选择一个样本开始分析"})})}),K=()=>e.jsxs(e.Fragment,{children:[e.jsx(s,{items:[{key:"Prokka",label:"Prokka",children:e.jsx(e.Fragment,{children:e.jsx(n,{inputAnalysisMethod:[{name:"1",label:"基因组组装文件",inputKey:["ngs-individual-assembly","tgs_individual_assembly"],mode:"multiple",type:"GroupSelectSampleButton",groupField:"sample_group",rules:[{required:!0,message:"该字段不能为空!"}]}],analysisMethod:[{name:"1",label:"prokka",inputKey:["prokka"],mode:"multiple"}],analysisType:"sample",children:e.jsx(l,{})})})}]}),e.jsx("p",{})]});export{K as default};
