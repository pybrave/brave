import { Breadcrumb, Button, Flex, Skeleton, Tabs, Tag } from "antd"
import { FC, useEffect, useState } from "react"
import AnalysisPanel from '../analysis-panel'
import Meta from "antd/es/card/Meta"
import { colors } from '@/utils/utils'

import axios from "axios"
import { useNavigate, useOutletContext, useParams } from "react-router"
import { listPipeline } from "@/api/pipeline"
const Pipeline: FC<any> = ({ name }) => {
    const [pipeline, setPipeline] = useState<any>()
    const [items, setItems] = useState<any>([])
    const navigate = useNavigate();
  
    const loadFunction: any = (data: any[]) => {
        if (!data) return undefined
        return data.map((item: any) => {
            if ("paramsFun" in item) {
                item.paramsFun = eval(item.paramsFun)
            }
            if("formJson" in item){
                item['formJson'].map((it2:any)=>{
                    if("filter" in it2){
                        it2['filter'].map((it3:any)=>{
                            it3.method= eval(it3.method)
                            return it3
                        })
                    }

                    it2.field = eval(it2.field)
                    return it2
                })
                
            }
            return item
        })
    }
    const loadColumnRender: any = (data: any[]) => {
        if (!data) return []
        return data.map((item: any) => {
            if ("render" in item) {
                const render = eval(item.render)
                item.render = (_: any, record: any) => <>
                    {render(record)}
                </>
            }
            return item
        })
    }
    const getPipline: any = (wrapAnalysisPipeline:any,pipeline: any[]) => {
        // console.log(pipeline)
        return pipeline.map((item, index) => {

            return {
                key: index,
                label: item.name,
                children: <AnalysisPanel
                    wrapAnalysisPipeline={wrapAnalysisPipeline}
                    inputAnalysisMethod={item.inputAnalysisMethod}
                    analysisPipline={item.analysisPipline}
                    analysisMethod={item.analysisMethod}
                    downstreamAnalysis={loadFunction(item.downstreamAnalysis)}
                    upstreamFormJson={item.upstreamFormJson}
                    appendSampleColumns={loadColumnRender(item.appendSampleColumns)}
                    parseAnalysisParams={{
                        parse_analysis_module: item.parseAnalysisModule,
                        parse_analysis_result_module: item.parseAnalysisResultModule
                    }}
                    analysisType={item.analysisType ? item.analysisType : "sample"}>
                </AnalysisPanel>
            }
        })
    }
    // [
    //     {
    //         name: "查看比对日志",
    //         analysisType: "one", // multiple or one
    //         sampleGroupJSON: false,
    //         paramsFun: (record: any) => {
    //             return {
    //                 "text": record.content.log,
    //             }
    //         },
    //         sampleGroupApI: false,
    //         saveAnalysisMethod: "text",
    //         moduleName: "text",
    //         sampleSelectComp: false,
    //         tableDesc: ` `,

    //     }
    // ]
    const loadData = async () => {
        const resp = await axios.get(`/get-pipeline/${name}`)
        // console.log(resp.data)
        setPipeline(resp.data)

    }
    useEffect(() => {
        loadData()
    }, [])
    return <div style={{ maxWidth: "1800px", margin: "0 auto" }}>

        <Flex style={{ marginBottom: "1rem" }} justify={"space-between"} align={"center"} gap="small">
            <div >
                {pipeline ? <>
                    <h2 style={{ margin: 0 }}>{pipeline?.name}</h2>
                    <p style={{ margin: "0", color: "rgba(0, 0, 0, 0.45)" }}>{pipeline?.description}</p>
                    {pipeline.tags && Array.isArray(pipeline.tags) && pipeline.tags.map((tag: any, index: any) => (
                        <Tag style={{ marginTop: "0.5rem" }} key={index} color={colors[index]}>{tag}</Tag>
                    ))}
                </> : <Skeleton active></Skeleton>}
            </div>
            <Flex gap="small" wrap>
                <Button color="cyan" variant="solid">流程介绍</Button>
                <Button color="cyan" variant="solid" onClick={loadData}>刷新</Button>
                <Button color="primary" variant="solid" onClick={() => navigate(`/pipeline-card`)}>返回</Button>
            </Flex>

        </Flex>

        {pipeline && Array.isArray(pipeline?.items) ? <Tabs  items={getPipline(pipeline.wrapAnalysisPipeline,pipeline.items)}></Tabs> : <Skeleton active></Skeleton>}
    </div>
}


export default Pipeline
