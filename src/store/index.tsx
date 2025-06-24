import { configureStore } from '@reduxjs/toolkit'
import menuReducer from './menuSlice'
import projectReducer from './priojectSlice'
const store = configureStore({
  reducer: {
    menu: menuReducer,
    project:projectReducer
  },
})

export default store
