import { Button, Card, Col, Empty, Flex, message, notification, Popconfirm, Row, Tag, Tooltip } from "antd"
import Item from "antd/es/list/Item"
import { FC, useEffect, useState } from "react"
import { useDispatch, useSelector } from "react-redux"
import { useNavigate, useOutletContext, useParams } from "react-router"
import { DeleteOutlined, EditOutlined } from '@ant-design/icons';

import Meta from "antd/es/card/Meta"
import { colors } from '@/utils/utils'
import { listPipeline } from '@/api/pipeline'
import { CreateOrUpdatePipelineComponent } from '@/components/create-pipeline'
import axios from "axios"
import { useModal } from "@/hooks/useModal"

const PipelineCard: FC<any> = () => {
    const { project } = useOutletContext<any>()
    const [menu, setMenu] = useState<any>([])
    const [createOpen, setCreateOpen] = useState<any>(false)
    const [record, setRecord] = useState<any>()

    const navigate = useNavigate();
    const dispatch = useDispatch()
    const [messageApi, contextHolder] = message.useMessage();
    const { modal, openModal, closeModal } = useModal();

    // const menuItems = useSelector((state: any) => state.menu.items)
    const sseData = useSelector((state: any) => state.global.sseData)

    const menu1: any[] = [
        {
            name: "样本前处理",
            items: [
                {
                    key: `${project}/sample-qc`,
                    label: "样本质控",
                    img: "/mvp-api/img/pipeline.jpg"
                }
            ]
        },
        {
            name: "宏基因组流程",
            items: [
                {
                    key: `${project}/meta_genome/remove-host`,
                    label: "去宿主",
                    img: "/mvp-api/img/pipeline.jpg"
                }, {
                    key: `${project}/meta_genome/reads-based-abundance-analysis`,
                    label: "基于Reads的丰度分析",
                    img: "/mvp-api/img/pipeline.jpg"
                }, {
                    key: `${project}/meta_genome/recovering-mag`,
                    label: "重构MAG",
                    img: "/mvp-api/img/pipeline.jpg"
                }, {
                    key: `${project}/meta_genome/abundance-meta`,
                    label: "丰度分析",
                    img: "/mvp-api/img/pipeline.jpg"
                }, {
                    key: `${project}/meta_genome/function-analysis`,
                    label: "功能分析",
                    img: "/mvp-api/img/pipeline.jpg"
                }, {
                    key: `${project}/meta_genome/abundance`,
                    label: "old丰度分析",
                    img: "/mvp-api/img/pipeline.jpg"
                }
            ]
        }, {
            name: "单菌流程",
            items: [
                // {
                //     key: `${project}/single_genome`,
                //     label: "项目介绍"
                // }, {
                //     key: `${project}/single_genome/sample`,
                //     label: "检测样本"
                // }, 
                {
                    key: `${project}/single_genome/assembly`,
                    label: "单菌组装",
                    img: "/mvp-api/img/pipeline.jpg"
                }, {
                    key: `${project}/single_genome/gene-prediction`,
                    label: "基因预测",
                    img: "/mvp-api/img/pipeline.jpg"
                }, {
                    key: `${project}/single_genome/gene-annotation`,
                    label: "基因注释",
                    img: "/mvp-api/img/pipeline.jpg"
                }, , {
                    key: `${project}/single_genome/gene-expression`,
                    label: "基因表达",
                    img: "/mvp-api/img/pipeline.jpg"
                },
                {
                    key: `${project}/single_genome/mutation`,
                    label: "突变检测",
                    img: "/mvp-api/img/pipeline.jpg"
                }, {
                    key: `${project}/single_genome/mutation-compare`,
                    label: "突变比较",
                    img: "/mvp-api/img/pipeline.jpg"
                }
            ]
        },
    ]
    const loadPipeine = async () => {
        const data: any = await listPipeline(dispatch)
        console.log(data)
        const menu = data.map((group: any) => ({
            name: group.name,
            items: group.items.map((item: any) => {
                const { path, name, ...rest } = item
                return {
                    key: `pipeline/${path}`,
                    label: name,
                    ...rest
                }
            })
        }));

        setMenu(menu)
    }
    const datelePipeline = async (pipelineId: any) => {
        try {
            const resp = await axios.delete(`/delete-pipeline/${pipelineId}`)
            messageApi.success("删除成功!")
            loadPipeine()
        } catch (error: any) {
            console.log(error)
            messageApi.error(`删除失败!${error.response.data.detail}`)
        }
    }
    useEffect(() => {
        loadPipeine()
        // console.log(menu)
    }, [])

    // indivi
    return <div style={{ maxWidth: "1500px", margin: "1rem auto" }}>
        {contextHolder}
        {JSON.stringify(sseData)}
        <Flex justify="flex-end" gap="small">
            <Button color="cyan" variant="solid" onClick={() => {
               
                openModal("modalA", {
                    data: undefined,
                    structure: {
                        component_type: "pipeline",
                    }
                })
            }}>创建流程</Button>

            <Popconfirm title="是否安装?" onConfirm={async () => {
                await axios.post("/import-pipeline")
                messageApi.success("安装成功!")
                loadPipeine()
            }}>
                <Button color="cyan" variant="solid">从本地安装</Button>
            </Popconfirm>

            <Button color="primary" variant="solid" onClick={loadPipeine}>刷新</Button>
        </Flex>
        {Array.isArray(menu) && menu.length != 0 ? menu.map((menuItem: any, menuIndex: any) => (
            <div key={menuIndex}>
                <h2>{menuItem.name}</h2>
                <hr />
                <Row gutter={16} style={{ position: "relative" }}>
                    {menuItem?.items.map((item: any, index: any) => (
                        <Col key={index} lg={4} sm={6} xs={24} style={{ marginBottom: "1rem", cursor: "pointer" }}>
                            <Card hoverable
                                // title={item.label}
                                // variant="borderless" 
                                style={{
                                    height: "100%"
                                }}
                                cover={<img alt={item.label} src={item.img} />}
                                onClick={() => navigate(`/${item.key}`)}>


                                <Meta title={item.label} description={item?.description} style={{ marginBottom: "1rem" }} />
                                {item.tags && Array.isArray(item.tags) && item.tags.map((tag: any, index: any) => (
                                    <Tooltip key={index} title={tag}>
                                        <Tag style={{
                                            wordBreak: "break-word",
                                            whiteSpace: "nowrap",
                                            overflow: "hidden",
                                            textOverflow: "ellipsis",
                                            maxWidth: 100,
                                            display: "inline-block",
                                            cursor: "default"
                                        }} color={colors[index]}>{tag}</Tag>
                                    </Tooltip>

                                ))}
                                <EditOutlined
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        openModal("modalA", {
                                            data: item,
                                            structure: {
                                                component_type: "pipeline",
                                            }
                                        })
                                        // setCreateOpen(true)
                                        // console.log(item)
                                        // setRecord(item)
                                    }}
                                    style={{
                                        position: "absolute",
                                        right: 40,
                                        bottom: 10,
                                        fontSize: 15,
                                        color: "rgba(0,0,0,0.45)",
                                        cursor: "pointer",
                                    }}
                                />
                                <Popconfirm title="是否删除?" onConfirm={(e: any) => {
                                    e.stopPropagation();
                                    datelePipeline(item.pipeline_id)
                                }} onCancel={(e: any) => { e.stopPropagation() }} >
                                    <DeleteOutlined
                                        onClick={(e) => e.stopPropagation()}
                                        style={{
                                            position: "absolute",
                                            right: 10,
                                            bottom: 10,
                                            fontSize: 15,
                                            color: "rgba(0,0,0,0.45)",
                                            cursor: "pointer",
                                        }}
                                    />
                                </Popconfirm>
                            </Card>
                        </Col>
                    ))}

                </Row>
            </div>
        )) : <Empty></Empty>}
        {/* <CreatePipeline
            callback={loadPipeine}
            pipelineStructure={{
                pipeline_type: "wrap_pipeline",
                parent_pipeline_id: "0"

            }}
            open={createOpen}
            setOpen={setCreateOpen}
            data={record}></CreatePipeline> */}

        <CreateOrUpdatePipelineComponent
            callback={loadPipeine}
            // pipelineStructure={pipelineStructure}
            // data={record}
            visible={modal.key == "modalA" && modal.visible}
            onClose={closeModal}
            params={modal.params}></CreateOrUpdatePipelineComponent>
        {import.meta.env.MODE == "development" &&
            <>
                <br /><br /><br /><br /><br /><br />

                {menu1.map((menuItem: any, menuIndex: any) => (
                    <div key={menuIndex}>
                        <h2>{menuItem.name}</h2>
                        <hr />
                        <Row gutter={16}>
                            {menuItem?.items.map((item: any, index: any) => (
                                <Col key={index} lg={4} sm={6} xs={24} style={{ marginBottom: "1rem", cursor: "pointer" }}>
                                    <Card hoverable
                                        // title={item.label}
                                        // variant="borderless" 
                                        cover={<img alt={item.label} src={item.img} />}
                                        onClick={() => navigate(`/${item.key}`)}>


                                        <Meta title={item.label} description={item?.description} style={{ marginBottom: "1rem" }} />
                                        {item.tags && Array.isArray(item.tags) && item.tags.map((tag: any, index: any) => (
                                            <Tag key={index} color={colors[index]}>{tag}</Tag>
                                        ))}
                                    </Card>
                                </Col>
                            ))}

                        </Row>
                    </div>
                ))}


            </>

        }


    </div>
}

export default PipelineCard