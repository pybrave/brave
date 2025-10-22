import{j as e,B as r,d as o}from"./main-Bb36JT4B.js";import{A as n}from"./index-DOf8ABVN.js";import{T as a}from"./index-2YD7whTu.js";import{T as m}from"./index-D01PGZ6m.js";import"./index-Cag_gRHe.js";import"./index-hepvEPhH.js";import"./index-Bj9IZtAf.js";import"./index-JTUypjtn.js";import"./Dropdown-DN1o0f1Q.js";import"./Table-BmozZZHG.js";import"./addEventListener-DVSeb2Tw.js";import"./index-CTSdT7in.js";import"./index-a5nKelg2.js";import"./createForOfIteratorHelper-BcXv2kSG.js";import"./DeploymentUnitOutlined-BloW4Lk-.js";import"./UserSwitchOutlined-DWZ6YS85.js";import"./AudioOutlined-DZYHLJmY.js";import"./ClearOutlined-C8EAuPHL.js";import"./DeleteOutlined-e3cflAOk.js";import"./TableOutlined-C9X6pdqB.js";import"./NodeIndexOutlined-BKFsG5mC.js";import"./RedoOutlined-BVTMzSmO.js";import"./UndoOutlined-CGI6NSgT.js";import"./UpOutlined-CAwxhdnf.js";import"./react-window-C6u_-vN5.js";import"./index-CedmWet4.js";import"./index-DgyWQACD.js";import"./index-BqIgTZ86.js";import"./index-C-67I0me.js";import"./index-D34bYyXo.js";import"./index-Bu1BS6Wx.js";import"./index-DV2HUdkJ.js";import"./index-B37dTN1Q.js";import"./study-page-b5Sf5qcC.js";import"./usePagination-Z7YQ7URL.js";import"./index-CiEuomCZ.js";import"./index-B-_UFcBZ.js";import"./index-BXw3nVYM.js";import"./callSuper-Difh5VKN.js";import"./index-DxAaoR83.js";import"./index-ncwm7blR.js";import"./rgb-BwIoVOhg.js";import"./index-Dw9IGcMD.js";const s=({record:t,plot:i})=>e.jsx(e.Fragment,{children:t?e.jsxs(e.Fragment,{children:[e.jsx(r,{onClick:()=>{i({name:"基因预测统计",saveAnalysisMethod:"prokka_txt_plot",moduleName:"prokka_txt_plot",params:{file_path:t.content.txt}})},children:"基因预测统计"}),e.jsx(r,{onClick:()=>{i({moduleName:"genome_circos_plot_gbk",params:{file_path:t.content.gbk},tableDesc:`
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


                `})},children:"基因组圈图(gbk)"}),e.jsx(r,{onClick:()=>{i({moduleName:"genome_circos_plot_gff",params:{file_path:t.content.gff}})},children:"基因组圈图(gff)"}),e.jsx(r,{onClick:()=>{i({moduleName:"dna_features_viewer_gbk",params:{file_path:t.content.gbk},formDom:e.jsxs(e.Fragment,{children:[e.jsx(o.Item,{label:"REGION_START ",name:"REGION_START",initialValue:1e3,children:e.jsx(a,{})}),e.jsx(o.Item,{label:"REGION_END ",name:"REGION_END",initialValue:1e4,children:e.jsx(a,{})})]}),tableDesc:`
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
                `})},children:" prokka初步功能注释"})]}):e.jsx(e.Fragment,{children:e.jsx("p",{children:"选择一个样本开始分析"})})}),X=()=>e.jsxs(e.Fragment,{children:[e.jsx(m,{items:[{key:"Prokka",label:"Prokka",children:e.jsx(e.Fragment,{children:e.jsx(n,{inputAnalysisMethod:[{name:"1",label:"基因组组装文件",inputKey:["ngs-individual-assembly","tgs_individual_assembly"],mode:"multiple",type:"GroupSelectSampleButton",groupField:"sample_group",rules:[{required:!0,message:"该字段不能为空!"}]}],analysisMethod:[{name:"1",label:"prokka",inputKey:["prokka"],mode:"multiple"}],analysisType:"sample",children:e.jsx(s,{})})})}]}),e.jsx("p",{})]});export{X as default};
