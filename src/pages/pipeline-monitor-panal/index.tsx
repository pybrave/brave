import AnalysisList from "@/components/analysis-list"
import { FC } from "react"
import { useOutletContext } from "react-router"

const PielineMonitorPanal: FC<any> = () => {
    const { project } = useOutletContext<any>()

    return <div style={{ maxWidth: "1500px", margin: "1rem auto" }}>
        <AnalysisList
            project={project}
            setRecord={(record: any) => {
                // const param = JSON.parse(record.request_param)
                // console.log(param)
                // upstreamForm.resetFields()
                // upstreamForm.setFieldsValue(param)
                // if (record?.id) {
                //     upstreamForm.setFieldValue("id", record?.id)
                // }
                // record['dataType'] = "analysis"
                // onClickItem(record)
            }}></AnalysisList>
    </div>
}

export default PielineMonitorPanal

