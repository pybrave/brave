import { Venn } from "@ant-design/plots"
import { Button, message, Popconfirm, Popover, Space, Table, Typography } from "antd"
import axios from "axios"
import { FC, useEffect, useState } from "react"
import { useParams } from "react-router"

export const readHdfsAPi = (contentPath: any) => axios.get(`/api/read-hdfs?path=${contentPath}`)
const SampleAnalysisResult: FC<any> = ({ form, setTableLoading, setSampleResult, shouldTrigger, analysisName, columnsParamsALL }) => {
    const { project } = useParams()
    const [data, setData] = useState<any>([])
    const [loading, setLoading] = useState(false)
    // const [content,setContent] = useState<any>()
    const loadData = async () => {
        setLoading(true)

        let resp: any = await axios.get(`/api/sample-analysis-list?project=${project}&analysis_name=${analysisName}`)


        setData(resp.data)
        setLoading(false)
    }
    const deleteById = async (id: any) => {
        // const resp: any = await axios.get(`/api/analysis-result-delete?id=${id}`)
        // message.success("删除成功!")
        // loadData()
    }
    const readHdfs = async (contentPath: any) => {
        setTableLoading(true)
        const resp: any = await readHdfsAPi(contentPath)

        // setTabletData(resp.data)
        setTableLoading(false)
        // reset()
        // console.log(resp.data)
        // setData(resp.data)
    }

    const downloadTSV = (tsvData: string, filename = 'data.tsv') => {
        const blob = new Blob([tsvData], { type: 'text/tab-separated-values' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url); // 释放内存:ml-citation{ref="2,7" data="citationList"}
    };
    const downloadHdfs = async (contentPath: any) => {
        const resp: any = await axios.get(`/api/download-hdfs?path=${contentPath}`)
        // console.log(contentPath.split('/').pop())
        downloadTSV(resp.data, contentPath.split('/').pop())
    }



    const columns: any = [
        {
            title: 'id',
            dataIndex: 'id',
            key: 'id',
            ellipsis: true,

        }, {
            title: '分析名称',
            dataIndex: 'analysis_name',
            key: 'analysis_name',
            ellipsis: true,

        }, {
            title: '分析版本',
            dataIndex: 'analysis_verison',
            key: 'analysis_verison',
            ellipsis: true,
        }, {
            title: '样本名称',
            dataIndex: 'sample_name',
            key: 'sample_name',
            ellipsis: true,

        }, {
            title: "软件",
            dataIndex: 'software',
            key: 'software',
            ellipsis: true,
        }, {
            title: 'project',
            dataIndex: 'project',
            key: 'project',
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
                            setSampleResult(record)
                            // const param = JSON.parse(record.request_param)
                            // console.log(param)
                            // form.resetFields()
                            // form.setFieldsValue(param)
                            // if (record?.id) {
                            //     form.setFieldValue("id", record?.id)
                            // }
                            // readHdfs(record.content)
                        }}>查看</a>
                    </Popover>
                    {/* <a onClick={() => { downloadHdfs(record.content) }}>下载</a>
                    <Popconfirm title="确定删除吗?" onConfirm={async ()=>{
                        await deleteById(record.id)
                    }}>
                        <a href="javascript:;">删除</a>
                    </Popconfirm>
                    */}
                </Space>
            ),
        },
    ]
    useEffect(() => {
        if (shouldTrigger) {
            loadData()
        }
        console.log(shouldTrigger)
    }, [shouldTrigger])

    return <>

        <Table
            pagination={false}
            loading={loading}
            scroll={{ x: 'max-content', y: 55 * 5 }}
            columns={columnsParamsALL ? columnsParamsALL : columns}
            dataSource={data} />
        <Button onClick={loadData}>刷新</Button>

    </>
}


export default SampleAnalysisResult