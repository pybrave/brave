import { Tabs } from "antd"
import { FC } from "react"
import AnalysisPanel from '../../../components/analysis-sotware-panel'
import { Bowtie2Paired } from '../../software-components/bowtie2'
const ReadsBasedAbundanceAnalysis: FC<any> = () => {

    return <>
        <Tabs items={[
            {
                key: "bowtie2_align_host",
                label: "比对到比对到宿主基因组",
                children: <>
                    <AnalysisPanel
                        inputAnalysisMethod={[
                            {
                                name: "clean_reads",
                                label: "clean reads",
                                inputKey: ["fastp_clean_reads"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField:"sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }
                        ]}
                        upstreamFormJson={[
                            {
                                name: "genome_index",
                                dataKey:"host_genome_index",
                                label: "宿主基因组",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                                type: "BaseSelect",
                            }
                        ]}
                        analysisPipline="bowtie2_remove_host"
                        analysisMethod={[
                            {
                                name: "bowtie2_align_host",
                                label: "bowtie2_align_host",
                                inputKey: ["bowtie2_align_host"],
                                mode: "multiple"
                            },  {
                                name: "samtools_remove_hosts",
                                label: "samtools_remove_hosts",
                                inputKey: ["samtools_remove_hosts"],
                                mode: "multiple"
                            }
                        ]} analysisType="sample" >
                        <Bowtie2Paired analysisKey="bowtie2_align_host"></Bowtie2Paired>
                    </AnalysisPanel>
                </>
            },
            //  {
            //     key: "samtools_clean_reads",
            //     label: "clean reads",
            //     children: <>
            //         <AnalysisPanel
            //             analysisMethod={[
            //                 {
            //                     key: "samtools_remove_hosts",
            //                     name: "samtools_remove_hosts",
            //                     value: ["samtools_remove_hosts"],
            //                     mode: "multiple"
            //                 }
            //             ]}
            //             analysisPipline="pipeline_samtools_clean_reads"
            //             inputAnalysisMethod={[
            //                 {
            //                     key: "bowtie2_align_host",
            //                     name: "bowtie2_align_host",
            //                     value: ["bowtie2_align_host"],
            //                     mode: "multiple"
            //                 }
            //             ]} analysisType="sample" >
            //             <Bowtie2Paired analysisKey="bowtie2_align_host"></Bowtie2Paired>
            //         </AnalysisPanel>
            //     </>
            // }
        ]}></Tabs>

        <p>

        </p>
    </>
}

export default ReadsBasedAbundanceAnalysis