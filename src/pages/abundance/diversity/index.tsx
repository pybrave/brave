import { FC, useEffect, useState } from "react"
import axios from "axios"
import { Button, Col, Drawer, Input, Row, Space, Table, TableProps, Image, Form, Select, Spin, Modal, Tabs } from "antd"
import { useParams } from "react-router"
import ResultList from '@/components/result-list'
import AnalysisForm from "../../../components/analysis-form-bak"


const AbundanceOpterature: FC<any> = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<any>()
    const { project } = useParams()
    const [boxplotModal, setBoxplotModal] = useState(false)
    const [taxonomy, setTaxonomy] = useState("")
    const [boxplot, setBoxplot] = useState("")
    const [boxplotLoading, setBoxplotLoading] = useState(false)

    const { Search } = Input;

    const getCompareAbundance = async () => {
        const values = await form.validateFields()
        console.log(values)
        setLoading(true)
        const resp: any = await axios.post(`/jupyter/abundance-diversity`, {
            ...values,
            project: project,
            // rnak:"SPECIES",

        })

        setData(resp.data)
        setLoading(false)
        console.log(resp)
    }
 


    return <>
        <Row>
            <Col lg={12} sm={24} xs={24}>
            <AnalysisForm form={form}></AnalysisForm>                
            <Button onClick={getCompareAbundance}>提交</Button>
                {/* <Abundance /> */}
                <ResultList analysisMethod={"diversity-alpha"} shouldTrigger={true} form={form} setTableLoading={setLoading} setTabletData={(data:any)=>{
                    // console.log(data)
                    setData(data)
                }}  ></ResultList>
            </Col>
            <Col lg={12} sm={24} xs={24}>
                <Spin spinning={loading} tip="正在计算中..." >
                    {data ? <>
                        <Tabs items={[
                            {
                                key: "roc",
                                label: "roc",
                                children: <Image width={"100%"} src={data?.img}></Image>
                            }, 
                        ]}></Tabs>


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

