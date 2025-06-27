import { FC, useEffect, useState } from "react"
import axios from "axios"
import { Button, Col, Drawer, Input, Row, Space, Table, TableProps, Image, Form, Select, Spin, Modal, Tabs } from "antd"
import { useOutletContext, useParams } from "react-router"
import ResultList from '@/components/result-list'
import AnalysisForm from "../../../components/analysis-form-bak"

const AbundanceOpterature: FC<any> = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<any>()
    const { project } = useOutletContext<any>()
    const [boxplotModal, setBoxplotModal] = useState(false)
    const [taxonomy, setTaxonomy] = useState("")
    const [boxplot, setBoxplot] = useState("")
    const [boxplotLoading, setBoxplotLoading] = useState(false)

    const { Search } = Input;

    const getCompareAbundance = async () => {
        const values = await form.validateFields()
        console.log(values)
        setLoading(true)
        const resp: any = await axios.post(`/jupyter/abundance-roc`, {
            ...values,
            project: project,
            // rnak:"SPECIES",

        })

        setData(resp.data)
        setLoading(false)
        console.log(resp)
    }
    const compareColumns: TableProps<any>['columns'] = [
        {
            title: 'taxonomy',
            dataIndex: 'taxonomy',
            key: 'taxonomy',
            render: (_, record) => (
                <>
                    <a href="javascript:;" onClick={() => {
                        getBoxplot(record.taxonomy)
                        setBoxplotModal(true)
                    }}>{record.taxonomy}</a>
                </>
            )
        }, {
            title: 'tax_id',
            dataIndex: 'tax_id',
            key: 'tax_id',
            render: (_, record) => (<>
                <a href={`https://www.ncbi.nlm.nih.gov/datasets/taxonomy/${record.tax_id}/`} target="__blank">{record.tax_id}</a>
            </>)
        }, {
            title: 'rank',
            dataIndex: 'rank',
            key: 'rank',
        }, {
            title: 'Importance',
            dataIndex: 'Importance',
            key: 'Importance',
        },
    ]
    const getBoxplot = async (taxonomy: any) => {
        const values = await form.validateFields()
        setTaxonomy(taxonomy)
        setBoxplotLoading(true)
        const resp: any = await axios.post(`/jupyter/abundance-boxplot`, {
            project: project,
            taxonomy: taxonomy,
            ...values
            // rnak:"SPECIES",
        })
        setBoxplot(resp.data)
        setBoxplotLoading(false)
    }

    return <>
        <Row>
            <Col lg={12} sm={24} xs={24}>
                <AnalysisForm form={form}></AnalysisForm>  
                <Button onClick={getCompareAbundance}>提交</Button>
                {/* <Abundance /> */}
                <ResultList analysisMethod={"roc"} shouldTrigger={true} form={form} setTableLoading={setLoading} setTabletData={(data:any)=>{
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
                            }, {
                                key: "importance",
                                label: "importance",
                                children: <>

                                    <Table
                                        pagination={{ pageSize: 30 }}
                                        loading={loading}
                                        scroll={{ x: 'max-content' }}
                                        columns={compareColumns}
                                        dataSource={data.importance ? data.importance : []} />
                                    <p>
                                        <ol>
                                            <li>
                                                Importance: 特征重要性反映每个特征在决策树分裂时对降低不纯度的平均贡献。权重值越大，表示该特征对分类的影响越显著。
                                            </li>
                                        </ol>
                                    </p>
                                    <p>
                                        {/* {data.importance.filter((it:any)=>it.tax_id!="").map((it:any)=>it.taxonomy).join(",")} */}
                                    </p>
                                </>

                            }
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


