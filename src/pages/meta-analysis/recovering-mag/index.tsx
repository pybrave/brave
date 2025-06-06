import { Button, Tabs } from "antd"
import { FC } from "react"
import AnalysisPanel from '../../components/analysis-panel'
import { Bowtie2 } from '../../software-components/bowtie2'
import { formatUrl } from '@/utils/utils'

const RecoveringMag: FC<any> = () => {

    return <>
        <Tabs items={[
            {
                key: "metawrap_individual_assembly",
                label: "metawrap_individual_assembly",
                children: <>
                    <AnalysisPanel
                        // analysisMethod={[
                        //     {
                        //         key: "metaphlan_sam_abundance",
                        //         name: "metaphlan_sam_abundance",
                        //         value: ["metaphlan_sam_abundance"],
                        //         mode: "multiple"
                        //     }
                        // ]} 
                        analysisPipline="pipeline_metaphlan_abundance"
                        analysisMethod={[
                            {
                                key: "metawrap_assembly",
                                name: "metawrap_assembly",
                                value: ["metawrap_assembly"],
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