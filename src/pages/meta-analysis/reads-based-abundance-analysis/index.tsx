import { Button, Tabs } from "antd"
import { FC } from "react"
import AnalysisPanel from '../../components/analysis-panel'
import { Bowtie2 } from '../../software-components/bowtie2'
import { Metaphlan } from './metaphlan'
const ReadsBasedAbundanceAnalysis: FC<any> = () => {

    return <>
        <Tabs items={[
            {
                key: "bowtie2_align_metaphlan",
                label: "比对到metaphlan marker库",
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
                        analysisPipline="pipeline_align_metaphlan_marker"
                        analysisMethod={[
                            {
                                name: "bowtie2_align_metaphlan",
                                label: "marker比对bam文件",
                                inputKey: ["bowtie2_align_metaphlan"],
                                mode: "multiple"
                            },
                        ]} analysisType="sample" >
                        <Bowtie2></Bowtie2>
                    </AnalysisPanel>
                </>
            }
            , {
                key: "abundance_estimation ",
                label: "丰度估计",
                children: <>
                    <AnalysisPanel
                        upstreamFormJson={[
                            {
                                name: "stat_q",
                                data: [
                                    {
                                        label: "0.2",
                                        value: 0.2
                                    }, {
                                        label: "0",
                                        value: 0
                                    }
                                ],
                                initialValue: 0.2,
                                label: " Quantile value for the robust average(--stat_q)",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                                type: "BaseSelect",
                            }
                        ]}
                        analysisMethod={[
                            {
                                name: "metaphlan_sam_abundance",
                                label: "metaphlan abundance",
                                inputKey: ["metaphlan_sam_abundance"],
                                mode: "multiple"
                            }
                        ]}
                        analysisPipline="pipeline_metaphlan_abundance"
                        inputAnalysisMethod={[
                            {
                                name: "bowtie2_align_metaphlan",
                                label: "marker比对bam文件",
                                inputKey: ["bowtie2_align_metaphlan"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField: "sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }
                        ]} analysisType="sample" >
                        <Metaphlan></Metaphlan>
                    </AnalysisPanel>
                </>
            }, {
                key: "consensus_marker",
                label: "consensus_marker",
                children: <>
                    <AnalysisPanel

                        inputAnalysisMethod={[
                            {
                                name: "bowtie2_align_metaphlan",
                                label: "marker比对bam文件",
                                inputKey: ["bowtie2_align_metaphlan"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField: "sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }
                        ]}
                        analysisPipline="pipeline_consensus_marker"
                        analysisMethod={[
                            {
                                name: "consensus_marker",
                                label: "consensus_marker",
                                inputKey: ["consensus_marker"],
                                mode: "multiple"
                            },
                        ]} analysisType="sample" >
                    </AnalysisPanel>
                </>
            }, {
                key: "strain_level_profiling",
                label: "strain_level_profiling",
                children: <>
                    <AnalysisPanel
                        upstreamFormJson={[
                            {
                                name: "clade",
                                label: "clade",
                                mode: "multiple",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                                type: "MetaphlanCladeSelect",
                            }
                        ]}
                        inputAnalysisMethod={[
                            {
                                name: "consensus_marker",
                                label: "consensus_marker",
                                inputKey: ["consensus_marker"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField: "sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }, {
                                name: "assembly_genome",
                                label: "assembly_genome",
                                inputKey: ["tgs_individual_assembly"],
                                mode: "single",
                                type: "BaseSelect",
                            }
                        ]}
                        analysisPipline="pipeline_strain_level_profiling"
                        analysisMethod={[
                            {
                                name: "strain_level_profiling",
                                label: "strain_level_profiling",
                                inputKey: ["strain_level_profiling"],
                            },
                        ]} analysisType="sample"
                        downstreamAnalysis={[
                            {
                                name: "菌株水平系统发育树",
                                analysisType: "one", // multiple or one
                                sampleGroupJSON: false,
                                paramsFun: (record: any) => {
                                    return {
                                        "best_tree": record.content.best_tree,
                                        "tree_pairwisedists": record.content.tree_pairwisedists,
                                    }

                                },
                                // formJson: [
                                //     {
                                //         name: "group_field",
                                //         label: "分组列",
                                //         rules: [{ required: true, message: '该字段不能为空!' }],
                                //         type: "GroupFieldSelect",
                                //     }, {
                                //         name: "treatment",
                                //         label: "处理组",
                                //         rules: [{ required: true, message: '该字段不能为空!' }],
                                //         type: "GroupSelectSampleButton",
                                //         group: "group_field",
                                //     }, {
                                //         name: "control",
                                //         label: "对照组",
                                //         rules: [{ required: true, message: '该字段不能为空!' }],
                                //         type: "GroupSelectSampleButton",
                                //         group: "group_field",
                                //     }, {
                                //         name: "rank",
                                //         label: "rank",
                                //         rules: [{ required: true, message: '该字段不能为空!' }],
                                //         type: "RankSelect"
                                //     }
                                // ],
                                // formDom: <AbundanceOtherForm></AbundanceOtherForm>,
                                sampleGroupApI: false,
                                saveAnalysisMethod: "strain_level_profiling_tree",
                                moduleName: "strain_level_profiling_tree",
                                sampleSelectComp: false,
                                tableDesc: ` `,

                            }
                        ]}
                    >

                    </AnalysisPanel>
                </>
            }
        ]}></Tabs>

        <p>

        </p>
    </>
}

export default ReadsBasedAbundanceAnalysis

const Strainphlan: FC<any> = ({ plot }) => {
    return <>
        <Button type="primary" onClick={() => {
            plot()

        }}>alpha多样性</Button >
    </>
}