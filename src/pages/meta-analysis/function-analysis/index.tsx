import { Tabs } from "antd"
import { FC } from "react"
import AnalysisPanel from '../../../components/analysis-sotware-panel'
import { Bowtie2Paired } from '../../software-components/bowtie2'
const ReadsBasedAbundanceAnalysis: FC<any> = () => {

    return <>
        <Tabs items={[
            {
                key: "function_analysis",
                label: "功能分析",
                children: <>
                    <AnalysisPanel
                        inputAnalysisMethod={[
                            {
                                name: "reads",
                                label: "去宿主后的reads",
                                inputKey: ["samtools_remove_hosts"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField:"sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            },   {
                                name: "abundance",
                                label: "metaphlan丰度文件",
                                inputKey: ["metaphlan_sam_abundance"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField:"sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }
                        ]}
                    
                        analysisPipline="pipeline_humann"
                        analysisMethod={[
                            {
                                name: "humann_profile",
                                label: "humann_profile",
                                inputKey: ["humann_profile"],
                                mode: "multiple"
                            },
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