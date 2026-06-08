import{r as c,j as e,F as p,x as h,p as d}from"./index-C6GJdTQl.js";import{S as o}from"./index-DB_YvGzs.js";import"./index-D2Hly2cy.js";const m=({publish_urls:r,path:t})=>{const[a,n]=c.useState("SSH");return e.jsxs(e.Fragment,{children:[e.jsx(p,{justify:"end",children:e.jsx(o,{size:"small",unCheckedChildren:"SSH",checkedChildren:"HTTPS",onChange:s=>{n(s?"HTTPS":"SSH")},value:a!=="SSH"})}),r&&r.map((s,i)=>e.jsxs("div",{children:[e.jsx(h,{style:{cursor:"pointer"},onClick:()=>{window.open(s.https,"_blank")},children:s.name}),e.jsx(d,{children:e.jsx("pre",{children:e.jsx("code",{style:{whiteSpace:"pre-wrap"},children:`cd ${t}
git add .
git commit -m 'update'
git remote add ${s.name} ${a==="SSH"?s.ssh:s.https}
git push ${s.name} master`})})}),e.jsx(d,{children:e.jsx("pre",{children:e.jsx("code",{style:{whiteSpace:"pre-wrap"},children:`cd ${t} && git add . && git commit -m 'update' && git push ${s.name} master`})})})]},i))]})};export{m as default};
