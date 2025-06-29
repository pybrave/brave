import { Tabs } from "antd"
import { FC } from "react"
import AnalysisPanel from '../../../components/analysis-sotware-panel'
const Assembly: FC<any> = () => {
   
    return <>
        <Tabs items={[
            {
                key: "ngs-individual-assembly",
                label: "二代测序单独组装",
                children: <>
                    <AnalysisPanel
                        inputAnalysisMethod={[
                            {
                                name: "1",
                                label: "V1_single_genome_NGS_DNA",
                                inputKey: ["V1_single_genome_NGS_DNA"],
                                mode: "multiple",
                                type: "GroupSelectSampleButton",
                                groupField:"sample_group",
                                rules: [{ required: true, message: '该字段不能为空!' }],
                            }
                        ]} 
                        analysisMethod={[
                            {
                                name: "1",
                                label: "ngs-individual-assembly",
                                inputKey: ["ngs-individual-assembly"],
                                mode: "multiple"
                            }
                        ]} analysisType="sample" />
                </>
            }, {
                key: "tgs_individual_assembly",
                label: "三代测序单独组装",
                children: <>
                    <AnalysisPanel 
                    inputAnalysisMethod={[
                        {
                            name: "1",
                            label: "V1_single_genome_PACBIO_HIFI_DNA",
                            inputKey: ["V1_single_genome_PACBIO_HIFI_DNA"],
                            mode: "multiple",
                            type: "GroupSelectSampleButton",
                            groupField:"sample_group",
                            rules: [{ required: true, message: '该字段不能为空!' }],
                        }
                    ]} analysisMethod={[
                        {
                            name: "1",
                            label: "tgs_individual_assembly",
                            inputKey: ["tgs_individual_assembly"],
                            mode: "multiple"
                        }
                    ]} analysisType="sample" />
                </>
            }, {
                key: "ngs-co-assembly",
                label: "二代测序混合组装",
                children: <>
                </>
            }, {
                key: "ngs-tgs-co-assembly",
                label: "二三代测序混合组装",
                children: <>
                </>
            },
        ]}></Tabs>

        <p>

        </p>
    </>
}

export default Assembly