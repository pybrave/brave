import { Tabs } from "antd"
import { FC } from "react"
import AnalysisPanel from '../../../components/analysis-sotware-panel'
import { UpstreamAnalysisInput } from '../../../components/analysis-sotware-panel'
import Prokka from "./prokka"
const GenePrediction: FC<any> = () => {

    return <>
        <Tabs items={[
            {
                key: "Prokka",
                label: "Prokka",
                children: <>
                    {/* <UpstreamAnalysisInput /> */}
                    <AnalysisPanel
                        inputAnalysisMethod={[
                            {
                                name: "1",
                                label: "基因组组装文件",
                                inputKey: ["ngs-individual-assembly", 'tgs_individual_assembly'],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField:"sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }
                        ]}
                        analysisMethod={[
                            {
                                name: "1",
                                label: "prokka",
                                inputKey: ["prokka"],
                                mode: "multiple"
                            }
                        ]}
                        analysisType="sample" >
                        <Prokka></Prokka>
                    </AnalysisPanel>
                </>
            }
        ]}></Tabs>

        <p>

        </p>
    </>
}

export default GenePrediction