import{r as s,u as x,a as f,b as y,c as h,d as v,e as g,j as e,C as b,E as j,F as w,B as l,f as E,g as S,s as z}from"./index-C6GJdTQl.js";import C from"./index-DPUs6QmO.js";import"./index-DX_DbKUb.js";import"./ZoomOutOutlined-CBcSnfDw.js";import"./addEventListener-CK75kOq2.js";const R=`
# Bioinformatics Reactive Analysis and Visualization Engine(BRAVE)


BRAVE is a visual bioinformatics workflow platform, similar to Galaxy, that enables intuitive configuration and visualized execution of both upstream and downstream data analyses.

It provides an interactive interface that allows users to quickly develop upstream Nextflow analysis pipelines and downstream visualization scripts using containerized applications such as RStudio, VS Code, and Jupyter.

Once a Nextflow pipeline or visualization script is developed, it can be published to a GitHub repository as a BRAVE “store” app, allowing other analysts to download and use it. Each app maintains isolation, reproducibility, and scalability, leveraging containerized execution to ensure consistent and reliable analyses.


![](/brave-api/img/logo.png)



`,U=()=>{const[V,k]=s.useState(R);x(576);const{project:o,projectObj:a,baseURL:A}=f(t=>t.user),{modal:i,openModal:r,closeModal:c}=y(),d=h();s.useEffect(()=>{console.log("registry",d)},[]);const p=v(),[B,F]=s.useState("llm"),u=async()=>{const t=await S.get(`/project/find-by-project-id/${o}`);p(z({projectObj:t.data}))},{setSideView:m,sideView:M,sideOptions:P,setSideOptions:n}=g();return s.useEffect(()=>(n([{label:"LLM",value:"llm-card"},{label:"Container App",value:"containerAppProject"}]),()=>{n([]),m("llm-card")}),[]),e.jsxs("div",{children:[e.jsx(b,{style:{flex:1,display:"flex",flexDirection:"column",height:" 100%",boxShadow:"none"},styles:{body:{flex:1,display:"flex",flexDirection:"column",height:" 100%",padding:0,overflowY:"auto"}},variant:"borderless",size:"small",extra:e.jsxs(w,{gap:"small",children:[e.jsx(l,{size:"small",color:"cyan",variant:"solid",onClick:()=>{r("projectForm",{project_id:o})},children:"Edit"}),e.jsx(l,{size:"small",color:"cyan",variant:"solid",onClick:()=>{u()},children:"Refresh"})]}),children:a!=null&&a.description?e.jsx(C,{data:a==null?void 0:a.description}):e.jsx(j,{})}),e.jsx(E,{research:!0,params:i.params,visible:i.key=="projectForm"&&i.visible,onClose:c})]})};export{U as default};
