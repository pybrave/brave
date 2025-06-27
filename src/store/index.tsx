import { configureStore } from '@reduxjs/toolkit'
import menuReducer from './menuSlice'
import projectReducer from './priojectSlice'
import  globalReducer from './globalSlice'

const store = configureStore({
  reducer: {
    menu: menuReducer,
    project:projectReducer,
    global:globalReducer
  },
})

export default store
