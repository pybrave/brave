import { Button, Form, Input, Modal, notification, Select, Space, Typography } from "antd";
import { FC, useState } from "react";
import ResultList from '@/components/result-list'

const AnalysisResultInput: FC<any> = ({ value, onChange, multiple = true }) => {
    const [form] = Form.useForm();
    const [analysisParams, setAnalysisParams] = useState<any>(value)
    const [api, contextHolder] = notification.useNotification();
    const [record, setRecord] = useState<any>()
    const [open, setOpen] = useState<boolean>(false)
    const [openForm, setOpenForm] = useState<boolean>(false)

    const columns: any = [
        {
            title: '分析名称',
            dataIndex: 'analysis_name',
            key: 'analysis_name',
            ellipsis: true,
        },
        {
            title: 'id',
            dataIndex: 'id',
            key: 'id',
        }, {
            title: "分析方法",
            dataIndex: 'analysis_method',
            key: 'analysis_method',
        }, {
            title: 'project',
            dataIndex: 'project',
            key: 'project',
        }, {
            title: 'control',
            dataIndex: 'control',
            key: 'control',
        }, {
            title: 'treatment',
            dataIndex: 'treatment',
            key: 'treatment',
        }, {
            title: 'software',
            dataIndex: 'software',
            key: 'software',
        }, {
            title: 'rank',
            dataIndex: 'rank',
            key: 'rank',
        }, {
            title: '创建时间',
            dataIndex: 'create_date',
            key: 'create_date',
        }, {
            title: '操作',
            key: 'action',
            fixed: "right",
            width: 200,
            render: (_: any, record: any) => (
                <Space size="middle">
                    {/* <Popover content={<>
                        {record.content}
                    </>} >
                        <a onClick={async () => {
                            const param = JSON.parse(record.request_param)
                            console.log(param)
                            form.setFieldsValue(param)
                            const resp = await readHdfsAPi(record.content)
                            setData(resp.data)
                        }}>查看</a>
                    </Popover> */}
                    <a onClick={() => {
                        setOpenForm(true)
                        setRecord(record);

                        form.setFieldValue("id", record.id)
                        form.setFieldValue("label", record.analysisName)

                        form.setFieldValue("contentPath", record.content)
                        console.log(record)
                        if (record.analysis_method == "abundance-venn") {
                            form.setFieldValue("name", `${record.software}-${record.rank}-${record.analysis_method}`)

                        } else {
                            form.setFieldValue("name", `${record.software}-${record.rank}-${record.analysis_method}(${record.treatment} - ${record.control})`)

                        }
                    }}>添加</a>
                    {/* <Popconfirm title="确定删除吗?" onConfirm={async ()=>{
                        await deleteById(record.id)
                    }}>
                        <a href="javascript:;">删除</a>
                    </Popconfirm> */}

                </Space>
            ),
        },
    ]
    const query: any = {
        difference: [
            {
                label: "table#`P-value`<0.05",
                value: "table#`P-value`<0.05"
            }
        ],
        prevalence: [
            {
                label: "table#type=='Prevalent in both sites'",
                value: "table#type=='Prevalent in both sites'"
            }, {
                label: "table#type=='Prevalent in oral cavity' or type=='Prevalent in both sites'",
                value: "table#type=='Prevalent in oral cavity' or type=='Prevalent in both sites'"
            }, {
                label: "table#type=='Prevalent in gut'",
                value: "table#type=='Prevalent in gut'"
            }, {
                label: "table#type=='Prevalent in gut' or type=='Prevalent in both sites'",
                value: "table#type=='Prevalent in gut' or type=='Prevalent in both sites'"
            },
        ], "abundance-venn": [
            {
                label: "regions#unique#taxonomy",
                value: "regions#unique#taxonomy"
            }, {
                label: "regions#11#taxonomy",
                value: "regions#11#taxonomy"
            }
        ]
    }

    return <>

        {value ? <>
            {/* <TextArea rows={5} style={{cursor:"pointer"}}  value={JSON.stringify(value, null, 2)} onClick={() => setOpen(true)}></TextArea> */}
            <Typography style={{ cursor: "pointer" }} onClick={() => setOpen(true)}>
                <pre>{JSON.stringify(value, null, 2)}</pre>
            </Typography><a onClick={() => { onChange(undefined); setAnalysisParams(undefined) }} >清除</a>
        </> : <><Button onClick={() => setOpen(true)}>添加数据</Button></>}
        <Modal footer={<><Button type="primary" onClick={() => setOpen(false)}>关闭</Button></>} width={"60%"} onOk={async () => {
            onChange(analysisParams)
            // setOpenAddForm(false)
        }} title={record ? `${record.software}-${record.rank}-${record.analysis_method}(${record.treatment} - ${record.control})` : ""} open={open} onCancel={() => setOpen(false)}>

            <ResultList columnsParamsALL={columns} shouldTrigger={true} form={form}   ></ResultList>

            {openForm && <>
                <Form form={form}>
                    <Form.Item name={"contentPath"} label="路径" rules={[{ required: true, message: '该字段不能为空!' }]} >
                        <Input disabled></Input>
                    </Form.Item>
                    <Form.Item name={"label"} label="标签" rules={[{ required: true, message: '该字段不能为空!' }]}>
                        <Input ></Input>
                    </Form.Item>
                    <Form.Item name={"name"} label="名称" rules={[{ required: true, message: '该字段不能为空!' }]}>
                        <Input ></Input>
                    </Form.Item>
                   
                    <Form.Item name={"query"} label="条件" rules={[{ required: true, message: '该字段不能为空!' }]}>
                        <Select allowClear options={query[record?.analysis_method]}></Select>
                    </Form.Item>
                    <Form.Item name={"id"} style={{ display: "none" }} >
                        <Input disabled></Input>
                    </Form.Item>

                </Form>
                {/* <Typography>
                    <pre>{JSON.stringify(record, null, 2)}</pre>
                </Typography> */}
                <Button onClick={async () => {
                    const values = await form.validateFields()

                    if (multiple) {
                        // if (!analysisParams) {
                        //     setAnalysisParams([])
                        // }

                        if (Array.isArray(analysisParams)) {
                            if (analysisParams.length > 3) {
                                api['error']({
                                    message: `目前只支持3个对象的韦恩图!`
                                });
                                return
                            }
                            const findName = analysisParams.filter((it: any) => it.name == values.name && it.query == values.query)
                            if (findName.length > 0) {
                                api['error']({
                                    message: `已经存在name:${values.name};query:${values.query}`
                                });
                                return
                            }
                            // console.log(findName)
                            analysisParams.push(values)
                            setAnalysisParams(analysisParams)
                            onChange(analysisParams)
                        } else {
                            setAnalysisParams([values])
                            onChange([values])
                        }
                        form.resetFields()


                        // console.log(values)



                    } else {
                        setAnalysisParams(values)
                        onChange(values)

                    }
                    // console.log(values)
                    setOpenForm(false)
                }}>确认</Button>
                {/* <Button onClick={getCompareAbundance}>提交</Button>  */}

                <Button onClick={() => {
                    setAnalysisParams([])
                    setOpenForm(false)
                    onChange(analysisParams)
                }}>清除</Button>
            </>}
            <div>
                {(analysisParams && Array.isArray(analysisParams)) ? analysisParams.map((item: any, index: any) => (<div key={index}>
                    <Typography>
                        <pre>{JSON.stringify(item, null, 2)}</pre>
                    </Typography>
                    <a onClick={() => {
                        const analysisParamsFilter = analysisParams.filter((it: any) => it.id != item.id)
                        setAnalysisParams(analysisParamsFilter)
                        onChange(analysisParamsFilter)
                    }}>删除</a>
                </div>)) : <>
                    <Typography>
                        <pre>{JSON.stringify(analysisParams, null, 2)}</pre>
                    </Typography>
                    <a onClick={() => {
                        onChange(undefined); setAnalysisParams(undefined)
                    }}>清除</a>
                </>}
            </div>
        </Modal>
        {contextHolder}
    </>
}

export default AnalysisResultInput