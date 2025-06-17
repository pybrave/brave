import { FC, memo, useEffect, useMemo, useRef, useState } from "react"
import axios from "axios"
import { Button, Col, Drawer, Input, Row, Space, Table, TableProps, Image, Form, Select, Spin, Modal, Tabs, Typography, message, Empty, Collapse, Card, Popover } from "antd"
import { useParams } from "react-router"
import ResultList from '@/pages/components/result-list'
import AnalysisForm from "../analysis-form"
import SampleAnalysisResult from '../sample-analysis-result'
import React from "react"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import AnalysisList from '../analysis-list'
import 'katex/dist/katex.min.css'
import FormJsonComp from "../form-components"
import TextArea from "antd/es/input/TextArea"
import Item from "antd/es/list/Item"
import { GroupSelectSampleButton, BaseSelect } from '@/pages/components/form-components'
const AnalysisPanel: FC<any> = ({ analysisPipline, parseAnalysisParams, inputAnalysisMethod, analysisMethod, appendSampleColumns, analysisType = "nonSample", children, cardExtra, upstreamFormJson, downstreamAnalysis }) => {

    const { project } = useParams()
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

    return <>

        <Row>
            <Col lg={20} sm={24} xs={24}>
                {/* <AnalysisForm form={form}></AnalysisForm>                 */}
                {/* <Button onClick={getCompareAbundance}>提交</Button> */}
                {/* <Abundance /> */}
                {/* {analysisName && <SampleAnalysisResult analysisName={analysisName} shouldTrigger={true} setSampleResult={(data: any) => {
                    setSampleResult(data)
                }}></SampleAnalysisResult>} */}
                {inputAnalysisMethod && <>
                    <UpstreamAnalysisInput
                        cardExtra={cardExtra}
                        upstreamFormJson={upstreamFormJson}
                        analysisPipline={analysisPipline}
                        onClickItem={setRecord}
                        project={project}
                        parseAnalysisParams={parseAnalysisParams}
                        analysisMethod={analysisMethod}
                        inputAnalysisMethod={inputAnalysisMethod}></UpstreamAnalysisInput>
                </>}
                {analysisMethod && <UpstreamAnalysisOutput
                    children={children}
                    onClickItem={setRecord}
                    downstreamAnalysis={downstreamAnalysis}
                    project={project}
                    analysisType={analysisType}
                    analysisMethod={analysisMethod}
                    appendSampleColumns={appendSampleColumns}></UpstreamAnalysisOutput>}



            </Col>
            <Col lg={4} sm={24} xs={24} style={{ paddingLeft: "1rem" }}>
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

export default AnalysisPanel


export const UpstreamAnalysisInput: FC<any> = ({ project, analysisPipline, parseAnalysisParams, upstreamFormJson, inputAnalysisMethod, onClickItem, cardExtra }) => {
    const [upstreamForm] = Form.useForm();
    const [resultTableList, setResultTableList] = useState<any>()
    const [messageApi, contextHolder] = message.useMessage();
    const [loading, setLoading] = useState<boolean>(false)
    const formId = Form.useWatch((values) => values?.id, upstreamForm);
    // const [currentAnalysisMethod, setCurrentAnalysisMethod] = useState<any>(analysisMethod[0].value[0])
    const [currentAnalysisMethod, setCurrentAnalysisMethod] = useState<any>(analysisPipline ? analysisPipline : "")
    const [activeTabKey, setActiveTabKey] = useState<any>()

    const tableRef = useRef<any>(null)

    const getrRequestParams = (values: any) => {
        const requestParams = {
            ...values,
            project: project,
            analysis_pipline: currentAnalysisMethod,
            ...parseAnalysisParams
        }
        return requestParams
    }
    const saveUpstreamAnalysis = async () => {
        const values = await upstreamForm.validateFields()
        const requestParams = getrRequestParams(values)
        console.log(requestParams)
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
        {contextHolder}
        <ResultList
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

                            </Spin>

                        </>
                    }, {
                        key: "2",
                        label: `分析记录 (${analysisPipline})`,
                        children: <>
                            <Spin spinning={loading}>
                                {currentAnalysisMethod}
                                <AnalysisList
                                    project={project}
                                    ref={tableRef}
                                    shouldTrigger={true}
                                    analysisMethod={currentAnalysisMethod}
                                    setRecord={(record: any) => {
                                        const param = JSON.parse(record.request_param)
                                        console.log(param)
                                        upstreamForm.resetFields()
                                        upstreamForm.setFieldsValue(param)
                                        if (record?.id) {
                                            upstreamForm.setFieldValue("id", record?.id)
                                        }
                                        onClickItem(record)
                                    }}></AnalysisList>
                            </Spin>

                        </>
                    }
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




const UpstreamAnalysisOutput: FC<any> = ({ children, project, onClickItem, analysisType, analysisMethod, appendSampleColumns, downstreamAnalysis }) => {
    const [form] = Form.useForm();

    // const [loading, setLoading] = useState(false)
    // const [data, setData] = useState<any>()
    const [record, setRecord] = useState<any>()
    const [filePlot, setFilePlot] = useState<any>()
    const [plotLoading, setPlotLoading] = useState<boolean>(false)

    const [formDom, setFormDom] = useState<any>()
    const [formJson, setFormJson] = useState<any>()

    const [sampleSelectComp, setSampleSelectComp] = useState<any>(false)

    const [htmlUrl, setHtmlUrl_] = useState<any>()
    const { Search } = Input;
    const [messageApi, contextHolder] = message.useMessage();
    const [moduleName, setModuleName] = useState<any>()
    const [params, setParams] = useState<any>()
    const [tableDesc, setTableDesc] = useState<any>()
    const [resultTableList, setResultTableList] = useState<any>([])
    const [saveAnalysisMethod, setSaveAnalysisMethod] = useState<any>()
    const [collapseActiveKey, setCollapseActiveKey] = useState<any>("1")
    const [activeTabKey, setActiveTabKey] = useState<any>()
    const [sampleGroup, setSampleGroup] = useState<any>([])

    const [sampleGroupJSON, setSampleGroupJSON] = useState<any>()
    const [btnName, setBtnName] = useState<any>()
    const tableRef = useRef<any>(null)
    const formId = Form.useWatch((values) => values?.id, form);
    const [tableType, setTableType] = useState<any>("xlsx")

    const getSampleGroup = async () => {
        try {
            const resp: any = await axios.post(`/fast-api/find-sample`, {
                "project": "hexiaoyan",
                "sequencing_target": "DNA",
                "sequencing_technique": "NGS",
                "sample_composition": "meta_genome"
            })
            const data = resp.data.map((it: any) => {
                return {
                    label: it.sample_key,
                    value: it.sample_key,
                    sample_group: it.sample_group,
                    sample_source: it.sample_source,
                    host_disease: it.host_disease,
                }
            })
            setSampleGroup(data)
        } catch (error: any) {
            console.log(error)
        }
    }


    const runPlot = async ({ moduleName, params }: any) => {
        const values = await form.validateFields()
        console.log(values)
        setPlotLoading(true)
        try {
            const resp: any = await axios.post(`/fast-api/file-parse-plot/${moduleName}`, {
                ...params,
                ...values,
                project: project,
                analysis_method: saveAnalysisMethod,
                table_type: tableType
            })
            setFilePlot(resp.data)

        } catch (error: any) {
            console.log(error)
            if (error.response?.data) {
                messageApi.error(error.response.data.detail)
            }
        }

        setPlotLoading(false)
        // console.log(resp.data);
    }
    const savePlot = async ({ moduleName, params }: any) => {
        const values = await form.validateFields()
        const requestParams = {
            ...params,
            ...values,
            project: project,
            software: analysisMethod.filter((it: any) => it.key == activeTabKey)[0].value[0],
            analysis_method: saveAnalysisMethod,
            table_type: tableType
        }
        console.log(requestParams)
        setPlotLoading(true)
        try {
            const resp: any = await axios.post(`/fast-api/file-save-parse-plot/${moduleName}`, requestParams)
            setFilePlot(resp.data)
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

        setPlotLoading(false)
        // console.log(resp.data);
    }
    // const stableSampleGroup = useMemo(() => sampleGroup, [JSON.stringify(sampleGroup)]);

    // // 保证 groupField 稳定（通常是字符串，如果来源稳定可省略）
    // const stableGroupField = useMemo(() => groupField, groupField);


    const plot = async ({ name, url, moduleName, params, paramsFun, formDom, formJson, tableDesc, saveAnalysisMethod, sampleSelectComp = false, sampleGroupJSON = true, sampleGroupApI = false }: any) => {
        setCollapseActiveKey("1")
        setHtmlUrl(undefined)
        setTableDesc(tableDesc)
        setFormDom(formDom)
        setModuleName(moduleName)
        setParams(params)

        setFilePlot(undefined)
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
        if (sampleGroupJSON) {
            if (sampleGroupApI) {
                getSampleGroup()

            } else {
                const resultTable = resultTableList[activeTabKey]
                // console.log(resultTableList)
                if (resultTable) {
                    // const result = resultTable.map((it: any) => {
                    //     const { sample_key, id, sample_group, ...rest } = it
                    //     return {
                    //         label: it.sample_key,
                    //         value: it.id,
                    //         sample_group: it.sample_group,
                    //         ...rest
                    //     }
                    // })


                    // console.log(result)
                    setSampleGroup(resultTable)

                }
                // console.log()
                // setSampleGroup()
            }


        }
        if (saveAnalysisMethod) {

            setSaveAnalysisMethod(saveAnalysisMethod)
        } else {
            setSaveAnalysisMethod("unknown")
        }

        // console.log(sampleSelectComp)
        if (url) {
            setHtmlUrl_(url)
        } else {
            if (!formDom && !sampleSelectComp && !sampleGroupJSON && !formJson) {
                await runPlot({ moduleName: moduleName, params: params })
            }
        }




    }
    // console.log(downstreamAnalysis)
    const setHtmlUrl = (url: any, tableDesc: any = undefined) => {
        setHtmlUrl_(url)
        setFormDom(undefined)
        setTableDesc(tableDesc)
        setFilePlot(undefined)
    }
    const cleanDom = () => {
        setFormDom(undefined)
        setFilePlot(undefined)
        setHtmlUrl(undefined)
    }
    const rank = [
        {
            label: "SGB",
            value: "SGB"
        }, {
            label: "SPECIES",
            value: "SPECIES"
        }, {
            label: "GENUS",
            value: "GENUS"
        }, {
            label: "FAMILY",
            value: "FAMILY"
        }, {
            label: "ORDER",
            value: "ORDER"
        }, {
            label: "CLASS",
            value: "CLASS"
        }, {
            label: "PHYLUM",
            value: "PHYLUM"
        },
    ]
    const group_field = [
        {
            label: "样本分组",
            value: "sample_group"
        }, {
            label: "样本来源",
            value: "sample_source"
        }, {
            label: "宿主疾病",
            value: "host_disease"
        }
    ]
    const dataMap = {
        "sample_group_list": sampleGroup,
        "rank": rank,
        group_field: group_field
    }
    return <>
        {contextHolder}
        <ResultList
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

        <div style={{ marginBottom: "1rem" }}>
            {downstreamAnalysis && downstreamAnalysis.map((item: any, index: any) => {
                const { name, analysisType, ...rest } = item
                return <span key={index}>
                    {(record && analysisType == 'one') && <>
                        <Button style={{ marginRight: "0.5rem" }} color="purple" variant="solid" onClick={() => plot({ ...rest })}>{name}({record.sample_name})</Button>
                    </>}
                    {(analysisType != 'one') && <>
                        <Button style={{ marginRight: "0.5rem" }} type="primary" onClick={() => plot({ ...rest })}>{name}</Button>
                    </>}

                </span>
            })}
        </div>


        {children && React.cloneElement(children, {
            record: record,
            setHtmlUrl: setHtmlUrl,
            plot: plot,
            cleanDom: cleanDom,
            form: form,
            activeTabKey: activeTabKey,
            resultTableList: resultTableList,
            sampleGroup: sampleGroup,
            dataMap: dataMap

        })}
        <div>
            <Form form={form}   >
                <Form.Item name={"id"} style={{ display: "none" }}>
                    <Input></Input>
                </Form.Item>
                {saveAnalysisMethod && <>

                    <Collapse
                        // activeKey={collapseActiveKey}
                        style={{ marginTop: "1rem" }}
                        defaultActiveKey={['1']}
                        size="small"
                        items={[
                            {
                                key: '1', label: <>执行分析{btnName ? `(${btnName})` : ""}</>, children: <>
                                    {sampleSelectComp && resultTableList && analysisMethod.map((it: any, index: any) => (<div key={index}>
                                        {/* {JSON.stringify(resultTableList)} */}
                                        <Form.Item key={it.name} label={it.label} name={it.name}>
                                            <SelectComp it={it} resultTableList={resultTableList} ></SelectComp>
                                        </Form.Item>
                                    </div>))}
                                    {/* {sampleGroupJSON && <>
                                        <Form.Item initialValue={"sample_group"} label="分组列" name={"group_field"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                                            <Select options={[
                                                {
                                                    label: "样本分组",
                                                    value: "sample_group"
                                                }, {
                                                    label: "样本来源",
                                                    value: "sample_source"
                                                }, {
                                                    label: "宿主疾病",
                                                    value: "host_disease"
                                                }
                                            ]} ></Select>
                                        </Form.Item>
                                      
                                    </>

                                    } */}


                                    {formJson &&
                                        <FormJsonComp formJson={formJson} dataMap={dataMap}></FormJsonComp>
                                    }

                                    {formDom &&
                                        <>
                                            {formDom}
                                        </>
                                    }

                                    {(sampleSelectComp || formDom || sampleGroup) && <>
                                        <Button type="primary" onClick={() => {
                                            runPlot({ moduleName: moduleName, params: params })
                                        }}>执行</Button>

                                        <hr />
                                    </>
                                    }




                                    <AnalysisResultView htmlUrl={htmlUrl}
                                        plotLoading={plotLoading}
                                        filePlot={filePlot}
                                        tableDesc={tableDesc}></AnalysisResultView>

                                </>

                            }, {
                                key: '2', label: `保存分析结果(${saveAnalysisMethod})`, children: <>
                                    <Spin spinning={plotLoading}>
                                        {filePlot && <>
                                            <hr />
                                            <Form.Item label="分析名称" name={"analysis_name"} style={{ maxWidth: 600 }}>
                                                <Input></Input>
                                            </Form.Item>
                                            <Button type="primary" onClick={() => {
                                                savePlot({ moduleName: moduleName, params: params })
                                            }}>{formId ? <>更新</> : <>保存</>}</Button>
                                            {formId && <Button type="primary" onClick={() => form.setFieldValue("id", undefined)}>取消更新</Button>}



                                            <hr />
                                        </>}

                                        <ResultList
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

                                        <Collapse ghost items={[
                                            {
                                                key: "1",
                                                label: "更多",
                                                children: <>
                                                    <Form.Item noStyle shouldUpdate>
                                                        {() => (
                                                            <Typography>
                                                                <pre>{JSON.stringify(form.getFieldsValue(), null, 2)}</pre>
                                                            </Typography>
                                                        )}
                                                    </Form.Item>
                                                </>
                                            }
                                        ]} />
                                    </Spin>

                                </>
                            }]}
                    />
                </>}


            </Form>
        </div>

    </>
}


export const TableView: FC<any> = ({ data, url }) => {
    const { Search } = Input;
    const [tableData, setTableData] = useState<any>([])
    const getColumns = (data: any) => {
        return Object.keys(data).map(it => {
            return {
                title: it,
                dataIndex: it,
                key: it,
                ellipsis: true,
                width: 150,
            }
        })
    }
    useEffect(() => {
        // console.log()
        if (data) {
            console.log(data)
            setTableData(data)
        }

    }, [data])
    return <>
        {Array.isArray(tableData) && <>
            <Table
                title={() => <>
                    <Search
                        placeholder="input search text"
                        allowClear
                        onSearch={(value: any) => {
                            // console.log(data?.table)
                            const filterData = data.filter((it: any) => Object.values(it).some(val =>
                                typeof val === "string" && val.includes(value)
                            ))
                            setTableData(filterData)
                        }}
                        style={{ width: 304 }}
                    />
                    
                    {url && <Popover title={`${window.location.origin}${url}`}><Button onClick={() => {
                        window.open(url, "_blank")
                    }} style={{ marginLeft: "1rem" }} type="primary">下载</Button></Popover>}
                </>}
                // showHeader={()=>{}}
                scroll={{ x: 'max-content', y: 55 * 5 }}
                dataSource={tableData}
                columns={getColumns(data[0])}
                footer={() => `一共${data.length}条记录`}
            ></Table>

        </>}

    </>
}

const AnalysisResultView: FC<any> = ({ htmlUrl, plotLoading, filePlot, tableDesc }) => {

    const componentMap: any = {
        table: TableView
    };

    const ComponentsRender = ({ type, ...rest }: any) => {
        const Component = componentMap[type] || (() => <div>未知类型 {type}</div>)
        return <Component {...rest} />;
    }
    return <>
        {htmlUrl && <>
            <iframe src={htmlUrl} width={"100%"} style={{ height: "80vh", border: "none" }}>
            </iframe>
            {/* {tableDesc && <>
                            <ReactMarkdown children={tableDesc} remarkPlugins={[remarkGfm]}></ReactMarkdown>
                        </>} */}
        </>}
        <Spin spinning={plotLoading} tip="请求中..." >
            {filePlot ? <>
                {/* {filePlot.img} */}


                {filePlot.img && <div>
                    {
                        Array.isArray(filePlot.img) ? <>
                            {filePlot.img.map((it: any) => (<>
                                <Image src={it} style={{ maxWidth: "20rem", marginRight: "0.5rem" }}></Image>
                            </>))}
                        </> :
                            <>
                                <Image src={filePlot.img} style={{ maxWidth: "20rem" }}></Image>

                            </>
                    }
                </div>}
                {filePlot.dataList && Array.isArray(filePlot.dataList) && <>
                    {filePlot.dataList.map((item: any, index: any) => (
                        <ComponentsRender key={index} {...item}></ComponentsRender>
                        // <div key={index}>
                        //     {typeof item == 'string' ?
                        //         <TextArea value={item} rows={10}></TextArea>
                        //         :
                        //         <TableView data={item}></TableView>
                        //     }
                        // </div>

                    ))}
                </>}
                {filePlot.data && Array.isArray(filePlot.data) ? <>
                    <TableView data={filePlot.data}></TableView>
                    {/* <Typography >
                                            <pre>{JSON.stringify(getColumns(filePlot.data), null, 2)}</pre>
                                        </Typography> */}



                    {/* <Typography >
                                            <pre>{JSON.stringify(filePlot.data, null, 2)}</pre>
                                        </Typography> */}

                </> : <Typography >
                    {typeof filePlot.data == 'string' ? <TextArea value={filePlot.data} rows={10}></TextArea>
                        :
                        <pre>{JSON.stringify(filePlot.data, null, 2)}</pre>
                    }

                </Typography>}


            </> : <div style={{ height: "100px" }}></div>}
        </Spin>

        {tableDesc && <>
            <Collapse ghost items={[
                {
                    key: "1",
                    label: "说明",
                    children: <>
                        <ReactMarkdown children={tableDesc} rehypePlugins={[rehypeKatex]} remarkPlugins={[remarkGfm, remarkMath]}></ReactMarkdown>

                    </>
                }
            ]} />
        </>}

    </>
}