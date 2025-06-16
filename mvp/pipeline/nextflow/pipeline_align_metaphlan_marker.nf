include {bowtie2} from './modules/bowtie2.nf'
include {metaphlan_bowtie2} from './modules/metaphlan.nf'


workflow  {
    ch_input = channel.fromList(params.samples).map(it->[[id:it.sample_key],[it.fastq1,it.fastq2]])

    ch_metaphlan_db_index = Channel.value("/data/wangyang/databases/metaphlan/mpa_vJun23_CHOCOPhlAnSGB_202403")
    ch_metaphlan_bowtie2_res = metaphlan_bowtie2(ch_input,ch_metaphlan_db_index )

    
}