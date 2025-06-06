import { FC, useEffect, useState } from "react"
import axios from "axios"
import { Button, Card, Col, Form, Row, Select, Table, TableProps, Tabs, Image, Typography, Spin } from "antd"
import { getSamples } from "@/pages/sample"
import { useParams } from "react-router"
import TextArea from "antd/es/input/TextArea"
import DemoHeatmap from '@/pages/plots/heatmap'
const MutationCompare: FC<any> = () => {
    const [mutationData, setMutationData] = useState([])
    const [loading, setLoading] = useState(false)
    const [columns, setColumns] = useState<any>([])
    const [sampleNames, setSampleNames] = useState([])
    const { project,sampleComposition } = useParams()


    // const [formValue,setFormValue] = useState({})
    const columns0: TableProps<any>['columns'] = [
        {
            title: 'seq_id',
            dataIndex: 'seq_id',
            key: 'seq_id',
        }, {
            title: 'position',
            dataIndex: 'position',
            key: 'position',
        }, {
            title: 'locus_tag',
            dataIndex: 'locus_tag',
            key: 'locus_tag',
        }, {
            title: 'type',
            dataIndex: 'type',
            key: 'type',
        },
        {
            title: 'ref_seq',
            dataIndex: 'ref_seq',
            key: 'ref_seq',
        },
        {
            title: 'gene_name',
            dataIndex: 'gene_name',
            key: 'gene_name',
        }, {
            title: 'gene_product',
            dataIndex: 'gene_product',
            key: 'gene_product',
        },
    ]
    const loadSample = async () => {
        const samples = await getSamples(project,sampleComposition)
        // samples.data
        const dynamic_columns = samples.data.map((it: any) => {
            return {
                title: it.sample_name,
                dataIndex: it.sample_name,
                key: it.sample_name,
            }
        })
        const sampleNames = samples.data.map((it: any) => {
            return {
                value: it.sample_name, label: it.sample_name
            }
        })
        // console.log(sampleNames)
        setSampleNames(sampleNames)
        setColumns([...columns0, ...dynamic_columns])
    }
    const loadMutationCompare = async (formValue: any) => {
        setLoading(true)
        // console.log(dynamic_columns)
        const resp: any = await axios.post('/api/mutation-compare', formValue)
        console.log(resp)
        setLoading(false)
        setMutationData(resp.data)
    }


    useEffect(() => {

        loadSample()
        loadMutationCompare({})
    }, [])
    return <>
        <Row>
            <Col lg={12} sm={24} xs={24}>
                <Card style={{ marginRight: "0.5rem" }}>
                    <CompareForm loadMutationCompare={loadMutationCompare}
                        sampleNames={sampleNames}
                        mutationData={mutationData}
                    ></CompareForm>
                    <hr />
                    <SnvMatrixCompare></SnvMatrixCompare>

                </Card>
            </Col>

            <Col lg={12} sm={24} xs={24}>
                <Card style={{ marginLeft: "0.5rem" }}>
                    <Tabs items={[
                        {
                            key: "snv_site",
                            label: "所有SNV位点",
                            children: <Table loading={loading}
                                pagination={{ pageSize: 30 }}
                                scroll={{ x: 'max-content' }}
                                columns={columns}
                                rowKey={(it: any) => it.position}
                                dataSource={mutationData} />
                        },
                        // {
                        //     key: "snv_statistic",
                        //     label: "样本之间SNV比较",
                        //     children: <SnvMatrixCompare />
                        // }
                    ]}></Tabs>

                </Card>
            </Col>

        </Row>

    </>
}

export default MutationCompare

const CompareForm: FC<any> = ({ loadMutationCompare, sampleNames, mutationData }) => {
    const [form] = Form.useForm();

    return <>

        <Form form={form}
            onFinish={(values) => {
                // setFormValue(values)

                loadMutationCompare(values)
                console.log(values)
            }}
        >
            <Form.Item label="第一组" name={"group1"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Select mode="multiple" allowClear options={sampleNames}></Select>
            </Form.Item>
            <Form.Item label="第二组" name={"group2"} rules={[{ required: true, message: '该字段不能为空!' }]}>
                <Select mode="multiple" allowClear options={sampleNames}></Select>
            </Form.Item>
            <Form.Item label={null}>
                <Button type="primary" htmlType="submit">
                    提交
                </Button>

            </Form.Item>
            <Button onClick={() => {
                // setFormValue({})
                form.resetFields()
                loadMutationCompare({})
            }}>重置</Button>
            {/* <Form.Item noStyle shouldUpdate>
                            {() => (
                                <Typography>
                                    <pre>{JSON.stringify(form.getFieldsValue(), null, 2)}</pre>
                                </Typography>
                            )}
                        </Form.Item> */}
        </Form>

        {mutationData && <>
            总共检测到[{ mutationData.length}]个突变位点
            <TextArea rows={4} value={mutationData.map((it: any) => it.locus_tag).join(", ")}>
            </TextArea>
        </>}

    </>
}

const SnvMatrixCompare: FC<any> = ({ }) => {
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<any>()
    const [heatmapData, setHeatmapData] = useState<any>([])
    const loadData = async () => {
        setLoading(true)
        const resp: any = await axios.get('/jupyter/snv_compare_tree')
        // console.log(resp.data)
        setData(resp.data)
        setLoading(false)
        const matrix = JSON.parse(resp.data.matrix)
        const heatmapData = Object.entries(matrix).map((item: any) => {
            const [key, value] = item
            return Object.entries(value).map((item2: any) => {
                const [key2, value2] = item2
                return {
                    sample1: key,
                    sample2: key2,
                    value: value2
                }
            })
        }).flat(Infinity)
        setHeatmapData(heatmapData)
        console.log(heatmapData)

    }
    useEffect(() => {
        loadData()
    }, [])
    return <>
        <Button onClick={loadData}>刷新</Button>
        <Spin spinning={loading}>
            {data && <>
                <Image width={"100%"} src={data.image}></Image>
                <DemoHeatmap data={heatmapData} />
                {/* <Typography>
                    <pre>{JSON.stringify(JSON.parse(data.matrix), null, 2)}</pre>
                </Typography> */}
            </>}
        </Spin>
        {/* <img  src={data} alt="" /> */}



        {/* <Table loading={loading}
            scroll={{ x: 'max-content' }}
            columns={columns}
            // rowKey={(it: any) => it.position}
            dataSource={data} /> */}
    </>
}