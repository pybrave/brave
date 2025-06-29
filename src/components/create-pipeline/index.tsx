import { Collapse, Form, Input, Modal, Select, Typography } from "antd"
import TextArea from "antd/es/input/TextArea"
import axios from "axios"
import { FC, use, useEffect, useState } from "react"

export const CreateORUpdatePipelineCompnentRelation: FC<any> = ({ visible, onClose,params, callback }) => {
    if (!visible) return null;
    
    const { data, pipelineStructure} = params
    const [form] = Form.useForm()
    const [pipeline, setPipeline] = useState<any>()
    const [pipelineRelation, setPipelineRelation] = useState<any>()

    const [loading, setLoaidng] = useState<any>(false)
    const componentMap: any = {
        wrap_pipeline: WrapPipeline,
        pipeline: WrapPipeline,
        software: TextAreaContent,
        input_analysis_method:TextAreaContent,
        analysis_method:TextAreaContent,
        downstream_analysis:TextAreaContent
    }
    const ComponentsRender = ({ relation_type, data, form }: any) => {
        const Component = componentMap[relation_type] || (() => <div>未知类型 {JSON.stringify(data)}</div>);
        return <Component data={data} form={form}></Component>
    }
    
    const getPipeleineRelation = async (relationId: any) => {
        const resp = await axios.post(`/find-pipeline-relation/${relationId}`)

        const data = resp.data
        setPipelineRelation(data)
        form.setFieldsValue(data)
    }
    const getPipeleine = async (componentId: any) => {
        const resp = await axios.post("/find-pipeline", { component_id: componentId })

        const data = resp.data
        data['content'] = JSON.parse(data['content']) //JSON.stringify(JSON.parse(data['content']), null, 2)
        setPipeline(data)
        // form.setFieldsValue(data)
    }

    useEffect(() => {

        if (visible) {
            if (data) {
                getPipeleineRelation(data.relation_id)
            } else {
                form.resetFields()
            }
        }

    }, [visible])
    const getParams = (values: any) => {
        const params = {
            ...values,
            ...pipelineStructure,

        }
        if(data){
            params['relation_id'] = pipelineRelation.relation_id
            params['parent_component_id'] = pipelineRelation.parent_component_id
            params['pipeline_id'] = pipelineRelation.pipeline_id

        
        }
        // if (data) {
        //     params['parent_component_id'] =data.componemt_id
        //     params['pipeline_id'] =data.pipeline_id
        // }

        return params
    }
    const savePipeline = async () => {
        setLoaidng(true)
        const values = await form.validateFields()
        const params = getParams(values)
        if (typeof params['content'] != 'string') {
            params['content'] = JSON.stringify(params['content'])
        }

        console.log(params)
        const resp = await axios.post("/save-pipeline-relation", params)
        console.log(resp)
        setLoaidng(false)
        if (callback) {
            callback()
        }
        onClose()
    }
    return <>
        <Modal
            loading={loading}
            title={`${data ? "更新" : "新增"}流程(${pipelineStructure?.pipeline_type})`}
            okText={data ? "更新" : "新增"}
            onOk={savePipeline}
            open={visible}
            onClose={() => onClose()}
            onCancel={() => onClose()}>
            <Form form={form}>

                <ComponentsRender {...pipelineStructure} data={pipeline} form={form}></ComponentsRender>
                <Collapse ghost items={[
                    {
                        key: "1",
                        label: "更多",
                        children: <>
                            <Form.Item noStyle shouldUpdate>
                                {() => (
                                    <Typography>
                                        <pre>{JSON.stringify(getParams(form.getFieldsValue()), null, 2)}</pre>
                                    </Typography>
                                )}
                            </Form.Item>
                        </>
                    }
                ]} />

            </Form>

        </Modal>
    </>
}

export const CreateOrUpdatePipelineComponent: FC<any> = ({ visible, onClose,params, callback }) => {
    if (!visible) return null;
    
    const { data, structure} = params
    const [form] = Form.useForm()
    const [component, setComponent] = useState<any>()

    const [loading, setLoaidng] = useState<any>(false)
    const componentMap: any = {
        pipeline: WrapPipeline,
        // pipeline: WrapPipeline,
        software: TextAreaContent,
        input_analysis_method:TextAreaContent,
        analysis_method:TextAreaContent,
        downstream_analysis:TextAreaContent
    }
    const ComponentsRender = ({ component_type, data, form }: any) => {
        const Component = componentMap[component_type] || (() => <div>未知类型 {JSON.stringify(data)}</div>);
        return <Component data={data} form={form}></Component>
    }
    
 
    const getPipeleine = async (componentId: any) => {
        const resp = await axios.post("/find-pipeline", { component_id: componentId })

        const data = resp.data
        data['content'] = JSON.parse(data['content']) //JSON.stringify(JSON.parse(data['content']), null, 2)
        setComponent(data)
        form.setFieldsValue(data)
    }

    useEffect(() => {

        if (visible) {
            if (data) {
                getPipeleine(data.component_id)
            } else {
                form.resetFields()
            }
        }

    }, [visible])
    const getParams = (values: any) => {
        const params = {
            ...values,
            ...structure,

        }
        if(data){
            // params['relation_id'] = pipelineRelation.relation_id
            // params['parent_component_id'] = pipelineRelation.parent_component_id
            params['component_id'] = component.component_id

        
        }
     

        return params
    }
    const savePipeline = async () => {
        setLoaidng(true)
        const values = await form.validateFields()
        const params = getParams(values)
        if (typeof params['content'] != 'string') {
            params['content'] = JSON.stringify(params['content'])
        }

        console.log(params)
        const resp = await axios.post("/save-pipeline", params)
        console.log(resp)
        setLoaidng(false)
        if (callback) {
            callback()
        }
        onClose()
    }
    return <>
        <Modal
            loading={loading}
            title={`${data ? "更新" : "新增"}流程(${structure?.component_type})`}
            okText={data ? "更新" : "新增"}
            onOk={savePipeline}
            open={visible}
            onClose={() => onClose()}
            onCancel={() => onClose()}>
            <Form form={form}>
                <ComponentsRender {...structure} data={component} form={form}></ComponentsRender>
                <Collapse ghost items={[
                    {
                        key: "1",
                        label: "更多",
                        children: <>
                            <Form.Item noStyle shouldUpdate>
                                {() => (
                                    <Typography>
                                        <pre>{JSON.stringify(getParams(form.getFieldsValue()), null, 2)}</pre>
                                    </Typography>
                                )}
                            </Form.Item>
                        </>
                    }
                ]} />

            </Form>

        </Modal>
    </>
}
export default CreateORUpdatePipelineCompnentRelation
const TextAreaContent: FC<any> = ({ data, form }) => {
    return <>
        {/* <Form.Item name={"content"} label="content">
            <TextAreaComp></TextAreaComp>
        </Form.Item> */}
        <Form.Item name={"component_id"} label="component_id">
            <Input></Input>
        </Form.Item>
    </>
}
const TextAreaComp:FC<any> = ({value,onChange})=>{
    const [data,setData] = useState<any>(JSON.stringify(value))
    // useEffect(()=>{
    //     setData(JSON.stringify(value))
    // },[value])
    return <>
          <TextArea value={data} onChange={(e:any)=>{
            setData(e.target.value)
            onChange(e.target.value)
            // console.log(e.target.value)
          }}></TextArea>
    </>
}

const WrapPipeline: FC<any> = ({ data, form }) => {
    // "content": {
    //     "name": "test",
    //     "analysisPipline": "reads-alignment-based-abundance-analysis",
    //     "parseAnalysisModule": "reads-alignment-based-abundance-analysis",
    //     "parseAnalysisResultModule": [
    //       {
    //         "module": "bowtie2_align",
    //         "dir": "bowtie2_align_metaphlan",
    //         "analysisMethod": "bowtie2_align_metaphlan"
    //       }
    //     ],
    //     "description": "使用reads基于marker gene的丰度分析",
    //     "tags": [
    //       "metaphlan",
    //       "bowtie2",
    //       "Alignment-based strategies"
    //     ],
    //     "img": "pipeline.jpg",
    //     "category": "metagenomics",
    //     "order": 1
    //   }
    return <>
        {/* <Form.Item name={"pipeline_key"} label="pipeline_key">
            <Input disabled={data ? true : false}></Input>
        </Form.Item> */}
        <Form.Item name={["content", "name"]} label="name">
            <Input></Input>
        </Form.Item>
        <Form.Item name={["content", "analysisPipline"]} label="analysisPipline">
            <Input></Input>
        </Form.Item>
        <Form.Item name={["content", "parseAnalysisModule"]} label="parseAnalysisModule">
            <Input></Input>
        </Form.Item>
        <Form.Item name={["content", "img"]} label="img">
            <Input></Input>
        </Form.Item>
        <Form.Item name={["content", "category"]} label="category">
            <Input></Input>
        </Form.Item>
        <Form.Item name={["content", "tags"]} label="tags">
            <Select
                mode="tags"
                style={{ width: '100%' }}
            />
        </Form.Item>
        <Form.Item name={["content", "description"]} label="description">
            <TextArea></TextArea>
        </Form.Item>
        {/* <Typography>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </Typography> */}
        {/* <Form.Item name={"content"} label="content">
            <TextArea rows={10}></TextArea>
        </Form.Item> */}
        {/* <Form.Item name={"content"} label="content">
            <TextArea rows={10}></TextArea>
        </Form.Item> */}
        {/* {JSON.stringify(data)} */}
    </>
}