import { Button, Tabs } from "antd"

import Difference from './difference/index'
import ROC from './roc/index'
import AbundanceTable from './abundance-table/index'
import Diversity from './diversity/index'
import DiversityBeta from './diversity/diversity-beta'

import Result from './result/index'
import Prevalence from './prevalence/index'
import StackedDiagram from './stacked-diagram'
import Pie from './pie'
import Venn from './venn'
import CumulativeAbundance from './cumulative-abundance'
import Unique from './unique'
import AnalysisPanel from "../../components/analysis-sotware-panel"
import AlphaDiversity from './alpha-diversity'
import { FC } from "react"
const AbundanceAnalysis = () => {

    return <>
        <Tabs items={[
             {
                key: "diversity-alphattmp",
                label: "alpha多样性",
                children: <Diversity></Diversity>
            }, {
                key: "diversity-beta",
                label: "beta多样性",
                children: <DiversityBeta></DiversityBeta>
            }, {
                key: "stacked-diagram",
                label: "堆叠图",
                children: <StackedDiagram></StackedDiagram>
            }
            , {
                key: "pie",
                label: "饼图",
                children: <Pie></Pie>
            }, {
                key: "difference",
                label: "差异分析",
                children: <Difference></Difference>
            }, {
                key: "roc",
                label: "ROC分析",
                children: <ROC></ROC>
            }, {
                key: "prevalence",
                label: "流行率分析",
                children: <Prevalence></Prevalence>
            }, {
                key: "cumulative-abundance",
                label: "累积丰度",
                children: <CumulativeAbundance></CumulativeAbundance>
            }, {
                key: "venn",
                label: "集合分析",
                children: <Venn></Venn>
            }, {
                key: "abundanceTable",
                label: "丰度表格",
                children: <AbundanceTable></AbundanceTable>
            }
            // ,{
            //     key:"result",
            //     label:"分析结果",
            //     children:<Result></Result>
            // }
        ]}></Tabs>
    </>
}

export default AbundanceAnalysis
