import { FC, useEffect, useState } from "react"
import axios from "axios"
import { Button, Col, Drawer, Input, Row, Space, Table, TableProps, Image, Form, Select, Spin, Modal, Tabs, Popconfirm, message } from "antd"
import { useParams } from "react-router"
import { Box } from '@ant-design/plots';
import ResultList from '@/components/result-list'
import AnalysisForm from "../../../components/analysis-form-bak";

const AbundanceOpterature: FC<any> = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<any>({})
    const { project } = useParams()
    const [boxplotModal, setBoxplotModal] = useState(false)
    const [taxonomy, setTaxonomy] = useState("")
    const [boxplot, setBoxplot] = useState("")
    const [boxplotLoading, setBoxplotLoading] = useState(false)
    const [table, setTable] = useState<any>([])
    // const [classifiedTaxonomy, setclassifiedTaxonomy] = useState([])
    // const [unclassifiedTaxonomy, setunclassifiedTaxonomy] = useState([])
    const { Search } = Input;

    const getCompareAbundance = async () => {
        const values = await form.validateFields()
        console.log(values)
        setLoading(true)
        const resp: any = await axios.post(`/jupyter/get--compare-abundance`, {
            ...values,
            project: project,
            // rnak:"SPECIES",

        })
        setData(resp.data)
        setTable(resp.data.table)
        setLoading(false)
        console.log(resp)
    }
    // const reset = () => {
    //     const classifiedTaxonomy = data.filter((it: any) => it.tax_id != null)
    //     const unclassifiedTaxonomy = data.filter((it: any) => it.tax_id == null)
    //     setclassifiedTaxonomy(classifiedTaxonomy)
    //     setunclassifiedTaxonomy(unclassifiedTaxonomy)
    // }
    const setTabletData = (data: any) => {
        setData(data)
        setTable(data.table)
        // const classifiedTaxonomy = data.filter((it: any) => it.tax_id != null)
        // const unclassifiedTaxonomy = data.filter((it: any) => it.tax_id == null)
        // setclassifiedTaxonomy(classifiedTaxonomy)
        // setunclassifiedTaxonomy(unclassifiedTaxonomy)
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
            title: 'Statistic',
            dataIndex: 'Statistic',
            key: 'Statistic',
        }, {
            title: 'P-value',
            dataIndex: 'P-value',
            key: 'P-value',
        }, {
            title: 'log2foldchange',
            dataIndex: 'log2foldchange',
            key: 'log2foldchange',
        }, {
            title: 'fdr_bh',
            dataIndex: 'fdr_bh',
            key: 'fdr_bh',
        }, {
            title: 'AdjustedP-value',
            dataIndex: 'AdjustedP-value',
            key: 'AdjustedP-value',
        },
    ]
    const getStatistics = () => {
        const significant = data?.table.filter((it: any) => it['P-value'] < 0.05)
        const upSignificant = significant.filter((it: any) => it.log2foldchange > 0)
        const downSignificant = significant.filter((it: any) => it.log2foldchange < 0)
        //  [significant.length,upSignificant.length,downSignificant.length]
        return `总共有${significant.length}个分类，其中上调的有${upSignificant.length}个，下调的有${downSignificant.length}多个`
    }
    return <>
        <Row>
            <Col lg={12} sm={24} xs={24}>
                <AnalysisForm form={form}></AnalysisForm>  
                <Button onClick={getCompareAbundance}>提交</Button>
                <ResultList analysisMethod={"difference"} shouldTrigger={!loading} form={form} setTableLoading={setLoading} setTabletData={setTabletData}  ></ResultList>
                {/* <Abundance /> */}


            </Col>
            <Col lg={12} sm={24} xs={24}>
                {/* <Spin spinning={loading} tip="正在计算中...">
                </Spin> */}
                  {data?.img && <>
                    <Image width={"50%"} src={data?.img}></Image>
                </>}

                <p>
                {data?.table &&
                    <>
                        一共鉴定到{data?.table.length}个分类，其中根据pvalue 小于 0.05筛选，{getStatistics()}
                    </>
                }
                </p>

                <Search
                    placeholder="input search text"
                    allowClear
                    onSearch={(value: any) => {
                        // console.log(data?.table)
                        const filterAbundance = data?.table.filter((it: any) => it.taxonomy.includes(value) || (it.tax_id && it.tax_id.includes(value)) )
                        setTable(filterAbundance)
                    }}
                    style={{ width: 304 }}
                />
               
                <Table
                    pagination={{ pageSize: 30 }}
                    loading={loading}
                    scroll={{ x: 'max-content', y: 55 * 5 }}
                    columns={compareColumns}

                    dataSource={table} />
               
                {/* <Tabs tabBarExtraContent={<>
                </>} items={[
                    {
                        key: "classified",
                        label: "已分类",
                        children: <>
                            已分类的一共有{classifiedTaxonomy.length}条记录
                            <Search
                                placeholder="input search text"
                                allowClear
                                onSearch={(value: any) => {
                                    const filterAbundance = data.filter((it: any) => it.tax_id != null).filter((it: any) => it.taxonomy.includes(value))
                                    setclassifiedTaxonomy(filterAbundance)
                                }}
                                style={{ width: 304 }}
                            />
                            <Table
                                pagination={{ pageSize: 30 }}
                                loading={loading}
                                scroll={{ x: 'max-content' }}
                                columns={compareColumns}
                                dataSource={classifiedTaxonomy} />
                        </>
                    }, {
                        key: "unclassified",
                        label: "未分类的",
                        children: <>
                            未分类的一共有{unclassifiedTaxonomy.length}条记录
                            <Search
                                placeholder="input search text"
                                allowClear
                                onSearch={(value: any) => {
                                    const filterAbundance = data.filter((it: any) => it.tax_id == null).filter((it: any) => it.taxonomy.includes(value))
                                    setunclassifiedTaxonomy(filterAbundance)
                                }}
                                style={{ width: 304 }}
                            />
                            <Table
                                pagination={{ pageSize: 30 }}
                                loading={loading}
                                scroll={{ x: 'max-content' }}
                                columns={compareColumns}
                                dataSource={unclassifiedTaxonomy} />
                        </>
                    }
                ]}></Tabs> */}


                {/* <SearchAbundance /> */}
            </Col>

            <Modal loading={boxplotLoading} title={taxonomy} width={"50%"} open={boxplotModal} footer={<></>} onCancel={() => setBoxplotModal(false)}>
                <Image width={"100%"} src={boxplot}></Image>
            </Modal>
        </Row>
    </>
}

export default AbundanceOpterature



