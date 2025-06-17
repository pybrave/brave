import { Venn } from "@ant-design/plots"
import { Button, Card, message, Popconfirm, Popover, Space, Table } from "antd"
import axios from "axios"
import { FC, forwardRef, useEffect, useImperativeHandle, useState } from "react"
import { useParams } from "react-router"

export const readHdfsAPi = (contentPath: any) => axios.get(`/api/read-hdfs?path=${contentPath}`)
export const readJsonAPi = (contentPath: any) => axios.get(`/fast-api/read-json?path=${contentPath}`)


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
    activeTabKey,
    setActiveTabKey,
    cardExtra
}, ref) => {
    useImperativeHandle(ref, () => ({
        reload
    }))

    const { project } = useParams()
    const [data, setData] = useState<any>([])
    const [groupedData, setGroupedData] = useState<any>()
    // const [content,setContent] = useState<any>()
    const [loading, setLoading] = useState(false)
    // const [currentAnalysisMethod, setCurrentAnalysisMethod] = useState<any>()

    // const reload = () => {
    //     loadData(currentAnalysisMethod.value)
    // }
    // useEffect(() => {
    //     const currentAnalysisMethod = analysisMethod[0]
    //     initData(currentAnalysisMethod)
    // }, [])
    // const initData = (currentAnalysisMethod:any)=>{
    //     setActiveTabKey(currentAnalysisMethod.key)
    //     setCurrentAnalysisMethod(currentAnalysisMethod)
    //     loadData(currentAnalysisMethod.value)
    // }
    // const onTabChange = (key:any)=>{
    //     const currentAnalysisMethod = analysisMethod.filter((it:any)=>it.key==key)[0]
    //     initData(currentAnalysisMethod)
    // }

    const reload = () => {
        console.log(analysisMethod)
        if (analysisMethod && Array.isArray(analysisMethod)) {
            const analysisMethodList = analysisMethod.flatMap((it: any) => it.inputKey)
            // console.log(analysisMethodList)
            loadData(analysisMethodList)
        }

    }
    useEffect(() => {
        // const currentAnalysisMethod = analysisMethod[0]
        if (setActiveTabKey) {
            setActiveTabKey(analysisMethod[0].name)
        }
        reload()

        // initData(currentAnalysisMethod)
    }, [])

    const onTabChange = (key: any) => {
        setData(groupedData[key])
        setActiveTabKey(key)


    }
    const getKeyMap = () => {
        const analysisMethodMap = Object.fromEntries(analysisMethod.map((item: any) => [item.name, item.inputKey]));
        // console.log(analysisMethodMap)
        const result: any = {};
        Object.entries(analysisMethodMap).forEach(([key, values]) => {
            values.forEach((value: any) => {
                result[value] = key;
            });
        });
        return result
    }
    const loadData = async (analysisMethodValues: any) => {
        setLoading(true)
        let resp: any = await axios.post(`/fast-api/find-analyais-result-by-analysis-method`, {
            project: project,
            analysis_method: analysisMethodValues
        })

        const keyMap = getKeyMap()
        // console.log(keyMap)
        const groupedData = resp.data.reduce((acc: any, item: any) => {
            // const key = item.analysis_method;
            const key = keyMap[item.analysis_method]
            if (!acc[key]) {
                acc[key] = [];
            }
            const { sample_key, id, sample_group, ...rest } = item
            // debugger
            acc[key].push({
                label: sample_key,
                value: id,
                sample_group: sample_group?sample_group:"no_group",
                sample_key:sample_key,
                id:id,
                // "aaa":"1111",
                ...rest
            });
            return acc;
        }, {});

        if (setResultTableList) {
            // console.log(groupedData)
            setResultTableList(groupedData)
        }
        setGroupedData(groupedData)
        console.log("activeTabKey: ", activeTabKey)
        if (activeTabKey) {
            setData(groupedData[activeTabKey] ? groupedData[activeTabKey] : [])
        } else {
            setData(groupedData[analysisMethod[0].name] ? groupedData[analysisMethod[0].name] : [])
        }
        setLoading(false)
    }

    // useEffect(() => {
    //     reload()

    // }, [])
    const deleteById = async (id: any) => {
        const resp: any = await axios.get(`/api/analysis-result-delete?id=${id}`)
        message.success("删除成功!")
        reload()
    }
    // const readHdfs = async (contentPath: any) => {
    //     setTableLoading(true)
    //     const resp: any = await readHdfsAPi(contentPath)

    //     setTabletData(resp.data)
    //     setTableLoading(false)
    //     // reset()
    //     // console.log(resp.data)
    //     // setData(resp.data)
    // }
    const readJOSN = async (contentPath: any) => {
        setTableLoading(true)
        const resp: any = await readJsonAPi(contentPath)
        setTabletData(resp.data)
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

    let columns: any = []
    if (analysisType == "sample") {
        columns = [
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
                title: '分析id',
                dataIndex: 'analysis_id',
                key: 'analysis_id',
                ellipsis: true,

            }, {
                title: '分析版本',
                dataIndex: 'analysis_version',
                key: 'analysis_version',
                ellipsis: true,
            }, {
                title: '样本名称',
                dataIndex: 'sample_name',
                key: 'sample_name',
                ellipsis: true,

            }, {
                title: '样本Key',
                dataIndex: 'sample_key',
                key: 'sample_key',
                ellipsis: true,

            } , {
                title: '分析Key',
                dataIndex: 'analysis_key',
                key: 'analysis_key',
                ellipsis: true,

            }, {
                title: '样本分组',
                dataIndex: 'sample_group',
                key: 'sample_group',
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
            }, ...appendSampleColumns, {
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
                                if (cleanDom) {
                                    cleanDom(undefined)
                                }

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

    } else {
        columns = [
            {
                title: '分析名称',
                dataIndex: 'analysis_name',
                key: 'analysis_name',
                ellipsis: true,

            }, {
                title: 'id',
                dataIndex: 'id',
                key: 'id',
                ellipsis: true,

            }, {
                title: "分析方法",
                dataIndex: 'analysis_method',
                key: 'analysis_method',
                ellipsis: true,
            }, {
                title: '输入软件',
                dataIndex: 'software',
                key: 'software',
                ellipsis: true,
            }, {
                title: 'project',
                dataIndex: 'project',
                key: 'project',
                ellipsis: true,
            }, {
                title: 'control',
                dataIndex: 'control',
                key: 'control',
                ellipsis: true,
            }, {
                title: 'treatment',
                dataIndex: 'treatment',
                key: 'treatment',
                ellipsis: true,

            }, {
                title: 'rank',
                dataIndex: 'rank',
                key: 'rank',
                ellipsis: true,
            }, {
                title: '创建时间',
                dataIndex: 'create_date',
                key: 'create_date',
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
                            {record.content}
                        </>} >
                            <a onClick={() => {
                                const param = JSON.parse(record.request_param)
                                console.log(param)
                                form.resetFields()
                                form.setFieldsValue(param)
                                if (record?.id) {
                                    form.setFieldValue("id", record?.id)
                                }
                                readJOSN(record.content)
                                setRecord(record)
                            }}>查看</a>
                        </Popover>

                        {/* <a onClick={() => { downloadHdfs(record.content) }}>下载</a> */}
                        <Popconfirm title="确定删除吗?" onConfirm={async () => {
                            await deleteById(record.id)
                        }}>
                            <a>删除</a>
                        </Popconfirm>

                    </Space>
                ),
            },
        ]
    }



    return <>
        <Card title={title}
            extra={<>{cardExtra}<Button onClick={reload}>刷新</Button></>}
            tabList={analysisMethod && Array.isArray(analysisMethod) && analysisMethod.length > 1 ?
                analysisMethod.map((it: any) => ({ key: it.name, label: it.label })) : undefined}
            activeTabKey={activeTabKey}
            onTabChange={onTabChange}
        >
            <Table
                rowKey={(it: any) => it.id}
                size="small"
                pagination={{ pageSize: 100 }}
                loading={loading}
                scroll={{ x: 'max-content', y: 55 * 5 }}
                columns={columnsParamsALL ? columnsParamsALL : columns}
                footer={() => `一共${data && Array.isArray(data) && data.length}条记录`}
                dataSource={data} />

        </Card>
        {/* <Card style={{ marginBottom: "1rem" }}>
            <Button onClick={loadData}>刷新</Button>
        </Card> */}

    </>

})

export default ResultList