import { Card, Col, Pagination, Row, Typography, Image, Flex, Button, Spin, Tag, Popconfirm, Empty } from "antd";
import axios from "axios"
import { FC, useEffect, useState } from "react"
const { Title, Text, Paragraph } = Typography;
import { colors } from '@/utils/utils'

const Literature: FC<any> = ({ params }) => {
    const [data, setData] = useState<any>([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState<boolean>(false)
    const pageSize = 6;

    const loadData = async () => {
        setLoading(true)
        const resp = await axios.post("/literature", {
            ...params,
            page_number: page,
            page_size: pageSize,
        });
        setLoading(false)
        setData(resp.data.items);
        setTotal(resp.data.total);
    };

    const importLiterature = async () => {
        setLoading(true)
        await axios.post("/literature/import")
        loadData()
        setLoading(false)
    }

    useEffect(() => {
        loadData()
    }, [page, JSON.stringify(params)])
    return <>
        <Flex justify="flex-end" gap="small">
            <Button color="cyan" variant="solid" onClick={loadData}>刷新</Button>
            <Popconfirm title="Are you sure to import literature?" onConfirm={importLiterature}>
                <Button color="cyan" variant="solid">导入</Button>
            </Popconfirm>
        </Flex>
        <div style={{ maxWidth: "1000px", margin: "1rem auto" }}>
            <Spin spinning={loading}>
                {total != 0 ?
                    <Row gutter={[16, 16]}>
                        {data.map((item: any) => (
                            <Col span={24} key={item.id}>
                                <Card
                                    styles={{ body: { padding: 12 } }}
                                    hoverable
                                    style={{ borderRadius: 12 }}

                                >
                                    <Row gutter={16}>
                                        {/* 左侧图片区域 */}
                                        {item.img && <Col span={6}>
                                            {item.img && (
                                                <Image
                                                    src={item.img}
                                                    alt="literature"
                                                    style={{
                                                        width: "100%",
                                                        // height: 160,
                                                        objectFit: "cover",
                                                        borderRadius: 8,
                                                    }}
                                                />
                                            )}
                                        </Col>}


                                        {/* 右侧文本内容区域 */}
                                        <Col span={item.img ? 18 : 24}>
                                            <Title level={5} style={{ marginBottom: 4, marginTop: 0 }}>
                                                <span style={{ display: "block", color: "gray", fontSize: "0.5rem" }}>{item.literature_key}</span>
                                                期刊 {item.journal || "未知"} 时间 {item.publish_date || "-"}
                                                <a href={item.url} target="_blank">来源</a>
                                                {/* 影响因子 {item.impact || "?"} 时间 {item.year || "-"} */}
                                            </Title>
                                            <Paragraph style={{ marginBottom: 8 }}>
                                                {/* {item.content} */}
                                                {highlightKeywords(item.content || "", item.keywords || [])}
                                            </Paragraph>
                                            <Paragraph>
                                                {/* <span style={{ color: "red", fontWeight: 500 }}>翻译：</span> */}
                                                {highlightKeywords(item.translate || "", item.keywords || [])}
                                            </Paragraph>
                                            {item.keywords && Array.isArray(item.keywords) && item.keywords.map((tag: any, index: any) => (
                                                <Tag key={index} color={colors[index]}>{tag}</Tag>
                                            ))}
                                        </Col>
                                    </Row>
                                </Card>
                            </Col>
                        ))}
                    </Row> :
                    <Empty description={"暂无相关资料!"}></Empty>
                }

            </Spin>

            {total != 0 && <div style={{ textAlign: "center", marginTop: 24 }}>
                <Pagination
                    current={page}
                    pageSize={pageSize}
                    total={total}
                    onChange={(p) => setPage(p)}
                    showSizeChanger={false}
                />
            </div>}

        </div>
    </>
}
// 高亮关键词
function highlightKeywords(text: string, keywords: string[]) {
    const lowerKeywords = keywords.map(k => k.toLowerCase());
    const parts = text.split(new RegExp(`(${keywords.join("|")})`, "gi"));

    return parts.map((part, i) =>
        lowerKeywords.includes(part.toLowerCase()) ? (
            <span key={i} style={{ color: "red", fontWeight: 600 }}>
                {part}
            </span>
        ) : (
            part
        )
    );
}
export default Literature