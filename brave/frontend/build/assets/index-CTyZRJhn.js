import{j as e,B as o}from"./index-s57B3ha7.js";const m=({record:i,resultTableList:a,plot:r})=>{const n=()=>a.bowtie2_align_metaphlan.map(t=>t.content.log);return e.jsx(e.Fragment,{children:e.jsx(o,{type:"primary",onClick:()=>{r({moduleName:"bowtie2_mapping",params:{log_path_list:n(),mappping_type:"unpaired"},tableDesc:`

                                `})},children:"比对统计"})})},c=({record:i,activeTabKey:a,resultTableList:r,plot:n,analysisKey:t})=>{const p=()=>r[t].map(s=>s.content.log);return e.jsx(e.Fragment,{children:a==t&&e.jsx(e.Fragment,{children:e.jsx(o,{type:"primary",onClick:()=>{n({saveAnalysisMethod:"bowtie2_align_host_table",moduleName:"bowtie2_mapping",params:{log_path_list:p(),mappping_type:"paired"},tableDesc:`

                                `})},children:"比对统计"})})})};export{c as B,m as a};
