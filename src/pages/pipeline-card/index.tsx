import { Button, Card, Col, Empty, Flex, message, Popconfirm, Row, Tag, Tooltip } from "antd"
import Item from "antd/es/list/Item"
import { FC, useEffect, useState } from "react"
import { useDispatch, useSelector } from "react-redux"
import { useNavigate, useOutletContext, useParams } from "react-router"
import { DeleteOutlined } from '@ant-design/icons';

import Meta from "antd/es/card/Meta"
import { colors } from '@/utils/utils'
import { listPipeline } from '@/api/pipeline'
import axios from "axios"
const PipelineCard: FC<any> = () => {
    const { project } = useOutletContext<any>()
    const [menu, setMenu] = useState<any>([])
    const navigate = useNavigate();
    const dispatch = useDispatch()
    const [messageApi, contextHolder] = message.useMessage();

    const menuItems = useSelector((state: any) => state.menu.items)

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
        listPipeline(dispatch)
    }
    useEffect(() => {
        const menu = menuItems.map((group: any) => ({
            name: group.name,
            items: group.items.map((item: any) => ({
                key: `${item.path}`,
                label: item.name,
                img: item.img,
                tags: item.tags,
                description: item.description,
                category: item.category
            }))
        }));
        // const itmes = menuItems.pipeline.map((item: any) => {
        //     return {
        //         key: `${project}/${item.path}`,
        //         label: item.name,
        //         img: item.img,
        //         tags: item.tags,
        //         description: item.description,
        //         category:item.category
        //     }
        // })


        // const newMeanu = {
        //     name: "组件化流程(开发中...)",
        //     items: itmes
        // }
        // const menu = [newMeanu]
        setMenu(menu)
        // console.log(menu)
    }, [JSON.stringify(menuItems)])

    // indivi
    return <div style={{ maxWidth: "1500px", margin: "1rem auto" }}>
        {contextHolder}
        <Flex justify="flex-end" gap="small">
            <Button color="cyan" variant="solid">创建流程</Button>
            
            <Popconfirm title="是否安装?" onConfirm={async () => {
                await axios.post("/import-pipeline")
                messageApi.success("安装成功!")
                loadPipeine()
            }}>
                <Button color="cyan" variant="solid">从本地安装</Button>
            </Popconfirm>

            <Button color="cyan" variant="solid" onClick={loadPipeine}>刷新</Button>
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
                                <Popconfirm title="是否删除?" onConfirm={(e: any) => {
                                    e.stopPropagation();
                                }} onCancel={(e: any) => { e.stopPropagation() }} >
                                    <DeleteOutlined
                                        onClick={(e) => {
                                            e.stopPropagation(); // 阻止卡片点击事件触发
                                            // 这里写删除逻辑
                                        }}
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