import { FC, forwardRef, useEffect, useState } from "react"
import axios from "axios"
import { Button, Col, Drawer, Input, Row, Space, Table, TableProps, Image, Form, Select, Spin, Modal, Tabs, Popover, Popconfirm, Typography, message, notification } from "antd"
import { useOutletContext, useParams } from "react-router"
import ResultList from '@/components/result-list'
import { readHdfsAPi } from '@/components/result-list'
import AnalysisResultInput from '../../../components/analysis-result-input'
import {AnalysisForm2} from '../../../components/analysis-form-bak'

const AbundanceOpterature: FC<any> = () => {
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<any>()
    const { project } = useOutletContext<any>()
    const [boxplotModal, setBoxplotModal] = useState(false)
    const [boxplotParams, setBoxplotParams] = useState({})
    // const [counter, setCounter] = useState<any>(0)
    const [vennElement, setVennElement] = useState<any>([])
    const { Search } = Input;
    const [api, contextHolder] = notification.useNotification();
    const [shouldTrigger, setShouldTrigger] = useState(true)

    const [submitForm] = Form.useForm();
    const [form] = Form.useForm();
    const submitAnalysis = async () => {
        // const values = { params: analysisParams }
        const values = await form.validateFields()
        // console.log(values)
        setLoading(true)
        setShouldTrigger(false)
        const resp: any = await axios.post(`/jupyter/abundance-unique`, {
            ...values,
            project: project,
            // rnak:"SPECIES",

        })
        setShouldTrigger(true)

        setData(resp.data)
        setLoading(false)
        // console.log(resp)
    }
    // const getCounter = () => {

    //     const counter1 = counter + 1
    //     setCounter(counter1)
    //     return counter1;
    // }




    return <>
        <Row>
            <Col lg={12} sm={24} xs={24}>
                <AnalysisForm2 form={form}></AnalysisForm2>
                <Button onClick={submitAnalysis}>提交</Button>

                {/* <Button onClick={getCompareAbundance}>提交</Button> */}
                {/* <Abundance /> */}


                <ResultList analysisMethod={"abundance-venn"} shouldTrigger={shouldTrigger} form={form} setTableLoading={setLoading} setTabletData={(data: any) => {
                    setData(data)
                    // setAnalysisParams(data.params.params)
                }}  ></ResultList>

                {/* <Typography>
                    <pre>{JSON.stringify(analysisParams, null, 2)}</pre>
                </Typography> */}


            </Col>
            <Col lg={12} sm={24} xs={24}>
                <Spin spinning={loading} tip="正在计算中..." >
                    {data ? <>
                        <Image width={"50%"} src={data?.img}></Image>

                        <table className="result-table">
                            <thead>
                                <tr>
                                    <th>binary_code</th>
                                    <th>label</th>
                                    <th>count</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.regions.map((item: any, index: any) => (<tr key={index}>
                                    <td>{item.binary_code}</td>
                                    <td>{item.label}</td>
                                    <td>{item.count}</td>
                                    <td><a onClick={() => {
                                        setVennElement(item.elements)
                                    }} style={{ whiteSpace: "nowrap" }}>查看元素</a></td>
                                    {/* <Typography>
                                    <pre>{JSON.stringify(item, null, 2)}</pre>
                                </Typography> */}
                                </tr>))}
                            </tbody>

                        </table>
                        {vennElement.length > 0 && <>
                            <table className="result-table">
                                <thead>
                                    <tr>
                                        <th>index</th>
                                        <th>name</th>

                                    </tr>
                                </thead>
                                <tbody>
                                    {vennElement.map((item: any, index: any) => (<tr key={index}>
                                        <td>{index + 1}</td>
                                        <td><a onClick={() => {
                                            setBoxplotParams({
                                                project: project,
                                                taxonomy: item.split("_")[0],
                                                column: "sample_group",
                                                rank: "SPECIES",
                                                software: "metaphlan"
                                            })
                                            setBoxplotModal(true)

                                        }}>{item}</a></td>

                                        {/* <td><a onClick={()=>{
                                            setVennElement(item.elements)
                                        }}  style={{whiteSpace: "nowrap"}}>查看元素</a></td> */}

                                    </tr>))}
                                </tbody>

                            </table>

                        </>}
                    </> : <div style={{ height: "100px" }}></div>}
                </Spin>
                <BoxplotTaxonomy boxplotParam={boxplotParams} open={boxplotModal} setOpen={setBoxplotModal}></BoxplotTaxonomy>
            </Col >

            {/* <Modal loading={boxplotLoading} title={taxonomy} width={"50%"} open={boxplotModal} footer={<></>} onCancel={() => setBoxplotModal(false)}>
                <Image width={"100%"} src={boxplot}></Image>
            </Modal> */}
        </Row >
    </>
}

export default AbundanceOpterature

// const BoxplotTaxonomy = forwardRef<any,any>(()=>{
//     return<>

//     </>
// })
const BoxplotTaxonomy: FC<any> = ({ boxplotParam, open, setOpen }) => {
    // const [taxonomy, setTaxonomy] = useState("")
    const [boxplot, setBoxplot] = useState("")
    const [boxplotLoading, setBoxplotLoading] = useState(false)
    const getBoxplot = async () => {
        // const values = await form.validateFields()
        // setTaxonomy(taxonomy)
        // console.log(boxplotParam)
        setBoxplotLoading(true)
        const resp: any = await axios.post(`/jupyter/abundance-boxplot`, {
            ...boxplotParam,
            // ...values
            // rnak:"SPECIES",
        })
        setBoxplot(resp.data)
        setBoxplotLoading(false)
    }

    useEffect(() => {
        if (open) {
            getBoxplot()
        }
    }, [open])
    return <>
        <Modal loading={boxplotLoading} title={"箱线图"} width={"50%"} open={open} footer={<></>} onCancel={() => setOpen(false)}>
            <Image width={"100%"} src={boxplot}></Image>
            <Typography>
                <pre>{JSON.stringify(boxplotParam, null, 2)}</pre>
            </Typography>
        </Modal>

    </>
}




