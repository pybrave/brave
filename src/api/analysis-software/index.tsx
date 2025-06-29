import axios from "axios"

export const listAnalysisFiles =async  ({project,analysisFileNames,params}:any)=>{
    let resp: any = await axios.post(`/fast-api/find-analyais-result-by-analysis-method`, {
        project: project,
        analysis_method: analysisFileNames,
        ...params
    })
    return resp.data
}