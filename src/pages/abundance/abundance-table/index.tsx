import { Button, Drawer, Input, Space, Table, TableProps } from "antd"
import axios from "axios"
import { FC, useEffect, useState } from "react"
import { useOutletContext, useParams } from "react-router"

const Abundance: FC<any> = () => {
    const [sampleData, setSampleData] = useState([])
    const [loading, setLoading] = useState(false)
    const { project } = useOutletContext<any>();
    const [open, setOpen] = useState(false)
    const [record, setRecord] = useState<any>()
    const [drawerLoading, setDrawerLoading] = useState(false)
    const [abundance, setAbundance] = useState([])
    const { Search } = Input;

    const loadSample = async () => {
        setLoading(true)
        const resp: any = await axios.get(`/api/abundance?project=${project}`)
        console.log(resp)
        setLoading(false)
        setSampleData(resp.data)
    }

    const getAbundance = async (contentPath: any) => {
        setDrawerLoading(true)
        // const resp: any = await axios.get(`/api/get-abundance?id=${id}`)
        const resp: any = await axios.get(`/api/read-hdfs?path=${contentPath}`)

        console.log(resp.data)
        setAbundance(resp.data)
        // setRecord(resp.data)
        setDrawerLoading(false)
    }

    const columns: TableProps<any>['columns'] = [
        // {
        //     title: 'id',
        //     dataIndex: 'id',
        //     key: 'id',
        // },
        {
            title: '样本名称',
            dataIndex: 'sample_name',
            key: 'sample_name',
        },  {
            title: '数据版本',
            dataIndex: 'data_version',
            key: 'data_version',
        },{
            title: 'software',
            dataIndex: 'software',
            key: 'software',
        }, {
            title: 'sample_composition',
            dataIndex: 'sample_composition',
            key: 'sample_composition',
        }, {
            title: 'host_disease',
            dataIndex: 'host_disease',
            key: 'host_disease',
        }, {
            title: 'sample_group',
            dataIndex: 'sample_group',
            key: 'sample_group',
        },
        {
            title: '项目',
            dataIndex: 'project',
            key: 'project',
        }, {
            title: '操作',
            key: 'action',
            fixed: "left",
            width: 100,
            render: (_, record) => (
                <Space size="middle">
                    <a onClick={() => {
                        setRecord(record)
                        getAbundance(record.content)
                        setOpen(true)

                    }}>查看</a>
                </Space>
            ),
        },
    ]
    const abundanceColumns: TableProps<any>['columns'] = [
        {
            title: 'taxonomy',
            dataIndex: 'taxonomy',
            key: 'taxonomy',
        }, {
            title: 'relative_abundance',
            dataIndex: 'relative_abundance',
            key: 'relative_abundance',
        }, {
            title: 'tax_id',
            dataIndex: 'tax_id',
            key: 'tax_id',
        }, {
            title: 'rank',
            dataIndex: 'rank',
            key: 'rank',
        }, {
            title: 'additional_species',
            dataIndex: 'additional_species',
            key: 'additional_species',
        },
    ]
    useEffect(() => {
        loadSample()
    }, [])
    return <>
        {sampleData && <>鉴定丰度的样本数量{sampleData.length}</>}
        <Button onClick={loadSample}>刷新</Button>
        <Table
            pagination={{ pageSize: 30 }}
            loading={loading}
            scroll={{ x: 'max-content' }}
            columns={columns}
            dataSource={sampleData} />
        <Drawer extra={<>
            <Button onClick={() => getAbundance(record?.content_path)}>刷新</Button>
        </>} loading={drawerLoading} title={record ? record.sample_name : ""} open={open} onClose={() => setOpen(false)} width={"80%"}>
            <Search
                placeholder="input search text"
                allowClear
                onSearch={(value: any) => {
                    const filterAbundance = abundance.filter((it: any) => it.taxonomy.includes(value))
                    setAbundance(filterAbundance)
                }}
                style={{ width: 304 }}
            />
            <Table
                pagination={{ pageSize: 30 }}
                loading={drawerLoading}
                scroll={{ x: 'max-content' }}
                columns={abundanceColumns}
                dataSource={abundance} />
        </Drawer>

    </>
}

export default Abundance