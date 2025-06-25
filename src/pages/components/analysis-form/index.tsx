import { Button, Collapse, Form, Input, message, Select, Typography } from "antd";
import axios from "axios";
import { FC, useEffect, useState } from "react";
import FormJsonComp from "../form-components";
import { listAnalysisResult } from '@/api/analysis-result'

export const AnalysisForm: FC<any> = ({
    form,
    resultTableList,
    // activeTabKey,
    formJson,
    formDom,
    moduleName,
    params,
    sampleGroupApI,
    setPlotLoading,
    inputAnalysisMethod,
    saveAnalysisMethod,
    project,
    setFilePlot,
    plotReloadTable,
    name
}) => {
    const formId = Form.useWatch((values: any) => values?.id, form);
    const is_save_analysis_result = Form.useWatch((values: any) => values?.is_save_analysis_result, form);
    const [sampleGroup, setSampleGroup] = useState<any>([])
    const [tableType, setTableType] = useState<any>("xlsx")
    const [imgType, setImgType] = useState<any>("pdf")

    const [messageApi, contextHolder] = message.useMessage();

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

    // const getData = async (inputAnalysisMethod:any)=>{
    // }

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
            label: "样本分组名称",
            value: "sample_group_name"
        }, {
            label: "样本来源",
            value: "sample_source"
        }, {
            label: "宿主疾病",
            value: "host_disease"
        }
    ]
    const dataMap_ = {
        // "sample_group_list": sampleGroup,
        "first_data_key": undefined,
        "rank": rank,
        group_field: group_field
    }
    const [dataMap, setDataMap] = useState<any>(dataMap_)


    const runPlot = async ({ moduleName, params }: any) => {
        const values = await form.validateFields()
        console.log(values)
        setPlotLoading(true)

        const downstreamInput = {
            inputAnalysisMenthod: inputAnalysisMethod,
            moduleName: moduleName,
            params: params
            // analysisMethod:saveAnalysisMethod
        }
        // console.log(downstreamInput)

        try {
            const reqParams = {
                ...params,
                ...values,
                project: project,
                analysis_method: saveAnalysisMethod,
                table_type: tableType,
                imgType: imgType,
                ...downstreamInput,
                software: "python"
            }
            // console.log(reqParams)
            const resp: any = await axios.post(`/fast-api/file-parse-plot/${moduleName}`, reqParams)
            setFilePlot(resp.data)
            if (plotReloadTable && values.is_save_analysis_result) {
                plotReloadTable()
            }
        } catch (error: any) {
            console.log(error)
            if (error.response?.data) {
                messageApi.error(error.response.data.detail)
            }
        }

        setPlotLoading(false)
        // console.log(resp.data);
    }
    useEffect(() => {
        if (name) {
            form.setFieldValue("analysis_name", name)
        }
    }, [name])
    const getFirstKey = (resultTableList: any) => {
        if (resultTableList && Object.keys(resultTableList).length == 1) {
            return Object.keys(resultTableList)[0]
        } else {
            return undefined
        }
    }
    const loadData = async (analysisMetnodNames:any) => {
      
        const data = await listAnalysisResult({ project: project, analysisMethodValues:analysisMetnodNames })
        const groupedData = data.reduce((acc: any, item: any) => {
            const key = item.analysis_method;
            // const key = keyMap[item.analysis_method]
            if (!acc[key]) {
                acc[key] = [];
            }
            const { sample_key, id, sample_group, ...rest } = item
            // debugger
            acc[key].push({
                label: sample_key,
                value: id,
                sample_group: sample_group ? sample_group : "no_group",
                sample_key: sample_key,
                id: id,
                // "aaa":"1111",
                ...rest
            });
            return acc;
        }, {});
        // console.log(groupedData)
        const result = { ...dataMap_, ...resultTableList, ...groupedData,first_data_key: getFirstKey(resultTableList) }
        console.log(result)
        setDataMap(result)

    }
    useEffect(() => {
        console.log(resultTableList)
        if (sampleGroupApI) {
            getSampleGroup()
        } else {
            // if (resultTableList && activeTabKey) {

            //     const resultTable = resultTableList[activeTabKey]
            //     if (resultTable) {
            //         setSampleGroup(resultTable)
            //     }
            // } else {
            //     // setSampleGroup(resultTableList)
            //     setDataMap({...dataMap_,...resultTableList})
            // }  
            // debugger
            const analysisMetnodNames = formJson??[]
                .filter((item: any) => item.inputAnalysisMethod !== undefined)
                .map((item: any) => item.inputAnalysisMethod);
            if (analysisMetnodNames.length != 0) {
                loadData(analysisMetnodNames)
            } else {
                setDataMap({ ...dataMap_, ...resultTableList, first_data_key: getFirstKey(resultTableList) })

            }
            // console.log(analysisMetnodNames)


        }

    }, [JSON.stringify(resultTableList)])
    return <>
        {contextHolder}
        <Form form={form}   >
            <Form.Item name={"id"} style={{ display: "none" }}>
                <Input></Input>
            </Form.Item>
            {/* {sampleSelectComp && resultTableList && analysisMethod.map((it: any, index: any) => (<div key={index}>
                <Form.Item key={it.name} label={it.label} name={it.name}>
                    <SelectComp it={it} resultTableList={resultTableList} ></SelectComp>
                </Form.Item>
            </div>))} */}

            <Form.Item initialValue={false} name={"is_save_analysis_result"} label={"是否保存分析结果"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Select options={[
                    {
                        label: "保存",
                        value: true
                    }, {
                        label: "不保存",
                        value: false
                    }
                ]}></Select>
            </Form.Item>
            {is_save_analysis_result &&
                <Form.Item label="分析名称" name={"analysis_name"} style={{ maxWidth: 600 }} rules={[{ required: true, message: '该字段不能为空!' }]}>
                    <Input></Input>
                </Form.Item>}


            {formJson &&
                <FormJsonComp project={project} formJson={formJson} dataMap={dataMap}></FormJsonComp>
            }

            {formDom &&
                <>
                    {formDom}
                </>
            }


            {(formDom || sampleGroup || formJson) && <>
                <Button type="primary" onClick={() => {
                    runPlot({ moduleName: moduleName, params: params })
                }}>{formId ? <>更新</> : is_save_analysis_result ? <>运行并保存</> : <>运行</>}</Button>
                {formId && <Button type="primary" onClick={() => form.setFieldValue("id", undefined)}>取消更新</Button>}

                {/* <Button type="primary" onClick={() => {
                                            runPlot({ moduleName: moduleName, params: params })
                                        }}>执行</Button> */}


            </>
            }

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
        </Form>
    </>
}

export default AnalysisForm