import { Button, Card } from "antd"
import axios from "axios"
import { FC, useEffect, useState } from "react"

const PipelineMonitor: FC<any> = ({ pipelineId }) => {
    if (!pipelineId) return null
    const [data, setData] = useState<any>()
    const loadData = async () => {
        const resp = await axios.get(`/monitor-pipeline/${pipelineId}`)
        setData(resp.data)
    }
    useEffect(() => {
        loadData()
    }, [])
    return <>
        <Card title="流程监控" extra={<><Button onClick={loadData} type="primary">刷新</Button></>}>
            {JSON.stringify(data)}
        </Card>

    </>
}

export default PipelineMonitor