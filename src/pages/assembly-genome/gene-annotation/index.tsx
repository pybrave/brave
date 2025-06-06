import { Tabs } from "antd"
import { FC } from "react"
import AnalysisPanel from '../../components/analysis-panel'

import Eggnog from "./eggnog"
const GeneAnnotation: FC<any> = () => {

    return <>
        <Tabs items={[
            {
                key: "eggnog",
                label: "eggnog",
                children: <>
                    <AnalysisPanel analysisMethod={[
                         {
                            key: "1",
                            name: "eggnog",
                            value: ["eggnog"],
                            mode: "multiple"
                        }
                    ]} analysisType="sample" >
                        <Eggnog></Eggnog>
                    </AnalysisPanel>
                </>
            }
        ]}></Tabs>

        <p>

        </p>
    </>
}

export default GeneAnnotation