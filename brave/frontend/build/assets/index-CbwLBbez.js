import{j as e,B as r,d as a}from"./main-CuY7LwDi.js";import{A as n}from"./index-DLVZXepE.js";import{T as o}from"./index-BVW_ZuQG.js";import{T as s}from"./index-qOmqaMb2.js";import"./index-BHv34jHO.js";import"./index-DQ88mTzX.js";import"./index-KrImrJYw.js";import"./index-BMhTxeKN.js";import"./Table-C4qk6tSP.js";import"./addEventListener-3f_zys3z.js";import"./Dropdown-BHbGj-Fl.js";import"./index-C59h2Yua.js";import"./index-BtCSA6Uf.js";import"./index-BGst5tb7.js";import"./index-C56i7L-C.js";import"./index-C3ZkAJoo.js";import"./index-CozlEGtu.js";import"./index-DFeHvYNt.js";import"./index-CMWrhJTm.js";import"./index-BHZG3skE.js";import"./study-page-B40m6mCQ.js";import"./usePagination-7P2VlRbv.js";import"./RedoOutlined-BNTfk6-k.js";import"./index-BYHgQKhy.js";import"./callSuper-C5M9W9Ql.js";import"./index-BTG2_cbq.js";import"./index-IVhR9oa8.js";import"./index-BEzmeFWl.js";import"./DeleteOutlined-Cq9E5-_a.js";import"./index-yDSewexe.js";import"./rgb-BwIoVOhg.js";import"./index-H2v9Gx9Q.js";import"./UpOutlined-DnwtgvX4.js";const l=({record:t,plot:i})=>e.jsx(e.Fragment,{children:t?e.jsxs(e.Fragment,{children:[e.jsx(r,{onClick:()=>{i({name:"基因预测统计",saveAnalysisMethod:"prokka_txt_plot",moduleName:"prokka_txt_plot",params:{file_path:t.content.txt}})},children:"基因预测统计"}),e.jsx(r,{onClick:()=>{i({moduleName:"genome_circos_plot_gbk",params:{file_path:t.content.gbk},tableDesc:`
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
