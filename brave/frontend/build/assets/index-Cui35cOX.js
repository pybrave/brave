import{j as e,B as n,F as t,az as s,T as r,A as l}from"./index-s57B3ha7.js";const o=({record:a,plot:i})=>e.jsx(e.Fragment,{children:a?e.jsxs(e.Fragment,{children:[e.jsx(n,{onClick:()=>{i({moduleName:"prokka_txt_plot",params:{file_path:a.content.txt}})},children:"基因预测统计"}),e.jsx(n,{onClick:()=>{i({moduleName:"genome_circos_plot_gbk",params:{file_path:a.content.gbk},tableDesc:`
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


                `})},children:"基因组圈图(gbk)"}),e.jsx(n,{onClick:()=>{i({moduleName:"genome_circos_plot_gff",params:{file_path:a.content.gff}})},children:"基因组圈图(gff)"}),e.jsx(n,{onClick:()=>{i({moduleName:"dna_features_viewer_gbk",params:{file_path:a.content.gbk},formDom:e.jsxs(e.Fragment,{children:[e.jsx(t.Item,{label:"REGION_START ",name:"REGION_START",initialValue:1e3,children:e.jsx(s,{})}),e.jsx(t.Item,{label:"REGION_END ",name:"REGION_END",initialValue:1e4,children:e.jsx(s,{})})]}),tableDesc:`
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
                `})},children:" 基因组区域基因(gbk)"}),e.jsx(n,{onClick:()=>{i({moduleName:"prokka_annotation",params:{file_path:a.content.tsv},tableDesc:`
                `})},children:" prokka初步功能注释"})]}):e.jsx(e.Fragment,{children:e.jsx("p",{children:"选择一个样本开始分析"})})}),d=()=>e.jsxs(e.Fragment,{children:[e.jsx(r,{items:[{key:"Prokka",label:"Prokka",children:e.jsx(e.Fragment,{children:e.jsx(l,{inputAnalysisMethod:[{key:"1",name:"基因组组装文件",value:["ngs-individual-assembly","tgs_individual_assembly"],mode:"multiple",type:"GroupSelectSampleButton",groupField:"sample_group",rules:[{required:!0,message:"该字段不能为空!"}]}],analysisMethod:[{key:"1",name:"prokka",value:["prokka"],mode:"multiple"}],analysisType:"sample",children:e.jsx(o,{})})})}]}),e.jsx("p",{})]});export{d as default};
