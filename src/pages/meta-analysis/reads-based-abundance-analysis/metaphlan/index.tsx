import { Button } from "antd"
import { FC } from "react"
import {SelectComp} from '../../../../components/analysis-panel'
import FormItem from "antd/es/form/FormItem"
export const Metaphlan: FC<any> = ({ record, resultTableList, plot }) => {
    const getLogs = () => {
        return [] //resultTableList['bowtie2_align_metaphlan'].map((it: any) => it.content.log)
    }
    return <>
        <Button type="primary" onClick={() => {
            plot({
                saveAnalysisMethod: "metaphlan_sam_abundance_matrix",
                moduleName: "abundance_matrix",
                sampleSelectComp:true,
                tableDesc: ` `
            })

        }}>丰度矩阵</Button >
      
    </>
}
