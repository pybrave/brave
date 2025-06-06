import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { BrowserRouter } from 'react-router'
import axios from 'axios';

console.log(import.meta.env.MODE)
if(import.meta.env.MODE!="development"){
  axios.defaults.baseURL = '/pip7878-api';

}


createRoot(document.getElementById('root')!).render(
  // <StrictMode>
  
  // </StrictMode>
    <App />
  ,
)
