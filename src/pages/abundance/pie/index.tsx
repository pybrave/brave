import { FC, useEffect, useState } from "react"
import axios from "axios"
import { Button, Col, Drawer, Input, Row, Space, Table, TableProps, Image, Form, Select, Spin, Modal, Tabs } from "antd"
import { useParams } from "react-router"
import ResultList from '@/pages/components/result-list'
import { Area, Bar, Column } from "@ant-design/plots"
import AnalysisForm from "../../components/analysis-form"


const AbundanceOpterature: FC<any> = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<any>()
    const { project } = useParams()
    const [boxplotModal, setBoxplotModal] = useState(false)
    const [taxonomy, setTaxonomy] = useState("")
    const [boxplot, setBoxplot] = useState("")
    const [boxplotLoading, setBoxplotLoading] = useState(false)
    const [shouldTrigger,setShouldTrigger] =useState(true)
    const { Search } = Input;

    const getCompareAbundance = async () => {
        const values = await form.validateFields()
        console.log(values)
        setLoading(true)
        setShouldTrigger(false)
        const resp: any = await axios.post(`/jupyter/abundance-pie`, {
            ...values,
            project: project,
            // rnak:"SPECIES",

        })

        setData(resp.data)
        setShouldTrigger(true)
        setLoading(false)
        console.log(resp)
    }
 
    return <>
        <Row>
            <Col lg={12} sm={24} xs={24}>
                <AnalysisForm form={form}></AnalysisForm>  
                <Button onClick={getCompareAbundance}>提交</Button>
                <ResultList analysisMethod={"abundance-pie"} shouldTrigger={shouldTrigger} form={form} setTableLoading={setLoading} setTabletData={(data:any)=>{
                    // console.log(data)
                    setData(data)
                }}  ></ResultList>

                {/* <Abundance /> */}
            </Col>
            <Col lg={12} sm={24} xs={24}>
                <Spin spinning={loading} tip="正在计算中..." >
              
                    {data ? <>
                        {/* <Tabs items={[
                            {
                                key: "roc",
                                label: "roc",
                                children: <Image width={"100%"} src={data?.img}></Image>
                            }, 
                        ]}></Tabs> */}
                          {/* <Area {...config2} /> */}
                         {/* <Bar {...config} /> */}
                         <Image width={"100%"} src={data?.img}></Image>
                    </> : <div style={{ height: "100px" }}></div>}
                </Spin>
            </Col >

            <Modal loading={boxplotLoading} title={taxonomy} width={"50%"} open={boxplotModal} footer={<></>} onCancel={() => setBoxplotModal(false)}>
                <Image width={"100%"} src={boxplot}></Image>
            </Modal>
        </Row >
    </>
}

export default AbundanceOpterature


