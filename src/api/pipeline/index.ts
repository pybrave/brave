import axios from "axios"
import { setMenuItems } from '@/store/menuSlice'

export const listPipeline  = async (dispatch:any)=>{
    const resp: any = await axios.get(`/list-pipeline-v2`)
    dispatch(setMenuItems(resp.data))
    return resp.data
}

export const listPipelineComponents  = async (params:any)=>{
    const resp: any = await axios.post(`/list-pipeline-components`,params)
    return resp
}