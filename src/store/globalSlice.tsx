import { createSlice } from '@reduxjs/toolkit'


const globalSlice = createSlice({
  name: 'global',
  initialState: {
    sseData:{}
  },
  reducers: {
    setSseData: (state, action) => {
      state.sseData = action.payload
    }
  }
})


export const { setSseData } = globalSlice.actions
export default globalSlice.reducer
