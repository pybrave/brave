import axios from "axios"
import { setMenuItems } from '@/store/menuSlice'

export const listPipeline  = async (dispatch:any)=>{
    const resp: any = await axios.get(`/list-pipeline`)
    dispatch(setMenuItems(resp.data))
    return resp.data
}