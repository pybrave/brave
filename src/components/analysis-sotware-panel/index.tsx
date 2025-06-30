import { FC, memo, useEffect, useMemo, useRef, useState } from "react"
import axios from "axios"
import { Button, Col, Drawer, Input, Row, Space, Table, TableProps, Image, Form, Select, Spin, Modal, Tabs, Typography, message, Empty, Collapse, Card, Popover, Flex, Popconfirm } from "antd"
import { useOutletContext, useParams } from "react-router"
import ResultList from '@/components/result-list'
// import AnalysisForm from "../analysis-form"
import SampleAnalysisResult from '../sample-analysis-result'
import React from "react"

import FormJsonComp from "../form-components"
import AnalysisList from '../analysis-list'
import AnalysisResultView from '../analysis-result-view'
import { GroupSelectSampleButton, BaseSelect } from '@/components/form-components'
import AnalysisForm from '../analysis-form'
import PipelineMonitor from '@/components/pipeline-monitor'
import { listAnalysisFiles } from '@/api/analysis-software'
import { useSelector } from "react-redux"
type AnalysisFile = {
    name: string,
    label: string
}
type AnalysisSoftware = {
    inputFile: AnalysisFile[],
    outputFile: any[],
    relation_id: any,
    pipeline: any,
    pipeline_id: any,
    component_id: any,


    wrapAnalysisPipeline: any,
    analysisPipline: any,
    inputAnalysisMethod: any,
    analysisMethod: any,
    appendSampleColumns: any,
    analysisType: any,
    children: any,
    cardExtra: any,
    upstreamFormJson: any,
    downstreamAnalysis: any,
    operatePipeline: any,
}

const AnalysisSoftwarePanel: FC<AnalysisSoftware> = ({
    inputFile,
    outputFile,
    pipeline,
    wrapAnalysisPipeline,
    analysisPipline,
    inputAnalysisMethod,
    analysisMethod,
    appendSampleColumns,
    analysisType = "nonSample",
    children,
    cardExtra,
    upstreamFormJson,
    downstreamAnalysis,
    operatePipeline,
    ...rest }) => {
    const { project } = useOutletContext<any>()

    const getAnalsyisFiles = async () => {
        const analysisFileType: any = []
        analysisFileType.push({
            type: "input",
            names: inputFile.map(item => item.name)
        })
        analysisFileType.push({
            type: "output",
            names: outputFile.map(item => item.name)
        })
        console.log(analysisFileType)

        const typeMap: any = {};
        analysisFileType.forEach(({ names, ...rest }: any) => {
            names.forEach((value: any) => {
                typeMap[value] = rest;
            });
        });

        const analysisFileNames = analysisFileType.flatMap((it: any) => it.names)
        const data = await listAnalysisFiles({ project: project, analysisFileNames: analysisFileNames })
        const groupedData = data.reduce((acc: any, item: any) => {
            const analysisFileName = item.analysis_method;
            const key = typeMap[analysisFileName].type
            // if (!acc[key]) {
            //     acc[key] = [];
            // }
            if (!acc[key][analysisFileName]) {
                acc[key][analysisFileName] = [];
            }
            const { sample_key, id, sample_group, ...rest } = item
            // debugger

            acc[key][analysisFileName].push({
                label: sample_key,
                value: id,
                sample_group: sample_group ? sample_group : "no_group",
                sample_key: sample_key,
                id: id,
                ...rest
            });
            return acc;
        }, { input: {}, output: {} });
        console.log(groupedData)
        console.log(typeMap)

    }

    useEffect(() => {
        // getAnalsyisFiles()
    }, [])

    const tableRef = useRef<any>(null)
    const [record, setRecord] = useState<any>()
    // inputAnalysisMethod = [
    //     {
    //         key: "ran_seq_reads",
    //         name: "RNA测序",
    //         value: ["V1_single_genome_NGS_RNA"],
    //         mode:"multiple"
    //     }, {
    //         key: "assembly",
    //         name: "组装基因组",
    //         value: ["ngs-individual-assembly", "tgs_individual_assembly"],
    //         mode:"single"

    //     }
    // ]
    // analysisMethod = [
    //     {
    //         key: "abc",
    //         name: "V1_single_genome_NGS_RNA_name",
    //         value: ["V1_single_genome_NGS_RNA"],
    //         mode:"multiple"
    //     }
    // ]
    const checkAvailable = (analysisMethod: any) => {
        return analysisMethod && Array.isArray(analysisMethod) && analysisMethod.length > 0
    }
    return <>

        <Row>
            <Col lg={20} sm={24} xs={24}>
                {/* <AnalysisForm form={form}></AnalysisForm>                 */}
                {/* <Button onClick={getCompareAbundance}>提交</Button> */}
                {/* <Abundance /> */}
                {/* {analysisName && <SampleAnalysisResult analysisName={analysisName} shouldTrigger={true} setSampleResult={(data: any) => {
                    setSampleResult(data)
                }}></SampleAnalysisResult>} */}
                {/* {JSON.stringify(pipeline)}

                <hr />
                {JSON.stringify(rest)} */}


                <hr />

                {/* {JSON.stringify(inputFile)}
                <hr />
                {JSON.stringify(outputFile)} */}
                {import.meta.env.MODE == "development" && <>
                    <ul>
                        <li>pipeline:{pipeline.component_id}</li>
                        <li>software:{rest.component_id}</li>
                    </ul>
                </>}

                {checkAvailable(inputFile) ? <>
                    <UpstreamAnalysisInput
                        {...rest}
                        pipeline={pipeline}
                        record={record}
                        software={{
                            component_id: rest.component_id
                        }}
                        onClickItem={setRecord}
                        project={project}
                        operatePipeline={operatePipeline}
                        cardExtra={cardExtra}
                        // wrapAnalysisPipeline={wrapAnalysisPipeline}
                        upstreamFormJson={upstreamFormJson}
                        analysisPipline={analysisPipline}
                        analysisMethod={analysisMethod}
                        inputAnalysisMethod={inputFile}></UpstreamAnalysisInput>
                </> : <>
                    {/* <Flex justify="center" style={{ margin: "2rem" }}>
                        <Button color="cyan" variant="solid" onClick={() => {
                            setPipelineRecord(undefined);
                            setPipelineStructure({
                                pipeline_type: "input_analysis_method",
                                parent_pipeline_id: rest.pipeline_id
                            })
                            setOperateOpen(true)
                        }}>添加管道输入</Button>
                    </Flex> */}
                </>}
                {/* {JSON.stringify(rest)} */}

                {/* <PipelineMonitor pipelineId={rest.pipeline_id} ></PipelineMonitor> */}
                <div style={{ marginBottom: "1rem" }}></div>
                {checkAvailable(outputFile) ? <UpstreamAnalysisOutput
                    {...rest}
                    pipeline={pipeline}

                    software={{
                        pipeline_id: rest.pipeline_id,
                        component_id: rest.component_id
                    }}

                    children={children}
                    onClickItem={setRecord}
                    downstreamAnalysis={downstreamAnalysis}
                    operatePipeline={operatePipeline}
                    project={project}
                    analysisType={analysisType}
                    analysisMethod={outputFile}
                    appendSampleColumns={appendSampleColumns}></UpstreamAnalysisOutput>
                    : <>
                        {/* {wrapAnalysisPipeline != analysisPipline &&
                            <Flex justify="center" style={{ margin: "2rem" }}>
                                <Button color="cyan" variant="solid" onClick={() => {
                                    setPipelineRecord(undefined);
                                    setPipelineStructure({
                                        pipeline_type: "analysis_method",
                                        parent_pipeline_id: rest.pipeline_id
                                    })
                                    setOperateOpen(true)
                                }}>添加管道输出</Button>
                            </Flex>} */}

                    </>}



            </Col>
            <Col lg={4} sm={24} xs={24} style={{ paddingLeft: "1rem" }}>
                {wrapAnalysisPipeline != analysisPipline && <>
                    <Flex gap="small" style={{ marginBottom: "1rem", flexWrap: "wrap" }}>
                        <Button color="cyan" variant="solid" onClick={() => {
                            operatePipeline.openModal("modalA", {
                                data: undefined, pipelineStructure: {
                                    relation_type: "pipeline_software",
                                    component_type: "software",
                                    parent_component_id: pipeline.component_id,
                                    pipeline_id: pipeline.component_id

                                }
                            })
                        }}>创建子流程</Button>
                        <Button color="cyan" variant="solid" onClick={() => {
                            operatePipeline.openModal("modalA", {
                                data: rest,
                                pipelineStructure: {
                                    relation_type: "pipeline_software",
                                    component_type: "software",
                                    pipeline_id: pipeline.component_id,

                                }
                            })
                            // setPipelineStructure()
                            // setOperateOpen(true)
                            // setPipelineRecord(rest)
                        }}>更新子流程</Button>
                        <Popconfirm title="是否删除?" onConfirm={() => {
                            operatePipeline.deletePipelineRelation(rest.relation_id)
                        }}>
                            <Button color="danger" variant="solid" >删除子流程</Button>
                        </Popconfirm>
                        {/* {JSON.stringify(rest)} */}
                    </Flex>

                </>}
                <Card title={`详细信息`}>
                    {record ? <>
                        <p>
                            {`分析方法 (${record?.analysis_method})`}
                        </p>
                        <Typography >
                            <pre>{JSON.stringify(record, null, 2)}</pre>
                        </Typography>
                    </> : <Empty />}
                </Card>
            </Col >


        </Row >
    </>
}

export default AnalysisSoftwarePanel


export const UpstreamAnalysisInput: FC<any> = ({ record, pipeline, software, operatePipeline, project, markdown, analysisPipline, upstreamFormJson, inputAnalysisMethod, onClickItem, cardExtra, ...rest }) => {
    const [upstreamForm] = Form.useForm();
    const [resultTableList, setResultTableList] = useState<any>()
    const [messageApi, contextHolder] = message.useMessage();
    const [loading, setLoading] = useState<boolean>(false)
    const formId = Form.useWatch((values) => values?.id, upstreamForm);
    // const [currentAnalysisMethod, setCurrentAnalysisMethod] = useState<any>(analysisMethod[0].value[0])
    // const [currentAnalysisMethod, setCurrentAnalysisMethod] = useState<any>(analysisPipline ? analysisPipline : "")
    const [activeTabKey, setActiveTabKey] = useState<any>()
    const [currentAnalysisMethod, setCurrentAnalysisMethod] = useState<any>()

    // const {    setPipelineStructure,setOperateOpen,setPipelineRecord,datelePipeline} = operatePipeline
    const tableRef = useRef<any>(null)

    const getrRequestParams = (values: any) => {
        const requestParams = {
            ...values,
            project: project,
            // analysis_pipline: analysisPipline,
            // parse_analysis_module: rest.parse_analysis_module,
            component_id: rest.component_id,
            pipeline_id:pipeline.component_id
            // parse_analysis_result_module: rest.parseAnalysisResultModule
        }
        return requestParams
    }
    const saveUpstreamAnalysis = async () => {
        const values = await upstreamForm.validateFields()
        const requestParams = getrRequestParams(values)
        setLoading(true)
        try {
            const resp: any = await axios.post(`/fast-api/save-analysis`, requestParams)
            // setFilePlot(resp.data)
            console.log(resp)
            if (tableRef.current) {
                tableRef.current.reload()
            }

            messageApi.success("执行成功!")
        } catch (error: any) {
            console.log(error)
            if (error.response?.data) {
                messageApi.error(error.response.data.detail)
            }
        }
        setLoading(false)
        // /fast-api/save-analysis
    }
    const host_genome_index = [
        {
            label: "人类",
            value: "/data/metagenome_data/bowtie2_index/human/human38"
        }, {
            label: "小鼠",
            value: "/data/databases/mouse/bowtie2/Mus_musculus.GRCm39.dna_sm.toplevel.fa"
        }
    ]
    const dataMap: any = {
        "host_genome_index": host_genome_index
    }
    const setResultTableListHandle = (resultTableList: any) => {
        // console.log(resultTableList)
        // resultTableList[it.key].map((it: any) => {
        //     const { sample_key, id, sample_group, ...rest } = it
        //     return {
        //         label: it.sample_key,
        //         value: it.id,
        //         sample_group: it.sample_group,
        //         ...rest
        //     }
        // }
        setResultTableList(resultTableList);
    }
    return <>
        {/* {JSON.stringify(software)} */}
        {contextHolder}
        <ResultList
            pipeline={pipeline}
            software={software}
            currentAnalysisMethod={currentAnalysisMethod}
            setCurrentAnalysisMethod={setCurrentAnalysisMethod}
            operatePipeline={operatePipeline}
            relationType="software_input_file"
            cardExtra={cardExtra}
            title={`输入文件 ${inputAnalysisMethod.length > 0 ? "" : inputAnalysisMethod.map((it: any) => it.label)}`}
            activeTabKey={activeTabKey}
            setActiveTabKey={setActiveTabKey}
            shouldTrigger={true}
            analysisType={"sample"}
            analysisMethod={inputAnalysisMethod}
            setRecord={(record: any) => onClickItem(record)}
            setResultTableList={setResultTableListHandle}></ResultList>
        <div style={{ marginBottom: "1rem" }}></div>
        <Form form={upstreamForm}>
            <Form.Item name={"id"} style={{ display: "none" }}>
                <Input></Input>
            </Form.Item>
            <Collapse
                // activeKey={collapseActiveKey}
                style={{ marginTop: "1rem" }}
                // defaultActiveKey={['1']}
                size="small"
                items={[
                    {
                        key: '1',
                        label: `执行分析 (${analysisPipline})`,
                        children: <>
                            <Spin spinning={loading}>
                                {/* {JSON.stringify(rest.parseAnalysisResultModule)} */}
                                <Flex gap={"samll"} style={{ marginBottom: "1rem" }}>
                                    <Button color="cyan" variant="solid" onClick={() => {
                                        operatePipeline.openModal("modalB", {
                                            module_type: "py_parse_analysis",
                                            module_name: rest.parseAnalysisModule,
                                            pipeline_id: pipeline.component_id,
                                            module_dir: rest.moduleDir
                                        })
                                    }}>输入解析</Button>

                                    {rest.parseAnalysisResultModule && <>
                                        {rest.parseAnalysisResultModule.map((item: any, index: any) =>
                                            <Button style={{ marginLeft: "0.5rem" }} key={index} color="cyan" variant="solid" onClick={() => {
                                                operatePipeline.openModal("modalB", {
                                                    module_type: "py_parse_analysis_result",
                                                    module_name: item.module,
                                                    pipeline_id: pipeline.component_id,
                                                    module_dir: item.moduleDir
                                                })
                                            }}>输出解析({item.module})</Button>)}
                                    </>}
                                </Flex>
                                <Form.Item name={"analysis_name"} label={"分析名称"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                                    <Input></Input>
                                </Form.Item>
                                {/* {JSON.stringify(inputAnalysisMethod)} */}
                                <FormJsonComp formJson={inputAnalysisMethod} dataMap={resultTableList}></FormJsonComp>
                                {/* {resultTableList && inputAnalysisMethod.map((it: any) => (<> */}
                                {/* <Form.Item key={it.key} label={it.name} name={it.key}>
                                        <SelectComp it={it} resultTableList={resultTableList} ></SelectComp>
                                    </Form.Item> */}
                                {/* 
                                    {it.mode == "multiple" && <GroupSelectSampleButton
                                        key={it.key}
                                        label={it.name}
                                        name={it.key}
                                        rules={[{ required: true, message: '该字段不能为空!' }]}
                                        data={resultTableList[it.key] ? resultTableList[it.key] : []}
                                        groupField={"sample_group"} ></GroupSelectSampleButton>} */}


                                {/* </>))} */}
                                {upstreamFormJson &&
                                    <FormJsonComp formJson={upstreamFormJson} dataMap={dataMap}></FormJsonComp>
                                }

                                <Button type="primary" onClick={saveUpstreamAnalysis}>{formId ? <>更新分析</> : <>保存分析</>}</Button>
                                {formId && <Button onClick={() => upstreamForm.setFieldValue("id", undefined)}>取消更新</Button>}
                                {/* <hr />
                                
                                <hr /> */}
                                <Collapse ghost items={[
                                    {
                                        key: "1",
                                        label: "更多",
                                        children: <>
                                            <Form.Item noStyle shouldUpdate>
                                                {() => (
                                                    <Typography>
                                                        <pre>{JSON.stringify(getrRequestParams(upstreamForm.getFieldsValue()), null, 2)}</pre>
                                                    </Typography>
                                                )}
                                            </Form.Item>
                                        </>
                                    }
                                ]} />


                                <AnalysisList
                                    project={project}
                                    ref={tableRef}
                                    shouldTrigger={true}
                                    analysisMethod={analysisPipline}
                                    setRecord={(record: any) => {
                                        const param = JSON.parse(record.request_param)
                                        console.log(param)
                                        upstreamForm.resetFields()
                                        upstreamForm.setFieldsValue(param)
                                        if (record?.id) {
                                            upstreamForm.setFieldValue("id", record?.id)
                                        }
                                        record['dataType'] = "analysis"
                                        onClickItem(record)
                                    }}></AnalysisList>

                                {/* {record && record.dataType == 'analysis' && <PipelineMonitor analysisId={record.analysis_id} ></PipelineMonitor>} */}

                        
                                {/* {markdown} */}
                                <AnalysisResultView
                                    plotLoading={false}
                                    markdown={markdown}></AnalysisResultView>
                                {/* <Literature params={{
                                    obj_key: analysisPipline,
                                    obj_type: "analysis_img"
                                }}></Literature> */}
                            </Spin>

                        </>
                    },
                    // {
                    //     key: "2",
                    //     label: `分析记录 (${analysisPipline})`,
                    //     children: <>
                    //         <Spin spinning={loading}>
                    //             {currentAnalysisMethod}

                    //         </Spin>

                    //     </>
                    // }
                ]}
            >
            </Collapse>

        </Form>
        <div style={{ marginBottom: "1rem" }}></div>
    </>
}

export const SelectComp: FC<any> = ({ it, resultTableList, value, onChange }) => {
    const [selectedItems, setSelectedItems] = useState<any>(value);
    const [options, setOptions] = useState<any>([]);
    const onChangeSelct = (value: any) => {
        console.log(value)
        onChange(value)
        setSelectedItems(value)
    }
    const getOptions = () => {
        return resultTableList[it.name] && resultTableList[it.name].map((it: any) => {
            return {
                label: `${it.sample_name}`,
                value: `${it.id}`
            }
        })
    }
    useEffect(() => {
        const options = getOptions()
        setOptions(options)
    }, [resultTableList])
    return <>
        <Select value={selectedItems} onChange={onChangeSelct} mode={it.mode == "multiple" ? "multiple" : undefined} allowClear options={options}></Select>
        {it.mode == "multiple" && <Button onClick={() => {
            const values = options.map((it: any) => it.value)
            // console.log(values)
            setSelectedItems(values)
            onChange(values)
        }}>选择全部{selectedItems && <>({selectedItems.length})</>}</Button>}
    </>
}




const UpstreamAnalysisOutput: FC<any> = ({ pipeline, software, operatePipeline, children, project, onClickItem, analysisType, analysisMethod, appendSampleColumns, ...rest }) => {
    const [form] = Form.useForm();

    // const [loading, setLoading] = useState(false)
    // const [data, setData] = useState<any>()
    const [record, setRecord] = useState<any>()
    const [filePlot, setFilePlot] = useState<any>()
    const [plotLoading, setPlotLoading] = useState<boolean>(false)

    const [formDom, setFormDom] = useState<any>()
    const [formJson, setFormJson] = useState<any>()

    const [sampleSelectComp, setSampleSelectComp] = useState<any>(false)

    // const [htmlUrl, setHtmlUrl_] = useState<any>()
    const { Search } = Input;
    const [messageApi, contextHolder] = message.useMessage();
    const [moduleName, setModuleName] = useState<any>()
    const [params, setParams] = useState<any>()
    // const [tableDesc, setTableDesc] = useState<any>()
    const [downstreamData, setDownstreamData] = useState<any>()

    const [resultTableList, setResultTableList] = useState<any>([])
    const [saveAnalysisMethod, setSaveAnalysisMethod] = useState<any>()
    const [collapseActiveKey, setCollapseActiveKey] = useState<any>("1")
    const [activeTabKey, setActiveTabKey] = useState<any>()
    const [currentAnalysisMethod, setCurrentAnalysisMethod] = useState<any>()

    const [sampleGroupJSON, setSampleGroupJSON] = useState<any>()
    const [btnName, setBtnName] = useState<any>()
    const [origin, setOrigin] = useState<any>(false)

    const tableRef = useRef<any>(null)


    const [sampleGroupApI, setSampleGroupApI] = useState<any>(false)



    // const getCurrentAnalysisMenthod = () => {
    //     const analysisMethodDict: any = analysisMethod.reduce((acc: any, item: any) => {
    //         acc[item.name] = item;
    //         return acc;
    //     }, {});
    //     // const analysisMethodDict = analysisMethidtoDict(analysisMethod)
    //     const currentAnalysisMenthod = analysisMethodDict[activeTabKey]
    //     return currentAnalysisMenthod
    // }


    // const savePlot = async ({ moduleName, params }: any) => {
    //     const values = await form.validateFields()
    //     const requestParams = {
    //         ...params,
    //         ...values,
    //         project: project,
    //         software: "python",
    //         // software: analysisMethod.filter((it: any) => it.key == activeTabKey)[0].value[0],
    //         analysis_method: saveAnalysisMethod,
    //         table_type: tableType
    //     }
    //     console.log(requestParams)
    //     setPlotLoading(true)
    //     try {
    //         const resp: any = await axios.post(`/fast-api/file-save-parse-plot/${moduleName}`, requestParams)
    //         setFilePlot(resp.data)
    //         if (tableRef.current) {
    //             tableRef.current.reload()

    //         }
    //         messageApi.success("执行成功!")
    //     } catch (error: any) {
    //         console.log(error)
    //         if (error.response?.data) {
    //             messageApi.error(error.response.data.detail)
    //         }

    //     }

    //     setPlotLoading(false)
    //     // console.log(resp.data);
    // }
    // const stableSampleGroup = useMemo(() => sampleGroup, [JSON.stringify(sampleGroup)]);

    // // 保证 groupField 稳定（通常是字符串，如果来源稳定可省略）
    // const stableGroupField = useMemo(() => groupField, groupField);


    const plot = async ({ name, origin = false, url, moduleName, params, paramsFun, formDom, formJson, saveAnalysisMethod, sampleSelectComp = false, sampleGroupJSON = true, sampleGroupApI = false, ...rest }: any) => {
        cleanDom()
        setCollapseActiveKey("1")
        setDownstreamData({ ...rest, moduleName: moduleName })
        setFormDom(formDom)
        setModuleName(moduleName)
        setParams(params)
        setSampleGroupApI(sampleGroupApI)
        setFilePlot(undefined)
        setOrigin(origin)
        form.resetFields()
        setBtnName(name)
        setFormJson(formJson)
        setSampleSelectComp(sampleSelectComp)
        setSampleGroupJSON(sampleGroupJSON)
        // debugger
        if (paramsFun) {
            params = paramsFun(record)
            console.log(params)
            setParams(params)
        }
        // if (sampleGroupJSON) {
        //     if (sampleGroupApI) {
        //         getSampleGroup()

        //     } else {
        //         const resultTable = resultTableList[activeTabKey]
        //         if (resultTable) {
        //             setSampleGroup(resultTable)
        //         }
        //     }
        // }
        if (saveAnalysisMethod) {

            setSaveAnalysisMethod(saveAnalysisMethod)
        }
        // else {
        //     setSaveAnalysisMethod("unknown")
        // }

        // console.log(sampleSelectComp)
        if (origin) {
            const resp: any = await axios.post(`/fast-api/file-parse-plot/${moduleName}`, {
                ...params,
                is_save_analysis_result: false,
                origin: true
            })
            console.log(resp)
            setFilePlot(resp.data)
            // await runPlot({ moduleName: moduleName, params: params })
        }
        // if (url) {
        //     setHtmlUrl_(url)
        // } else {
        //     if (!formDom && !sampleSelectComp && !sampleGroupJSON && !formJson) {
        //         // await runPlot({ moduleName: moduleName, params: params })
        //     }
        // }




    }
    // console.log(downstreamAnalysis)
    // const setHtmlUrl = (url: any, tableDesc: any = undefined) => {
    //     setHtmlUrl_(url)
    //     setFormDom(undefined)
    //     setTableDesc(tableDesc)
    //     setFilePlot(undefined)
    //     setOrigin(false)
    // }
    const cleanDom = () => {
        setFormDom(undefined)
        setFilePlot(undefined)
        // setHtmlUrl(undefined)
        setDownstreamData(undefined)
        setSaveAnalysisMethod(undefined)
    }

    return <>
        {contextHolder}
        <ResultList
            pipeline={pipeline}
            software={software}
            currentAnalysisMethod={currentAnalysisMethod}
            setCurrentAnalysisMethod={setCurrentAnalysisMethod}
            operatePipeline={operatePipeline}
            relationType="software_output_file"
            title={`输出文件 ${analysisMethod.length > 0 ? "" : analysisMethod.map((it: any) => it.name)}`}
            appendSampleColumns={appendSampleColumns}
            activeTabKey={activeTabKey}
            setActiveTabKey={setActiveTabKey}
            cleanDom={cleanDom}
            analysisType={analysisType}
            analysisMethod={analysisMethod}
            shouldTrigger={true}
            form={form}
            // setTableLoading={setLoading}
            setResultTableList={setResultTableList}
            setRecord={(data: any) => { setRecord(data); onClickItem(data) }}
        // setTabletData={(data: any) => { setData(data) }}

        ></ResultList>
        <div style={{ marginBottom: "1rem" }}></div>


        {/* {JSON.stringify(currentAnalysisMethod?.downstreamAnalysis)} */}

        <div style={{ marginBottom: "1rem" }}>
            {currentAnalysisMethod?.downstreamAnalysis && currentAnalysisMethod?.downstreamAnalysis.map((item: any, index: any) => {
                const { name, analysisType, ...rest } = item
                return <span key={index}>
                    {/* {JSON.stringify(item)} */}
                    {(record && analysisType == 'one') && <>
                        {/* variant="solid" */}
                        <Button style={{ marginRight: "0.5rem" }} color="purple" variant={name == btnName ? "solid" : "filled"} onClick={() => plot({ ...rest, name: name })}>{name}({record.sample_name})</Button>
                    </>}
                    {(analysisType != 'one') && <>
                        <Button style={{ marginRight: "0.5rem" }} color="primary" variant={name == btnName ? "solid" : "filled"} onClick={() => plot({ ...rest, name: name })}>{name}</Button>
                    </>}

                </span>
            })}
            <Button color="cyan" variant="solid" onClick={() => {
                operatePipeline.openModal("modalA", {
                    data: undefined,
                    pipelineStructure: {
                        relation_type: "file_downstream",
                        pipeline_id: pipeline.component_id,
                        parent_component_id: currentAnalysisMethod.component_id,
                    }
                })

            }}>新增下游分析</Button>
        </div>


        {children && React.cloneElement(children, {
            record: record,
            // setHtmlUrl: setHtmlUrl,
            plot: plot,
            cleanDom: cleanDom,
            form: form,
            activeTabKey: activeTabKey,
            resultTableList: resultTableList,
            // sampleGroup: sampleGroup,
            // dataMap: dataMap

        })}
        <div>


            {/* <Form form={form}   >
                <Form.Item name={"id"} style={{ display: "none" }}>
                    <Input></Input>
                </Form.Item> */}
            {/* {JSON.stringify(rest)} */}
            {btnName && <>
                {/* {JSON.stringify(downstreamData)} */}
                <Collapse
                    // activeKey={collapseActiveKey}
                    style={{ marginTop: "1rem" }}
                    defaultActiveKey={['1']}
                    size="small"
                    items={[
                        {
                            key: '1',
                            label: <>执行分析{btnName ? `(${btnName})` : ""}</>,
                            children: <>
                                {!origin && <>
                                    {import.meta.env.MODE == "development" && <>
                                        <ul>
                                            <li>pipeline:{pipeline.component_id}</li>
                                            <li>software:{software.component_id}</li>
                                            <li>file:{currentAnalysisMethod?.component_id}</li>
                                            <li>downstream:{downstreamData?.component_id}</li>
                                            {JSON.stringify(downstreamData)}
                                        </ul>
                                    </>}
                                    <Tabs
                                        tabBarExtraContent={<>
                                            <Flex gap={"small"}>
                                                <Button color="cyan" variant="solid" onClick={() => {
                                                    operatePipeline.openModal("modalB", {
                                                        module_type: "py_plot",
                                                        module_name: downstreamData.moduleName,
                                                        pipeline_id: pipeline.component_id,
                                                        module_dir: downstreamData.moduleDir
                                                    })
                                                }}>查看模块</Button>
                                                <Button color="cyan" variant="solid" onClick={() => {
                                                    operatePipeline.openModal("modalA", {
                                                        data: downstreamData,
                                                        pipelineStructure: {
                                                            relation_type: "file_downstream",
                                                            pipeline_id: pipeline.component_id
                                                        }
                                                    })

                                                }}>更新</Button>
                                                <Popconfirm title="确认删除!" onConfirm={() => {
                                                    operatePipeline.deletePipelineRelation(downstreamData.relation_id)
                                                    setBtnName(undefined)
                                                }}>
                                                    <Button color="danger" variant="solid" >删除</Button>
                                                </Popconfirm>

                                            </Flex>
                                        </>}
                                        items={[
                                            {
                                                key: "1",
                                                label: "分析",
                                                children: <AnalysisForm
                                                    {...downstreamData}
                                                    pipeline={pipeline}
                                                    form={form}
                                                    resultTableList={resultTableList}
                                                    formJson={formJson}
                                                    formDom={formDom}
                                                    // activeTabKey={activeTabKey}
                                                    sampleGroupApI={sampleGroupApI}
                                                    // moduleName={moduleName}
                                                    params={params}
                                                    name={btnName}
                                                    setPlotLoading={setPlotLoading}
                                                    inputAnalysisMethod={currentAnalysisMethod}
                                                    saveAnalysisMethod={saveAnalysisMethod}
                                                    project={project}
                                                    setFilePlot={setFilePlot}
                                                    plotReloadTable={() => {
                                                        if (tableRef.current) {
                                                            tableRef.current.reload()
                                                        }
                                                    }}
                                                // runPlot={runPlot}
                                                // sampleGroup={sampleGroup}
                                                // analysisMethod={analysisMethod} 
                                                ></AnalysisForm>

                                            }, {
                                                key: "2",
                                                label: "分析结果",
                                                children: <ResultList
                                                    title="下游分析历史记录"
                                                    ref={tableRef}
                                                    analysisType={"analysisResult"}
                                                    analysisMethod={[
                                                        {
                                                            name: saveAnalysisMethod,
                                                            label: saveAnalysisMethod,
                                                            inputKey: [saveAnalysisMethod],
                                                            mode: "multiple"
                                                        }
                                                    ]}
                                                    form={form}
                                                    setTableLoading={setPlotLoading}
                                                    // setRecord={(data: any) => {  onClickItem(data) }}
                                                    setTabletData={(data: any) => {
                                                        setFilePlot(data)
                                                    }}  ></ResultList>
                                            }
                                        ]}></Tabs>



                                </>}


                                <AnalysisResultView
                                    plotLoading={plotLoading}
                                    filePlot={filePlot}
                                    {...downstreamData}></AnalysisResultView>

                            </>

                        },
                        // {
                        //     key: '2', label: `保存分析结果(${saveAnalysisMethod})`, children: <>
                        //         <Spin spinning={plotLoading}>
                        //             {filePlot && <>
                        //                 <hr />
                        // <Form.Item label="分析名称" name={"analysis_name"} style={{ maxWidth: 600 }}>
                        //     <Input></Input>
                        // </Form.Item>
                        // <Button type="primary" onClick={() => {
                        //     savePlot({ moduleName: moduleName, params: params })
                        // }}>{formId ? <>更新</> : <>保存</>}</Button>
                        // {formId && <Button type="primary" onClick={() => form.setFieldValue("id", undefined)}>取消更新</Button>}



                        //                 <hr />
                        //             </>}




                        //         </Spin>

                        //     </>
                        // }
                    ]}
                />
            </>}


            {/* </Form> */}
        </div>

    </>
}

