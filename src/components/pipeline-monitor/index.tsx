import { Button, Card, Table } from "antd"
import axios from "axios"
import { FC, useEffect, useState } from "react"
import { useSelector } from "react-redux"
import { useOutletContext } from "react-router";
type SSEContextType = {
    eventSource: EventSource | null;
};
const PipelineMonitor: FC<any> = ({ analysisId }) => {
    if (!analysisId) return null
    const [data, setData] = useState<any>()
    // const sseData = useSelector((state: any) => state.global.sseData)
    const { eventSource } = useOutletContext<SSEContextType>();
    useEffect(() => {
        if (!eventSource) return;

        const handler = (event: MessageEvent) => {
            const data = JSON.parse(event.data)
            if (data.msgType == "trace") {
                loadData()
                console.log('子组件监听:', data);
            }

        };

        eventSource.addEventListener('message', handler);

        return () => {
            eventSource.removeEventListener('message', handler);
        };
    }, [eventSource]);
    const loadData = async () => {
        const resp = await axios.get(`/monitor-analysis/${analysisId}`)
        setData(resp.data)
    }
    useEffect(() => {
        loadData()
        // console.log(sseData)
    }, [analysisId])
    return <>
        <Card title="流程监控" extra={<><Button onClick={loadData} type="primary">刷新</Button></>}>
            {/* {JSON.stringify(data)} */}
            {/* {JSON.stringify(sseData)} */}

            {data && <>
                <Card style={{marginBottom:"1rem"}}>
                   已完成数量: { data?.total}
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

        </Card>
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

export default PipelineMonitor