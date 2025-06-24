import { createSlice } from '@reduxjs/toolkit'

const menuSlice = createSlice({
  name: 'menu',
  initialState: {
    items: [],       // 菜单项数组
    selectedKey: '', // 当前选中的菜单 key
    
  },
  reducers: {
    setMenuItems: (state, action) => {
      state.items = action.payload
    },
    setSelectedKey: (state, action) => {
      state.selectedKey = action.payload
    },
  },
})

export const { setMenuItems, setSelectedKey } = menuSlice.actions
export default menuSlice.reducer
