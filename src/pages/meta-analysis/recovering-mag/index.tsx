import { Button, Tabs } from "antd"
import { FC } from "react"
import AnalysisPanel from '../../../components/analysis-sotware-panel'
import { Bowtie2 } from '../../software-components/bowtie2'
import { formatUrl } from '@/utils/utils'

const RecoveringMag: FC<any> = () => {

    return <>
        <Tabs items={[
            {
                key: "ngs_individual_assembly",
                label: "二代测序宏基因组单独组装",
                children: <>
                    <AnalysisPanel
                        inputAnalysisMethod={[
                            {
                                name: "remove_hosts_reads",
                                label: "remove_hosts_reads",
                                inputKey: ["samtools_remove_hosts"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField: "sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }, {
                                name: "clean_reads",
                                label: "clean_reads",
                                inputKey: ["fastp_clean_reads"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField: "sample_group",
                                // rules: [{ required: true, message: '该字段不能为空!' }],
                            },

                        ]}
                        analysisPipline="pipeline_ngs_individual_metawrap_assembly"
                        analysisMethod={[
                            {
                                name: "metawrap_assembly",
                                label: "metawrap_assembly",
                                inputKey: ["metawrap_assembly"],
                                mode: "multiple"
                            }
                        ]} analysisType="sample" >
                        <Metawrap></Metawrap>
                    </AnalysisPanel>
                </>
            },{
                key: "ngs_co_assembly",
                label: "二代测序宏基因组共组装",
                children: <>
                    <AnalysisPanel
                        inputAnalysisMethod={[
                            {
                                name: "remove_hosts_reads",
                                label: "remove_hosts_reads",
                                inputKey: ["samtools_remove_hosts"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField: "sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }, {
                                name: "clean_reads",
                                label: "clean_reads",
                                inputKey: ["fastp_clean_reads"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField: "sample_group",
                                // rules: [{ required: true, message: '该字段不能为空!' }],
                            },

                        ]}
                        analysisPipline="pipeline_ngs_individual_metawrap_assembly"
                        analysisMethod={[
                            {
                                name: "metawrap_assembly",
                                label: "metawrap_assembly",
                                inputKey: ["metawrap_assembly"],
                                mode: "multiple"
                            }
                        ]} analysisType="sample" >
                        <Metawrap></Metawrap>
                    </AnalysisPanel>
                </>
            }
        ]}></Tabs>

        <p>

        </p>
    </>
}

export default RecoveringMag

const Metawrap: FC<any> = ({ plot, record }) => {

    return <>
        {record && <>
            <Button onClick={() => {
                plot({
                    url: formatUrl(record.content.html),
                    tableDesc: ``
                })
            }}
            >查看报告</Button>
        </>}

    </>
}