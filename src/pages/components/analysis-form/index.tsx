import { Form, Input, Select } from "antd";
import axios from "axios";
import { FC, useEffect, useState } from "react";
import { useParams } from "react-router";
import AnalysisResultInput from "../analysis-result-input";

export const AnalysisForm: FC<any> = ({ form,children }) => {

    const { project,sampleComposition } = useParams()
    const [groups, setGroups] = useState<any>([])
    const columnName = Form.useWatch('column', form);
    // console.log(columnName)
    const getGroup = async () => {
        const resp: any = await axios.get(`/api/get-group?column=${columnName}&project=${project}&sample_composition=${sampleComposition}`)

        const groups = resp.data.map((it: any) => {
            return {
                label: `${it.group_name}(${it.count})`,
                value: it.group_name
            }
        })
        console.log(groups)
        setGroups(groups)
    }
    useEffect(() => {
        if (columnName) {
            getGroup()
        }
        // const a= {
        //     "args":{
        //         "column":["host_disease"],
        //          "control":["SCZ"],
        //          "treatment":["HC"],
        //          "project":["project"],
        //         "rnak":["rnak"]
        //     }
        // }
        // console.log(JSON.stringify(a))
    }, [columnName])
    const formId = Form.useWatch((values:any) => values.id, form);

    return <>
        <Form form={form}>
    
            <Form.Item label="分析id" name={"id"} style={{display:"none"}} >
                <Input></Input>
            </Form.Item>
            <Form.Item label="分析名称"  name={"analysisName"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Input></Input>
            </Form.Item>
            <Form.Item initialValue={"metaphlan"} name="software" label="分析软件" rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Select allowClear options={[
                    {
                        label: "metaphlan",
                        value: "metaphlan"
                    }, {
                        label: "kraken",
                        value: "kraken"
                    }
                ]} ></Select>
            </Form.Item>
            <Form.Item initialValue={"sample_group"} name="column" label="分组列" rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Select allowClear options={[
                    {
                        label: "sample_composition",
                        value: "sample_composition"
                    }, {
                        label: "host_disease",
                        value: "host_disease"
                    }, {
                        label: "sample_group",
                        value: "sample_group"
                    }
                ]} ></Select>
            </Form.Item>

            <Form.Item label="处理组" name={"treatment"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Select allowClear options={groups}></Select>
            </Form.Item>
            <Form.Item label="对照组" name={"control"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Select allowClear options={groups}></Select>
            </Form.Item>
            <Form.Item initialValue={"SPECIES"} label="rank" name={"rank"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Select allowClear options={[
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
                ]}></Select>
            </Form.Item>
            {children}
        </Form>
        {formId?<>
            <a onClick={()=>form.setFieldValue("id",undefined)}>更新</a>
            <a onClick={()=>form.resetFields()}>清除</a>
            </>:<>新增</>}
        {/* <Button onClick={async () => {
            const values = await form.validateFields()
            console.log(values)
        }}>
            提交
        </Button> */}
    </>
}
export const AnalysisForm2: FC<any> = ({ form }) => {

    const { project,sampleComposition } = useParams()
    const [groups, setGroups] = useState<any>([])
    const columnName = Form.useWatch('column', form);
    // console.log(columnName)
    const getGroup = async () => {
        const resp: any = await axios.get(`/api/get-group?column=${columnName}&project=${project}&sample_composition=${sampleComposition}`)

        const groups = resp.data.map((it: any) => {
            return {
                label: `${it.group_name}(${it.count})`,
                value: it.group_name
            }
        })
        console.log(groups)
        setGroups(groups)
    }
    useEffect(() => {
        if (columnName) {
            // getGroup()
        }
        // const a= {
        //     "args":{
        //         "column":["host_disease"],
        //          "control":["SCZ"],
        //          "treatment":["HC"],
        //          "project":["project"],
        //         "rnak":["rnak"]
        //     }
        // }
        // console.log(JSON.stringify(a))
    }, [columnName])
    const formId = Form.useWatch((values:any) => values.id, form);

    return <>
        <Form form={form}>
          
            <Form.Item label="分析id" name={"id"} style={{display:"none"}} >
                <Input></Input>
            </Form.Item>
            <Form.Item label="分析名称" name={"analysisName"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Input></Input>
            </Form.Item>
            <Form.Item initialValue={"SPECIES"} label="rank" name={"rank"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Select allowClear options={[
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
                ]}></Select>
            </Form.Item>
            <Form.Item name={"params"} label="params" rules={[{ required: true, message: '该字段不能为空!' }]}>
                <AnalysisResultInput></AnalysisResultInput>
            </Form.Item>
           
        </Form>
        {formId?<>
            <a onClick={()=>form.setFieldValue("id",undefined)}>更新</a>
            <a onClick={()=>form.resetFields()}>清除</a>
            </>:<>新增</>}
        {/* <Button onClick={async () => {
            const values = await form.validateFields()
            console.log(values)
        }}>
            提交
        </Button> */}
    </>
}

export default AnalysisForm