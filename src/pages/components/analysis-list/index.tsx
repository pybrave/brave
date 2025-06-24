import { Venn } from "@ant-design/plots"
import { Button, Card, message, Popconfirm, Popover, Space, Table } from "antd"
import axios from "axios"
import { FC, forwardRef, useEffect, useImperativeHandle, useState } from "react"
import { useParams } from "react-router"

export const readHdfsAPi = (contentPath: any) => axios.get(`/api/read-hdfs?path=${contentPath}`)
export const readJsonAPi = (contentPath: any) => axios.get(`/fast-api/read-json?path=${contentPath}`)
export const parseAnalysisResultAPi = (id: any) => axios.post(`/fast-api/parse-analysis-result/${id}`)

const ResultList = forwardRef<any, any>(({
    title,
    form,
    appendSampleColumns = [],
    setResultTableList,
    cleanDom,
    analysisType,
    setRecord,
    setTableLoading,
    setTabletData,
    shouldTrigger,
    analysisMethod,
    columnsParamsALL,
    project
}, ref) => {
    useImperativeHandle(ref, () => ({
        reload: loadData
    }))
    const [messageApi, contextHolder] = message.useMessage();
    
    const [data, setData] = useState<any>([])
    // const [content,setContent] = useState<any>()
    const [loading, setLoading] = useState(false)
    const loadData = async () => {
        setLoading(true)
        let resp: any = await axios.get(`/fast-api/analysis?analysis_method=${analysisMethod}&project=${project}`);
        // if (analysisMethod) {
        //     resp = await axios.get(`/api/analysis-result?project=${project}&analysis_method=${analysisMethod}`)
        // } else {
        //     resp 
        // }
        if (setResultTableList) {
            setResultTableList(resp.data)
        }

        setData(resp.data)
        setLoading(false)
    }
    const deleteById = async (id: any) => {
        const resp: any = await axios.delete(`/fast-api/analysis/${id}`)
        message.success("删除成功!")
        loadData()
    }


    const readJOSN = async (contentPath: any) => {
        setTableLoading(true)
        const resp: any = await readJsonAPi(contentPath)
        setTabletData(resp.data)
        setTableLoading(false)
        // reset()
        // console.log(resp.data)
        // setData(resp.data)
    }


    let columns: any = [
        {
            title: 'id',
            dataIndex: 'id',
            key: 'id',
            ellipsis: true,

        }, {
            title: 'project',
            dataIndex: 'project',
            key: 'project',
            ellipsis: true,

        }, {
            title: 'analysis_method',
            dataIndex: 'analysis_method',
            key: 'analysis_method',
            ellipsis: true,

        }, {
            title: "analysis_name",
            dataIndex: 'analysis_name',
            key: 'analysis_name',
            ellipsis: true,
        }, {
            title: 'params_path',
            dataIndex: 'params_path',
            key: 'params_path',
            ellipsis: true,
        }, {
            title: 'pipeline_script',
            dataIndex: 'pipeline_script',
            key: 'pipeline_script',
            ellipsis: true,
        }, {
            title: 'work_dir',
            dataIndex: 'work_dir',
            key: 'work_dir',
            ellipsis: true,
        }, {
            title: 'output_dir',
            dataIndex: 'output_dir',
            key: 'output_dir',
            ellipsis: true,
        }, {
            title: '操作',
            key: 'action',
            fixed: "right",
            ellipsis: true,
            width: 200,
            render: (_: any, record: any) => (
                <Space size="middle">
                    <Popover content={<>
                        {/* <Typography >
                                <pre>{JSON.stringify(JSON.parse(record.content), null, 2)}</pre>
                            </Typography> */}
                        {record.analysis_name}
                    </>} >
                        <a onClick={() => {
                            // record.content = JSON.parse(record.content)
                            setRecord(record)
                            // if (cleanDom) {
                            //     cleanDom(undefined)
                            // }
                        }}>查看</a>
                    </Popover>
                    <Popconfirm title={"是否删除!"} onConfirm={async () => {
                        await deleteById(record.id)
                    }}>
                        <a>删除</a>
                    </Popconfirm>
                    <Popconfirm title={"是否解析!"} onConfirm={async () => {
                        try {
                            await parseAnalysisResultAPi(record.id)
                            messageApi.success("提交成功")
                        } catch (error:any) {
                            console.log(error)
                            messageApi.error(error?.response?.data?.detail)
                        }

                    }}>
                        <a>解析</a>
                    </Popconfirm>
                </Space>
            ),
        },
    ]


    useEffect(() => {
        loadData()
    }, [])
    return <>
        {contextHolder}
        <Card title={title} extra={<Button onClick={loadData}>刷新</Button>} >
            <Table
                size="small"
                pagination={false}
                loading={loading}
                scroll={{ x: 'max-content', y: 55 * 5 }}
                columns={columns}
                footer={() => `一共${data.length}条记录`}
                dataSource={data} />

        </Card>

    </>
})

export default ResultList

