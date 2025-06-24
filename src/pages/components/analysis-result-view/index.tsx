import { Button, Input, Popover, Spin, Table, Image, Typography, Collapse, Flex } from "antd";
import TextArea from "antd/es/input/TextArea";
import { FC, useEffect, useState } from "react";
import Markdown from '../markdown'
export const TableView: FC<any> = ({ data, url }) => {
    const { Search } = Input;
    const [tableData, setTableData] = useState<any>([])
    const getColumns = (data: any) => {
        return Object.keys(data).map(it => {
            return {
                title: it,
                dataIndex: it,
                key: it,
                ellipsis: true,
                width: 150,
            }
        })
    }
    useEffect(() => {
        // console.log()
        if (data) {
            // console.log(data)
            const dataWithKey = data.map((item: any, index: any) => ({ ...item, key: index }));
            setTableData(dataWithKey)
        }

    }, [data])
    return <>
        {Array.isArray(tableData) && <>
            <Table
                title={() => <>
                    <Search
                        placeholder="input search text"
                        allowClear
                        onSearch={(value: any) => {
                            // console.log(data?.table)
                            const filterData = data.filter((it: any) => Object.values(it).some(val =>
                                typeof val === "string" && val.includes(value)
                            ))
                            setTableData(filterData)
                        }}
                        style={{ width: 304 }}
                    />

                    {url && <Popover title={`${window.location.origin}${url}`}><Button onClick={() => {
                        window.open(url, "_blank")
                    }} style={{ marginLeft: "1rem" }} type="primary">下载</Button></Popover>}
                </>}
                // showHeader={()=>{}}
                scroll={{ x: 'max-content', y: 55 * 5 }}
                dataSource={tableData}
                columns={getColumns(data[0])}
                footer={() => `一共${data.length}条记录`}
            ></Table>

        </>}

    </>
}

const ImgView: FC<any> = ({ data, url }) => {
    return <div >
        <div style={{ textAlign: "center" }}>

            <Image src={data} style={{ maxWidth: "20rem", marginRight: "0.5rem" }}></Image>

            {url && <div>
                <Popover title={`${window.location.origin}${url}`}>
                    <Button onClick={() => { window.open(url, "_blank") }} type="primary">下载</Button>
                </Popover>
            </div>}

        </div>


    </div>
}
const { Paragraph } = Typography;

const StringView: FC<any> = ({ data }) => {

    return <>
        <Paragraph style={{ background: "#13c2c2", padding: "1rem", border: "1px solid #1677ff" }}>{data}</Paragraph>
    </>
}
const HtmlView: FC<any> = ({ data}) => {

    return <>
        {data && data.startsWith("/brave") ? <>
            <iframe src={data} width={"100%"} style={{ height: "80vh", border: "none" }}>
            </iframe>
        </>:<>{data}</>}

    </>
}
const AnalysisResultView: FC<any> = ({ htmlUrl, plotLoading, filePlot, tableDesc }) => {

    const componentMap: any = {
        table: TableView,
        string: StringView,
        html: HtmlView
    };

    const ComponentsRender = ({ type, ...rest }: any) => {
        const Component = componentMap[type] || (() => <div>未知类型 {type}</div>)
        return <Component {...rest} />;
    }
    return <>
        {htmlUrl && <>
            <iframe src={htmlUrl} width={"100%"} style={{ height: "80vh", border: "none" }}>
            </iframe>
            {/* {tableDesc && <>
                            <ReactMarkdown children={tableDesc} remarkPlugins={[remarkGfm]}></ReactMarkdown>
                        </>} */}
        </>}
        <Spin spinning={plotLoading} tip="请求中..." >
            {filePlot ? <>
                {/* {filePlot.img} */}


                {filePlot.img && <div style={{ display: "flex", justifyContent: "flex-start" }}>
                    {

                        Array.isArray(filePlot.img) ? <>
                            {filePlot.img.map((it: any, index: any) => (<>
                                <ImgView {...it} key={index}></ImgView>
                            </>))}
                        </> :
                            <>
                                <ImgView {...filePlot.img}></ImgView>
                                {/* <Image src={filePlot.img.data} style={{ maxWidth: "20rem" }}></Image> */}

                            </>
                    }
                </div>}
                {filePlot.dataList && Array.isArray(filePlot.dataList) && <>
                    {filePlot.dataList.map((item: any, index: any) => (
                      <ComponentsRender key={index} {...item}></ComponentsRender>
                        // <div key={index}>
                        //     {typeof item == 'string' ?
                        //         <TextArea value={item} rows={10}></TextArea>
                        //         :
                        //         <TableView data={item}></TableView>
                        //     }
                        // </div>

                    ))}
                </>}

                {filePlot.data && Array.isArray(filePlot.data) && <>
                    <TableView data={filePlot.data}></TableView>
                </>}
                {/* : <Typography >
                    {typeof filePlot.data == 'string' ? <TextArea value={filePlot.data} rows={10}></TextArea>
                        :
                        <pre>{JSON.stringify(filePlot.data, null, 2)}</pre>
                    }
                </Typography> */}

            </> : <div style={{ height: "100px" }}></div>}
        </Spin>

        {tableDesc && <>
            <Collapse ghost items={[
                {
                    key: "1",
                    label: "说明",
                    children: <>
                        <Markdown data={tableDesc}></Markdown>
                    </>
                }
            ]} />
        </>}

    </>
}

export default AnalysisResultView