import { useRef, useState } from "react"
import ResultList from "../components/result-list"
import { Button, Card, Drawer, Flex, Form, Radio, RadioChangeEvent, Spin } from "antd"
import AnalysisResultView from '../components/analysis-result-view'
import AnalysisForm from '../components/analysis-form'
import axios from "axios"
import Literature from '../literature'
const AnalysisResult = () => {
    const tableRef = useRef<any>(null)
    const [analysisType, setAnalysisType] = useState<any>("downstream")
    const [filePlot, setFilePlot] = useState<any>()
    const [plotLoading, setPlotLoading] = useState<boolean>(false)
    const [record, setRecord] = useState<any>()
    const [requestParam, setRequestParam] = useState<any>()
    const [open, setOpen] = useState<boolean>(false)
    const [form] = Form.useForm();
    const [resultTableList, setResultTableList] = useState<any>()
    const [downstreamAnalysisJSON, setDownstreamAnalysisJSON] = useState<any>({})
    const [drawerLoading, setDrawerLoading] = useState<any>(false)
    const [analysisFormLoaing, setAnalysisFormLoaing] = useState<any>(false)

    const getDownstreamAnalysis = async (analysis_method: any) => {
        setDrawerLoading(true)
        const resp: any = await axios.get(`/find_downstream_analysis/${analysis_method}`)
        setDownstreamAnalysisJSON(resp.data)
        setDrawerLoading(false)
        // console.log(resp.data)

    }

    return <div style={{ maxWidth: "1800px", margin: "1rem auto" }}>
        <Flex style={{ marginBottom: "1rem" }} justify={"flex-end"} align={"center"} gap="small">
            <Radio.Group
                options={[
                    {
                        label: "下游分析结果",
                        value: "downstream"
                    }, {
                        label: "上游分析结果",
                        value: "upstream"
                    }
                ]}

                onChange={({ target: { value } }: RadioChangeEvent) => {
                    console.log(value)
                    setAnalysisType(value)
                }}
                value={analysisType}
                optionType="button"
                buttonStyle="solid"
            />

        </Flex>
        <ResultList
            title="下游分析历史记录"
            ref={tableRef}
            analysisType={"analysisResult"}
            params={{ analysis_type: analysisType }}
            setTableLoading={setPlotLoading}
            // analysisMethod={[
            //     // {
            //     //     name: saveAnalysisMethod,
            //     //     label: saveAnalysisMethod,
            //     //     inputKey: [saveAnalysisMethod],
            //     //     mode: "multiple"
            //     // }
            // ]}
            // setRecord={(data: any) => {  onClickItem(data) }}
            setRecord={(record: any) => {
                const requestParam = JSON.parse(record.request_param)
                console.log(requestParam)
                setRecord(record)
                setRequestParam(requestParam)
            }}
            setTabletData={(data: any) => {
                setFilePlot(data)
            }}  ></ResultList>

        <div style={{ marginBottom: "2rem" }}></div>

        {record && <>

            <Card title={`${record.analysis_method}`} extra={<>
                <Button onClick={() => {
                    setOpen(true)
                    getDownstreamAnalysis(requestParam.analysis_method)
                    form.resetFields()
                    form.setFieldsValue(requestParam)
                    if (record?.id) {
                        form.setFieldValue("id", record?.id)
                    }
                }}>重新分析</Button>
            </>}>
                <AnalysisResultView
                    plotLoading={plotLoading}
                    filePlot={filePlot}></AnalysisResultView>
            </Card>
            <hr />
            <Literature params={{
                obj_key: record.analysis_method,
                obj_type: "analysis_img"
            }}></Literature>

            <Drawer loading={drawerLoading} title={`重新分析 - ${record.analysis_name}`} open={open} onClose={() => setOpen(false)} width={"50%"}>
                <ResultList
                    title={`输出文件`}
                    // appendSampleColumns={appendSampleColumns}
                    // activeTabKey={activeTabKey}
                    // setActiveTabKey={setActiveTabKey}
                    // cleanDom={cleanDom}
                    analysisType={analysisType}
                    analysisMethod={[requestParam.inputAnalysisMenthod]}
                    shouldTrigger={true}
                    setResultTableList={setResultTableList}
                // form={form}
                // setTableLoading={setLoading}

                // setRecord={(data: any) => { setRecord(data); onClickItem(data) }}
                ></ResultList>
                <Spin spinning={analysisFormLoaing}>
                    <AnalysisForm
                        form={form}
                        resultTableList={resultTableList}
                        formJson={downstreamAnalysisJSON.formJson}
                        sampleGroupApI={false}
                        moduleName={requestParam.moduleName}
                        params={requestParam.params}
                        setPlotLoading={(val: any) => {
                            setPlotLoading(val)
                            setAnalysisFormLoaing(val)
                        }}
                        activeTabKey={requestParam.inputAnalysisMenthod.name}
                        inputAnalysisMethod={[requestParam.inputAnalysisMenthod]}
                        saveAnalysisMethod={requestParam.analysis_method}
                        project={requestParam.project}
                        setFilePlot={setFilePlot}
                        plotReloadTable={() => {
                            if (tableRef.current) {
                                tableRef.current.reload()
                            }
                        }}
                    ></AnalysisForm>
                </Spin>

            </Drawer>
        </>
        }


    </div>
}

export default AnalysisResult