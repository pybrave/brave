import { FC, useEffect, useState } from "react"
import axios from "axios"
import { Button, Col, Drawer, Input, Row, Space, Table, TableProps, Image, Form, Select, Spin, Modal, Tabs } from "antd"
import { useOutletContext, useParams } from "react-router"
import ResultList from '@/components/result-list'
import AnalysisForm from "../../../components/analysis-form-bak"


const AbundanceOpterature: FC<any> = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<any>({})
    const [table, seTable] = useState<any>([])
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
        const resp: any = await axios.post(`/jupyter/abundance-prevalence `, {
            ...values,
            project: project,
            // rnak:"SPECIES",

        })

        setData(resp.data)
        seTable(resp.data.table)
        setLoading(false)
        // console.log(resp)
    }




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
            title: 'oral_prev',
            dataIndex: 'oral_prev',
            key: 'oral_prev',
        }, {
            title: 'faeces_prev',
            dataIndex: 'faeces_prev',
            key: 'faeces_prev',
        }, {
            title: '类型',
            dataIndex: 'type',
            key: 'type',
        },
    ]
    return <>
        <Row>
            <Col lg={12} sm={24} xs={24}>
                <AnalysisForm form={form}></AnalysisForm>
                <Button onClick={getCompareAbundance}>提交</Button>
                {/* <DifferenceList form={form} setTableLoading={setLoading} setTabletData={setTabletData}  ></DifferenceList> */}
                {/* <Abundance /> */}
                <ResultList analysisMethod={"prevalence"} shouldTrigger={true} form={form} setTableLoading={setLoading} setTabletData={(data: any) => {
                    // console.log(data)
                    setData(data)
                    seTable(data.table)
                }}  ></ResultList>

                {/* {data.img && 
                     <Image width={"100%"} src={data.img}></Image>
                } */}
            </Col>
            <Col lg={12} sm={24} xs={24}>
                {/* <Spin spinning={loading} tip="正在计算中...">
                </Spin> */}

                {/* <SearchAbundance /> */}
                {data?.img && <>
                    <Image width={"50%"} src={data?.img}></Image>
                </>}
                <p>
                    {data?.desc ? data.desc : ""}
                </p>

                {/* 一共有{classifiedTaxonomy.length}条记录 */}
                <div>
                    <Search
                        placeholder="input search text"
                        allowClear
                        onSearch={(value: any) => {
                            const filterAbundance = data.table.filter((it: any) => it.type.includes(value) || it.taxonomy.includes(value))
                            seTable(filterAbundance)
                        }}
                        style={{ width: 304 }}
                    />


                </div>

                <Table
                    pagination={{ pageSize: 30 }}
                    loading={loading}
                    scroll={{ x: 'max-content', y: 55 * 5 }}
                    columns={compareColumns}
                    dataSource={table} />
            </Col>

            <Modal loading={boxplotLoading} title={taxonomy} width={"50%"} open={boxplotModal} footer={<></>} onCancel={() => setBoxplotModal(false)}>
                <Image width={"100%"} src={boxplot}></Image>
            </Modal>
        </Row>
    </>
}

export default AbundanceOpterature




