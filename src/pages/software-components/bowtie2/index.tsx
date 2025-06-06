import { Button, Form, Input, InputNumber } from "antd"
import { FC } from "react"
import { formatUrl } from '@/utils/utils'
export const Bowtie2: FC<any> = ({ record, resultTableList, plot }) => {
    const getLogs = () => {
        return resultTableList['bowtie2_align_metaphlan'].map((it: any) => it.content.log)
    }
    return <>
        <Button type="primary" onClick={() => {
            plot({
                // saveAnalysisMethod: "mutations_gene",
                moduleName: "bowtie2_mapping",
                params: { "log_path_list": getLogs(), mappping_type: "unpaired" },
                tableDesc: `

                                `

            })

        }}>比对统计</Button >
        {/* {resultTableList['bowtie2_align_metaphlan'] && <>
            {JSON.stringify(resultTableList['bowtie2_align_metaphlan'].map((it:any)=>it.content.log))}
        </>} */}

    </>
}

export const Bowtie2Paired: FC<any> = ({ record, activeTabKey, resultTableList, plot, analysisKey }) => {
    const getLogs = () => {
        return resultTableList[analysisKey].map((it: any) => it.content.log)
    }
    return <>
        {activeTabKey == analysisKey && <>
            <Button type="primary" onClick={() => {
                plot({
                    // saveAnalysisMethod: "mutations_gene",
                    saveAnalysisMethod: "bowtie2_align_host_table",
                    moduleName: "bowtie2_mapping",
                    params: { "log_path_list": getLogs(), mappping_type: "paired" },
                    tableDesc: `

                                `

                })

            }}>比对统计</Button >
        </>}

        {/* {resultTableList['bowtie2_align_metaphlan'] && <>
            {JSON.stringify(resultTableList['bowtie2_align_metaphlan'].map((it:any)=>it.content.log))}
        </>} */}

    </>
}
