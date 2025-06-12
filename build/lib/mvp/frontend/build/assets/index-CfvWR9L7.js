import{j as e}from"./index-01VgbQhG.js";import{B as n}from"./Table-CvEpiXur.js";const c=({record:i,resultTableList:r,plot:a})=>{const o=()=>r.bowtie2_align_metaphlan.map(t=>t.content.log);return e.jsx(e.Fragment,{children:e.jsx(n,{type:"primary",onClick:()=>{a({moduleName:"bowtie2_mapping",params:{log_path_list:o(),mappping_type:"unpaired"},tableDesc:`

                                `})},children:"比对统计"})})},g=({record:i,activeTabKey:r,resultTableList:a,plot:o,analysisKey:t})=>{const p=()=>a[t].map(s=>s.content.log);return e.jsx(e.Fragment,{children:r==t&&e.jsx(e.Fragment,{children:e.jsx(n,{type:"primary",onClick:()=>{o({saveAnalysisMethod:"bowtie2_align_host_table",moduleName:"bowtie2_mapping",params:{log_path_list:p(),mappping_type:"paired"},tableDesc:`

                                `})},children:"比对统计"})})})};export{g as B,c as a};
