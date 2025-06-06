import { Button, Form, InputNumber } from "antd"
import { FC, useState } from "react"
import { formatUrl } from '@/utils/utils'
const Breseq: FC<any> = ({ plot }) => {
    const [url, setUrl] = useState<any>()
    return <>
           <Button onClick={() => {
                 plot({
                     moduleName: "breseq_statistic",
                     params: { "file_path": "/ssd1/wy/workspace2/leipu/leipu_workspace2/output/breseq/OSP-6/data/OSP-6.count" },
                     formDom: <>
                         <Form.Item label="REGION_START " name={"REGION_START"} initialValue={1000}>
                             <InputNumber ></InputNumber >
                         </Form.Item>
                         <Form.Item label="REGION_END " name={"REGION_END"} initialValue={10000}>
                             <InputNumber ></InputNumber >
                         </Form.Item>
                     </>
     
                 })
                 // setFormItem(<>
                 // <Form.Item label="REGION_START " name={"REGION_START"} initialValue={1000}>
                 //     <InputNumber ></InputNumber >
                 // </Form.Item>
                 // <Form.Item label="REGION_END " name={"REGION_END"} initialValue={10000}>
                 //     <InputNumber ></InputNumber >
                 // </Form.Item>
                 //     <Button onClick={() => {
     
     
                 //     }}>执行</Button>
                 // </>)
             }}> Circos plot of  mutations</Button >
    </>
}

export default Breseq