import { FC, useEffect, useState } from "react"
import axios from "axios"
import { Table, TableProps, Tabs } from "antd"
import AnalysisPanel from "@/components/analysis-sotware-panel"
import Breseq from "./breseq"
import BreseqMutliSample from './breseq/multi-sample'
const Mutation: FC<any> = () => {
    const [mutationData, setMutationData] = useState([])
    const [loading,setLoading] = useState(false)
    const loadSample = async () => {
        setLoading(true)
        const resp: any = await axios.get('/api/mutation')
        console.log(resp)
        setLoading(false)
        setMutationData(resp.data)
    }
    const columns: TableProps<any>['columns'] = [
        {
            title: 'title',
            dataIndex: 'title',
            key: 'title',
        },{
            title: 'seq_id',
            dataIndex: 'seq_id',
            key: 'seq_id',  
        },{
            title: 'position',
            dataIndex: 'position',
            key: 'position',  
        },{
            title: 'type',
            dataIndex: 'type',
            key: 'type',  
        },{
            title: 'ref_seq',
            dataIndex: 'ref_seq',
            key: 'ref_seq',  
        },{
            title: 'new_seq',
            dataIndex: 'new_seq',
            key: 'new_seq',  
        },{
            title: 'gene_name',
            dataIndex: 'gene_name',
            key: 'gene_name',  
        },{
            title: 'gene_product',
            dataIndex: 'gene_product',
            key: 'gene_product',  
        },{
            title: 'locus_tag',
            dataIndex: 'locus_tag',
            key: 'locus_tag',  
        },
        
        {
            title: 'mutation_category',
            dataIndex: 'mutation_category',
            key: 'mutation_category',  
        }
    ]
    useEffect(() => {
        loadSample()
    }, [])
    const appendSampleColumns:any=[
        {
            title: '参考基因组',
            dataIndex: 'reference',
            key: 'reference',
            ellipsis: true,
            render:(_: any, record: any)=><>
                {record?.content?.reference}
            </>
        },
    ]
    return <>

        <Tabs items={[
            {
                label:"breseq",
                key:"breseq",
                children: <AnalysisPanel appendSampleColumns={appendSampleColumns} analysisMethod={[
                    {
                        name: "breseq",
                        label: "breseq",
                        inputKey: ["breseq"],
                        mode: "multiple"
                    }
                ]} analysisType="sample" >
                   <Breseq></Breseq>
                </AnalysisPanel>
            }
            // ,{
            //     label:"breseq",
            //     key:"breseq",
            //     children:<Table loading={loading} scroll={{ x: 'max-content' }} columns={columns} dataSource={mutationData} />
            // }
        ]}>
        </Tabs>
        
    </>
}

export default Mutation
