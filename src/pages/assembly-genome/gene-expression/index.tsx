import { Button, Form, Select, Tabs } from "antd"
import { FC, useEffect, useState } from "react"
import AnalysisPanel from '../../../components/analysis-sotware-panel'

// import Eggnog from "./eggnog"
const GeneExpressison: FC<any> = () => {

    return <>
        <Tabs items={[
            {
                key: "gene_count",
                label: "gene_count",
                children: <>
                    <AnalysisPanel analysisPipline={"gene_count"} inputAnalysisMethod={[
                        {
                            name: "rna_seq",
                            label: "RNA测序文件",
                            inputKey: ["V1_single_genome_NGS_RNA"],
                            mode: "multiple"
                        }, {
                            name: "genome_assembly",
                            label: "基因组参考文件",
                            inputKey: ["ngs-individual-assembly", 'tgs_individual_assembly'],
                            mode: "single"
                        }, {
                            name: "prokka",
                            label: "基因组注释文件",
                            inputKey: ["prokka"],
                            mode: "single"
                        }
                    ]}
                        analysisMethod={[
                            {
                                name: "bowtie2_RNA_mapping",
                                label: "bowtie2_RNA_mapping",
                                inputKey: ["bowtie2_RNA_mapping"],
                                mode: "multiple"
                            }, {
                                name: "feature_counts_RNA_mapping",
                                label: "feature_counts_RNA_mapping",
                                inputKey: ["feature_counts_RNA_mapping"],
                                mode: "multiple"
                            },
                        ]}
                        analysisType="sample" >
                        <GeneExpressisonComp></GeneExpressisonComp>
                    </AnalysisPanel>
                </>
            }
        ]}></Tabs>

        <p>

        </p>
    </>
}

export default GeneExpressison

import { Bowtie2Paired } from '../../software-components/bowtie2'

const GeneExpressisonComp: FC<any> = ({ resultTableList, plot, activeTabKey }) => {
    const [featureCountsSample,setFeatureCountsSample] = useState<any>([])
    useEffect(()=>{
        console.log(resultTableList['feature_counts_RNA_mapping'])
        if(resultTableList['feature_counts_RNA_mapping']){
            const featureCountsSample = resultTableList['feature_counts_RNA_mapping'].map((it: any) => {
                return {
                    label: `${it.sample_key} `,
                    value: `${it.id}`
    
                }
            })
            setFeatureCountsSample(featureCountsSample)
        }
    
    },[resultTableList]) 

    const getLogs = (analysisKey: any) => {
        return resultTableList[analysisKey].map((it: any) => it.content.log)
    }
    return <>
        {activeTabKey == "bowtie2_RNA_mapping" && <>
            <Bowtie2Paired
                resultTableList={resultTableList}
                plot={plot}
                analysisKey="bowtie2_RNA_mapping"></Bowtie2Paired>
        </>}


        {activeTabKey == "feature_counts_RNA_mapping" && <>
            <Button type="primary" onClick={() => {
                plot({
                    // saveAnalysisMethod: "mutations_gene",
                    saveAnalysisMethod: "feature_counts_RNA_mapping_stat",
                    moduleName: "feature_counts_stat",
                    params: { "log_path_list": getLogs("feature_counts_RNA_mapping") },
                    tableDesc: `
                                `
                })

            }}>基因计数统计</Button >
            {/* <Bowtie2Paired
                resultTableList={resultTableList}
                plot={plot}
                analysisKey="bowtie2_RNA_mapping"></Bowtie2Paired> */}

            <Button type="primary"
                onClick={() => {
                    plot({
                        name:"差异表达基因分析",
                        // saveAnalysisMethod: "mutations_gene",
                        saveAnalysisMethod: "feature_counts_RNA_deg",
                        moduleName: "feature_counts_RNA_deg",
                        params: {

                        },
                        formDom: <>
                            <Form.Item label="选择处理组" name={"treatment"}>
                                <Select mode="multiple"  style={{ maxWidth: "20rem" }} allowClear options={featureCountsSample}></Select>
                            </Form.Item>
                            <Form.Item label="选择对照组" name={"control"}>
                                <Select mode="multiple"  style={{ maxWidth: "20rem" }} allowClear options={featureCountsSample}></Select>
                            </Form.Item>
                        </>,
                        tableDesc: `

                                `
                    })

                  
                }}
            >差异表达基因分析</Button>
        </>}
        {/* {JSON.stringify(resultTableList['feature_counts_RNA_mapping'])} */}
    </>
}