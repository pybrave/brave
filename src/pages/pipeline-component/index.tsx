import axios from "axios"
import { FC, useEffect } from "react"

const PipelineComponent:FC<any> = ()=>{

    const loadData = async ()=>{
        const resp = await axios.post("/list-pipeline-components",{})
        console.log(resp)
    }
    useEffect(()=>{
        loadData()
    },[])
    return <>


    
    </>
}

export default PipelineComponent