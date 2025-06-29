import { Button, Form, Select, Tabs, Typography } from "antd"

import AnalysisPanel from "../../../components/analysis-sotware-panel"

import { FC, useEffect, useState } from "react"
import { json } from "stream/consumers"
const AbundanceAnalysis = () => {

    return <>
        <Tabs items={[

            // {
            //     key: "diversity-alpha0",
            //     label: "alpha多样性0",
            //     children: <AnalysisPanel analysisMethod={[
            //         {
            //             key: "metaphlan_sam_abundance_matrix",
            //             name: "metaphlan_sam_abundance_matrix",
            //             value: ["metaphlan_sam_abundance_matrix"],
            //             mode: "multiple"
            //         }
            //     ]} analysisType="sample" >
            //         {/* <Eggnog></Eggnog> */}
            //         <AbundanceAnalysisComp0></AbundanceAnalysisComp0>
            //     </AnalysisPanel>
            // },
            {
                key: "diversity-alpha",
                label: "丰度分析",
                children: <AnalysisPanel analysisMethod={[
                    {
                        name: "metaphlan_sam_abundance",
                        label: "metaphlan_sam_abundance",
                        inputKey: ["metaphlan_sam_abundance"],
                        mode: "multiple"
                    }
                ]} analysisType="sample" >
                    {/* <Eggnog></Eggnog> */}
                    <AbundanceAnalysisComp></AbundanceAnalysisComp>
                </AnalysisPanel>
            }
        ]}></Tabs>
    </>
}

export default AbundanceAnalysis

const AbundanceAnalysisComp0: FC<any> = ({ sampleGroup, record, resultTableList, plot }) => {

    return <>
        <Button type="primary" onClick={() => {
            plot({
                sampleGroupJSON: [
                    {
                        name: "treatment",
                        label: "处理组"
                    }, {
                        name: "control",
                        label: "对照组"
                    },
                ],
                sampleGroupApI: true,
                saveAnalysisMethod: "metaphlan_sam_abundance_matrix",
                moduleName: "abundance_matrix",
                sampleSelectComp: false,
                tableDesc: ` `
            })

        }}>alpha多样性</Button >

        {/* {JSON.stringify(sampleGroup)} */}
    </>
}


const AbundanceAnalysisComp: FC<any> = ({ sampleGroup, record, resultTableList, plot, dataMap }) => {

    return <>

        <Button type="primary" onClick={() => {
            plot({
                sampleGroupJSON:true,
                formJson: [
                    {
                        name: "group_field",
                        label: "分组列",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupFieldSelect",
                    }, {
                        name: "treatment",
                        label: "处理组",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    }, {
                        name: "control",
                        label: "对照组",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    },{
                        name: "rank",
                        label: "rank",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "RankSelect"
                    }
                ],
                // formDom: <AbundanceOtherForm></AbundanceOtherForm>,
                sampleGroupApI: false,
                saveAnalysisMethod: "metaphlan_abundance_alpha_diversity",
                moduleName: "abundance_alpha_diversity",
                sampleSelectComp: false,
                tableDesc: ` `,
                name: "alpha多样性"
            })

        }}>alpha多样性</Button >
        <Button type="primary" onClick={() => {
            plot({
                sampleGroupJSON:true,
                formJson: [
                    {
                        name: "group_field",
                        label: "分组列",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupFieldSelect",
                    }, {
                        name: "treatment",
                        label: "处理组",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    }, {
                        name: "control",
                        label: "对照组",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    },{
                        name: "rank",
                        label: "rank",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "RankSelect"
                    }
                ],
                sampleGroupApI: false,
                // formDom: <AbundanceOtherForm> </AbundanceOtherForm>,
                saveAnalysisMethod: "metaphlan_abundance_beta_diversity",
                moduleName: "abundance_beta_diversity",
                sampleSelectComp: false,
                tableDesc: ` `,
                name: "beta多样性"
            })

        }}>beta多样性</Button >

        <Button type="primary" onClick={() => {
            plot({
                sampleGroupJSON: true,
                formJson: [
                    {
                        name: "group_field",
                        label: "分组列",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupFieldSelect",
                    }, {
                        name: "treatment",
                        label: "处理组",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    }, {
                        name: "control",
                        label: "对照组",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    },{
                        name: "rank",
                        label: "rank",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "RankSelect"
                    }
                ],
                sampleGroupApI: false,
                // formDom: <AbundanceOtherForm> </AbundanceOtherForm>,
                saveAnalysisMethod: "metaphlan_abundance_difference_matrix",
                moduleName: "abundance_difference",
                sampleSelectComp: false,
                tableDesc: ` `,
                name: "差异分析"
            })

        }}>差异分析</Button >

        <Button type="primary" onClick={() => {
            plot({
                sampleGroupJSON: true,
                formJson: [
                    {
                        name: "group_field",
                        label: "分组列",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupFieldSelect",
                    }, {
                        name: "sites1",
                        label: "部位一",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    }, {
                        name: "sites2",
                        label: "部位二",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    }
                ],
                sampleGroupApI: false,
                formDom: <AbundanceOtherForm> </AbundanceOtherForm>,
                saveAnalysisMethod: "metaphlan_prevalence_matrix",
                moduleName: "abundance_prevalence",
                sampleSelectComp: false,
                tableDesc: ` `,
                name: "流行度分析"
            })

        }}>流行度分析</Button >
        {/* {JSON.stringify(sampleGroupedOptions)} */}
        <Button type="primary" onClick={() => {
            plot({
                sampleGroupJSON: true,
                formJson: [
                    {
                        name: "group_field",
                        label: "分组列",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupFieldSelect"
                    }, {
                        name: "sites1",
                        label: "部位一",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    }, {
                        name: "sites2",
                        label: "部位二",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    }, {
                        name: "treatment",
                        label: "累积丰度处理组",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    }, {
                        name: "control",
                        label: "累积丰度对照组",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "GroupSelectSampleButton",
                        group: "group_field",
                    }, {
                        name: "rank",
                        label: "rank",
                        rules: [{ required: true, message: '该字段不能为空!' }],
                        type: "RankSelect"
                    }
                ],
                sampleGroupApI: false,
                formDom:

                    <>
                        <GroupCompareSelect></GroupCompareSelect>
                        {/* <AbundanceOtherForm> </AbundanceOtherForm>
                        <GroupCompareSelect></GroupCompareSelect> */}
                        {/* <AbundanceOtherForm> </AbundanceOtherForm>
                        <Form.Item label="累积丰度菌定义" name={"query"}>
                            <Select mode="multiple" options={query}></Select>
                        </Form.Item>
                        <Form.Item label="累积丰度处理组" name={"treatment"}>
                            <Select mode="multiple" options={sampleGroupedOptions}></Select>
                        </Form.Item>
                        <Form.Item label="累积丰度对照组" name={"control"}>
                            <Select mode="multiple" options={sampleGroupedOptions}></Select>
                        </Form.Item> */}
                        {/* {JSON.stringify(sampleGroupedOptions)} */}
                    </>


                ,
                saveAnalysisMethod: "abundance-cumulative-abundance",
                moduleName: "abundance-cumulative-abundance",
                sampleSelectComp: false,
                tableDesc: ` `,
                name: "累积丰度分析"
            })

        }}>累积丰度分析</Button >
        {/* {JSON.stringify(sampleGrouped)} */}
        {/* {JSON.stringify(sampleGroup)} */}
    </>
}

const GroupCompareSelect: FC<any> = ({ value, onChange }) => {
    const form = Form.useFormInstance();
    const treatment_group = Form.useWatch(["sites1", "group"], form);
    const control_group = Form.useWatch(["sites2", "group"], form);
    const [query, setQuery] = useState<any>()
    useEffect(() => {
        if (treatment_group && control_group) {
            setQuery([
                {
                    label: `Prevalent in both sites`,
                    value: `Prevalent in both sites`
                }, {
                    label: `Prevalent in ${control_group.join("-")}`,
                    value: `Prevalent in ${control_group.join("-")}`
                }, {
                    label: `Prevalent in ${treatment_group.join("-")}`,
                    value: `Prevalent in ${treatment_group.join("-")}`
                }, {
                    label: `Not prevalent in either sites`,
                    value: `Not prevalent in either sites`
                }
            ])
        }
    }, [treatment_group, control_group])


    return <>
        <Form.Item label="累积丰度菌定义" name={"query"} rules={[{ required: true, message: '该字段不能为空!' }]}>
            <Select mode="multiple" options={query} value={value} onChange={onChange}></Select>
        </Form.Item>
        <Form.Item initialValue={"sum"} label="计算方式" name={"calculation_method"} rules={[{ required: true, message: '该字段不能为空!' }]}>
            <Select options={[
                {
                    label: "sum",
                    value: "sum"
                }, {
                    label: "count",
                    value: "count"
                }
            ]} value={value} onChange={onChange}></Select>
        </Form.Item>
        <Form.Item initialValue={"mannwhitneyu"} label="统计检验方法" name={"hypothesis"} rules={[{ required: true, message: '该字段不能为空!' }]}>
            <Select options={[
                {
                    label: "Mann–Whitney U(Wilcoxon rank-sum)",
                    value: "mannwhitneyu"
                }, {
                    label: "Poisson regression",
                    value: "poisson"
                }
            ]} value={value} onChange={onChange}></Select>
        </Form.Item>
    </>
}
const AbundanceOtherForm: FC<any> = () => {
    return <>
        <Form.Item initialValue={"SPECIES"} label="rank" name={"rank"} rules={[{ required: true, message: '该字段不能为空!' }]}>
            <Select allowClear options={[
                {
                    label: "SGB",
                    value: "SGB"
                }, {
                    label: "SPECIES",
                    value: "SPECIES"
                }, {
                    label: "GENUS",
                    value: "GENUS"
                }, {
                    label: "FAMILY",
                    value: "FAMILY"
                }, {
                    label: "ORDER",
                    value: "ORDER"
                }, {
                    label: "CLASS",
                    value: "CLASS"
                }, {
                    label: "PHYLUM",
                    value: "PHYLUM"
                },
            ]}></Select>
        </Form.Item>
    </>
}