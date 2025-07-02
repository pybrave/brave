import { Button, Card, Flex, Table, Tabs, Tag } from "antd"
import Typography from "antd/es/typography/Typography";
import axios from "axios"
import { FC, useEffect, useState } from "react"
import { useSelector } from "react-redux"
import { useOutletContext } from "react-router";
import { SyncOutlined, MinusCircleOutlined } from '@ant-design/icons';

type SSEContextType = {
    eventSource: EventSource | null;
};
const PipelineMonitor: FC<any> = ({ data }) => {

    return <>
        {/* {JSON.stringify(data)} */}
        {/* {JSON.stringify(sseData)} */}

        {data && <>
            <Card style={{ marginBottom: "1rem" }}>
                <Flex gap={"small"}>
                    <p>已完成数量: {data?.total} </p>
                    <p>状态: {data.status == "running" ? <>运行中({data.process_id})<Tag icon={<SyncOutlined spin />} color="processing"></Tag></> :
                        <>运行结束<Tag icon={<MinusCircleOutlined />} color="processing"></Tag></>}
                    </p>
                </Flex>

            </Card>
            <Table dataSource={data?.traceTable} rowKey={(row: any) => row.hash} columns={[
                {
                    title: 'hash',
                    dataIndex: 'hash',
                    key: 'hash',
                    ellipsis: true,
                }, {
                    title: 'name',
                    dataIndex: 'name',
                    key: 'name',
                    ellipsis: true,
                }, {
                    title: 'tag',
                    dataIndex: 'tag',
                    key: 'tag',
                    ellipsis: true,
                }, {
                    title: 'status',
                    dataIndex: 'status',
                    key: 'status',
                    ellipsis: true,
                }, {
                    title: 'realtime',
                    dataIndex: 'realtime',
                    key: 'realtime',
                    ellipsis: true,
                },
            ]}></Table>
        </>}

        {/* %cpu:
"2867.4%"
%mem:
"0.8%"
cpus:
30
exit:
0
hash:
"2b/0eb520"
memory:
"50 GB"
name:
"bowtie2 (MTF-18)"
name.1:
"bowtie2 (MTF-18)"
native_id:
3356273
read_bytes:
"668.4 MB"
realtime:
"2m 49s"
rss:
"3.9 GB"
status:
"COMPLETED"
tag:
"MTF-18"
task_id:
6
vmem:
"8.5 GB"
write_bytes:
"6.1 GB" */}
    </>
}

const PipelineParams: FC<any> = ({ data, type }) => {

    if (type == "params") {
        return <>
            <Typography>
                <pre>
                    {JSON.stringify(data, null, 2)}
                </pre>
            </Typography>
        </>
    } else {
        return <>

            <Typography>
                <pre>
                    {data}
                </pre>
            </Typography>

        </>
    }

}
const PipelineInfo: FC<any> = ({ analysisId ,onClose}) => {

    if (!analysisId) return null
    const [data, setData] = useState<any>()
    const [activeTabKey, setActiveTabKey] = useState<any>("trace")
    const { eventSource } = useOutletContext<SSEContextType>();
    useEffect(() => {
        if (!eventSource) return;

        const handler = (event: MessageEvent) => {
            const data = JSON.parse(event.data)
            console.log(data)
            if (data.analysis_id == analysisId) {
                if ((data.msgType == "trace" || data.msgType == "process_end" ) && activeTabKey == "trace") {
                    loadData(activeTabKey)
                    console.log('子组件监听trace || process_end:', data);
                } else if (data.msgType == "workflow_log" && activeTabKey == "workflow_log") {
                    loadData(activeTabKey)
                    console.log('子组件监听: workflow_log', data);
                }
            }


        };

        eventSource.addEventListener('message', handler);

        return () => {
            console.log("removeEventListener")
            eventSource.removeEventListener('message', handler);
        };
    }, [eventSource]);
    const loadData = async (type: any) => {
        console.log(type)
        const resp = await axios.get(`/monitor-analysis/${analysisId}?type=${type}`)
        setData(resp.data)
    }
    const onTabChange = (key: any) => {
        // console.log(key)
        setData(undefined)
        setActiveTabKey(key)
        loadData(key)
    }
    useEffect(() => {
        loadData(activeTabKey)
    }, [analysisId])
    const componentMap: any = {
        trace: PipelineMonitor,
        params: PipelineParams,
        workflow_log: PipelineParams,
        executor_log: PipelineParams,
        script_config: PipelineParams
    }
    const ComponentsRender = (params: any) => {
        const Component = componentMap[activeTabKey] || (() => <div>未知类型</div>);
        return <Component {...params}></Component>
    }
    return <>
        <Card
            title={`流程监控(${analysisId})`}
            tabList={[
                {
                    key: "trace",
                    label: "流程监控"
                }, {
                    key: "params",
                    label: "流程参数"
                }, {
                    key: "workflow_log",
                    label: "流程日志"
                }, {
                    key: "executor_log",
                    label: "运行日志"
                }, {
                    key: "script_config",
                    label: "配置文件"
                }
            ]}
            activeTabKey={activeTabKey}
            onTabChange={onTabChange}
            extra={<>
            <Button style={{marginRight:"0.5rem"}} onClick={() => loadData(activeTabKey)} type="primary">刷新</Button>
            <Button onClick={onClose} type="primary">关闭</Button>
            </>}>

            {/* {JSON.stringify(data)} */}
            <ComponentsRender data={data} type={activeTabKey}></ComponentsRender>

        </Card>

        {/* <Tabs items={[
            {
                key: "1",
                label: "流程监控",
                children: <PipelineMonitor data={data}></PipelineMonitor>
            }, {
                key: "2",
                label: "流程参数",
                children: <PipelineParams {...params} type="params"></PipelineParams>
            }, {
                key: "3",
                label: "运行日志",
                children: <PipelineParams {...params} type="workflow_log" ></PipelineParams>
            }, {
                key: "4",
                label: "程序日志",
                children: <PipelineParams {...params} type="executor_log" ></PipelineParams>
            }
        ]}></Tabs> */}
    </>
}
export default PipelineInfo