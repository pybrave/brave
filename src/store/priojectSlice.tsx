import { createSlice } from '@reduxjs/toolkit'

const localCurrenct = localStorage.getItem('currenct_project')

const projectSlice = createSlice({
  name: 'project',
  initialState: {
    currenct: localCurrenct
      ? JSON.parse(localCurrenct)  // 如果存在，从 localStorage 解析
      : {
          name: "default project",  // 否则使用默认值
          projectKey: "default"
        },
  },
  reducers: {
    setCurrenct: (state, action) => {
      state.currenct = action.payload
      localStorage.setItem('currenct_project', JSON.stringify(action.payload))  // 更新 localStorage
    }
  }
})


export const { setCurrenct } = projectSlice.actions
export default projectSlice.reducer
