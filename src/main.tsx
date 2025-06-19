import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { BrowserRouter } from 'react-router'
import axios from 'axios';
import store from './store'
import { Provider } from 'react-redux'

console.log(import.meta.env.MODE)
axios.defaults.baseURL = '/brave-api';


createRoot(document.getElementById('root')!).render(
  // <StrictMode>

  // </StrictMode>
  <Provider store={store}>
    <App />
  </Provider>
  ,
)
