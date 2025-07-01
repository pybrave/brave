import { Breadcrumb, Button, Empty, Flex, message, Modal, Skeleton, Tabs, Tag } from "antd"
import { FC, useEffect, useState } from "react"
import AnalysisPanel from '../analysis-sotware-panel'
import Meta from "antd/es/card/Meta"
import { colors } from '@/utils/utils'

import axios from "axios"
import { useLocation, useNavigate, useOutletContext, useParams } from "react-router"
import { listPipeline } from "@/api/pipeline"
import { CreateORUpdatePipelineCompnentRelation, CreateOrUpdatePipelineComponent } from "../create-pipeline"
import ModuleEdit from "../module-edit"
import { useModal } from '@/hooks/useModal'
const Pipeline: FC<any> = ({ }) => {
    const { pipelineId: name } = useParams()
    // console.log(pipelineId)
    const [pipeline, setPipeline] = useState<any>()
    const [items, setItems] = useState<any>([])
    const navigate = useNavigate();

    const [messageApi, contextHolder] = message.useMessage();
    // const [editor, setEditor] = useState<any>({
    //     open: false,
    // })
    // const updateEditor = (key: string, value: any) => {
    //     setEditor((prev: any) => ({
    //         ...prev,
    //         [key]: value
    //     }));
    // };
    const { modal, openModal, closeModal } = useModal();

    // const [createOpen, setCreateOpen] = useState<any>(false)
    // const [record, setRecord] = useState<any>()
    // const [pipelineStructure, setPipelineStructure] = useState<any>()



    const loadFunction: any = (data: any[]) => {
        if (!data) return undefined
        return data.map((item: any) => {
            if ("paramsFun" in item) {
                item.paramsFun = eval(item.paramsFun)
            }
            if ("formJson" in item) {
                item['formJson'].map((it2: any) => {
                    if ("filter" in it2) {
                        it2['filter'].map((it3: any) => {
                            it3.method = eval(it3.method)
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

    const getPipline: any = (pipeline: any) => {
        // console.log(pipeline)
        const softwareList: any[] = pipeline.items
        // console.log(pipeline)
        if (!softwareList) return []
        return softwareList.map((item, index) => {
            // const { downstreamAnalysis, appendSampleColumns, analysisType, ...rest } = item
            return {
                key: index + 1,
                label: item.name,
                children: <AnalysisPanel

                    // inputAnalysisMethod={item.inputAnalysisMethod}
                    // analysisPipline={item.analysisPipline}
                    // analysisMethod={item.analysisMethod}
                    // upstreamFormJson={item.upstreamFormJson}
                    {...item}
                    pipeline={{
                        component_id: pipeline.component_id

                    }}
                    // editor={editor}
                    // updateEditor={updateEditor}
                    operatePipeline={
                        {
                            deletePipelineRelation: deletePipelineRelation,
                            openModal: openModal
                        }
                    }
                // datelePipeline={datelePipeline}
                // setPipelineStructure={setPipelineStructure}
                // setOperateOpen={setCreateOpen}
                // setPipelineRecord={setRecord}
                // openModal={openModal}
                // wrapAnalysisPipeline={wrapAnalysisPipeline}
                // downstreamAnalysis={loadFunction(downstreamAnalysis)}
                // appendSampleColumns={loadColumnRender(appendSampleColumns)}
                // parseAnalysisParams={{
                //     parse_analysis_module: parseAnalysisModule,
                //     parse_analysis_result_module: parseAnalysisResultModule
                // }}
                >
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
        const resp = await axios.get(`/get-pipeline-v2/${name}`)
        // console.log(resp.data)
        const data = resp.data
        const content = JSON.parse(data['content'])
        const pipeline = { ...data, ...content }
        setPipeline(pipeline)
        // console.log(content)
        const items = getPipline(data)
        setItems(items)
        // if (resp.data.items && Array.isArray(resp.data.items) && resp.data.items.length > 1) {
        //     const item = data.items[0]
        //     const upstreamFormList = data.items
        //         .filter((item: any) => item.upstreamFormJson && Array.isArray(item.upstreamFormJson))       // 确保 upstreamFormJson 存在并是数组
        //         .flatMap((item: any) => item.upstreamFormJson);
        //     const parseAnalysisResultModule = data.items
        //         .filter((item: any) => item.parseAnalysisResultModule && Array.isArray(item.parseAnalysisResultModule))       // 确保 upstreamFormJson 存在并是数组
        //         .flatMap((item: any) => item.parseAnalysisResultModule);
        //     const wrapPipeline = {
        //         key: 0,
        //         label: "总流程",
        //         children: <>
        //             <AnalysisPanel
        //                 wrapAnalysisPipeline={data.analysisPipline}
        //                 inputAnalysisMethod={item.inputAnalysisMethod}
        //                 analysisPipline={data.analysisPipline}
        //                 upstreamFormJson={upstreamFormList}
        //                 appendSampleColumns={loadColumnRender(item.appendSampleColumns)}
        //                 parseAnalysisParams={{
        //                     parse_analysis_module: data.parseAnalysisModule,
        //                     parse_analysis_result_module: parseAnalysisResultModule
        //                 }}
        //                 analysisType={item.analysisType ? item.analysisType : "sample"}>
        //             </AnalysisPanel>
        //             {/* {data.analysisPipline} */}
        //         </>
        //     }
        //     setItems([wrapPipeline, ...items])
        // } else {
        //     setItems(items)
        // }



    }
    const deletePipelineRelation = async (realtionId: any) => {
        try {
            const resp = await axios.delete(`/delete-pipeline-relation/${realtionId}`)
            messageApi.success("删除成功!")
            loadData()
        } catch (error: any) {
            console.log(error)
            messageApi.error(`删除失败!${error.response.data.detail}`)
        }
    }
    const datelePipeline = async (pipelineId: any) => {
        try {
            const resp = await axios.delete(`/delete-pipeline/${pipelineId}`)
            messageApi.success("删除成功!")
            loadData()
        } catch (error: any) {
            console.log(error)
            messageApi.error(`删除失败!${error.response.data.detail}`)
        }
    }
    useEffect(() => {
        loadData()
    }, [])
    return <div style={{ maxWidth: "1500px", margin: "0 auto" }}>
        {contextHolder}
        {/* {JSON.stringify(pipeline)} */}
        <Flex style={{ marginBottom: "1rem" }} justify={"space-between"} align={"center"} gap="small">
            <div >
                {pipeline ? <>
                    <h2 style={{ margin: 0 }}>{pipeline?.name}</h2>
                    <p style={{ margin: "0", color: "rgba(0, 0, 0, 0.45)" }}>{pipeline?.description}</p>
                    {import.meta.env.MODE == "development" && <>
                        <p style={{ margin: "0", color: "rgba(0, 0, 0, 0.45)" }}>{pipeline?.component_id}</p></>}

                    {pipeline.tags && Array.isArray(pipeline.tags) && pipeline.tags.map((tag: any, index: any) => (
                        <Tag style={{ marginTop: "0.5rem" }} key={index} color={colors[index]}>{tag}</Tag>
                    ))}
                </> : <Skeleton active></Skeleton>}
            </div>
            <Flex gap="small" wrap>

                <Button color="cyan" variant="solid" onClick={() => {
                    openModal("modalC", {
                        data: pipeline, structure: {
                            component_type: "pipeline",
                        }
                    })
                }}>更新流程</Button>

                <Button color="primary" variant="solid" onClick={loadData}>刷新</Button>
                <Button color="primary" variant="solid" onClick={() => navigate(`/pipeline-card`)}>返回</Button>
            </Flex>

        </Flex>

        {pipeline && Array.isArray(pipeline?.items) ? <Tabs destroyInactiveTabPane={true} items={items}></Tabs> :

            <Empty>
                <Button style={{marginRight:"0.5rem"}} color="cyan" variant="solid" onClick={() => {
                    openModal("modalC", {
                        data: undefined, structure: {
                            component_type: "software",
                            relation_type: "pipeline_software",
                            parent_component_id: pipeline.component_id,
                            pipeline_id: pipeline.component_id
                        }
                    })
                }}>新增软件</Button>
                <Button color="cyan" variant="solid" onClick={() => {
                    openModal("modalA", {
                        data: undefined, pipelineStructure: {
                            relation_type: "pipeline_software",
                            parent_component_id: pipeline.component_id,
                            pipeline_id: pipeline.component_id

                        }
                    })
                }}>添加软件</Button>
            </Empty>}

        {/* {
                pipeline_type: "wrap_pipeline",
                parent_pipeline_id: "0"

            } */}
        <ModuleEdit
            visible={modal.key == "modalB" && modal.visible}
            onClose={closeModal}
            callback={loadData}
            params={modal.params}
        >
        </ModuleEdit>
        <CreateORUpdatePipelineCompnentRelation
            callback={loadData}
            // pipelineStructure={pipelineStructure}
            // data={record}
            visible={modal.key == "modalA" && modal.visible}
            onClose={closeModal}
            params={modal.params}></CreateORUpdatePipelineCompnentRelation>
        <CreateOrUpdatePipelineComponent
            callback={loadData}
            // pipelineStructure={pipelineStructure}
            // data={record}
            visible={modal.key == "modalC" && modal.visible}
            onClose={closeModal}
            params={modal.params}></CreateOrUpdatePipelineComponent>

    </div>
}


export default Pipeline
