import { Button, message, Tabs } from "antd"
import { FC } from "react"
import AnalysisPanel from '../../../components/analysis-sotware-panel'
import { Bowtie2 } from '../../software-components/bowtie2'
import axios from "axios"
import { useOutletContext, useParams } from "react-router"
import { formatUrl } from '@/utils/utils'


const ReadsBasedAbundanceAnalysis: FC<any> = () => {
    const [messageApi, contextHolder] = message.useMessage();
    const { project } = useOutletContext<any>()

    const fromSampleImport = async () => {
        const resp: any = await axios.post(`/fast-api/add-sample-analysis?project=${project}`)
        message.success("导入成功!")
    }
    return <>
        {contextHolder}
        <Tabs items={[
            {
                key: "ngs-sample-qc",
                label: "NGS样本质控",
                children: <>
                    <AnalysisPanel
                        cardExtra={<Button onClick={fromSampleImport}>从样本导入</Button>}
                        analysisMethod={[
                            {
                                name: "fastp_clean_reads",
                                label: "fastp_clean_reads",
                                inputKey: ["fastp_clean_reads"],
                                mode: "multiple"
                            }
                        ]} 
                        analysisPipline="ngs-sample-qc"
                        inputAnalysisMethod={[
                            {
                                name: "reads",
                                label: "reads",
                                inputKey: ["V1_meta_genome_NGS_DNA","V1_single_genome_NGS_DNA"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField:"sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }
                        ]} analysisType="sample" >
                        <Fastp></Fastp>
                    </AnalysisPanel>
                </>
            },
        ]}></Tabs>

        <p>

        </p>
    </>
}

export default ReadsBasedAbundanceAnalysis

const Fastp:FC<any> = ({ plot, record }) => {

    return <>
        {record && <>
            <Button onClick={() => {
                plot({
                    url: formatUrl(record.content.html),
                    tableDesc: ``
                })
            }}
            >查看报告({record.sample_name})</Button>
        </>}

    </>
}