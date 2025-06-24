import axios from "axios"

export const listAnalysisResult =async  ({project,analysisMethodValues,params}:any)=>{
    let resp: any = await axios.post(`/fast-api/find-analyais-result-by-analysis-method`, {
        project: project,
        analysis_method: analysisMethodValues,
        ...params
    })
    return resp.data
}