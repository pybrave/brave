
include {kraken2} from './modules/kraken2.nf'
include {bracken} from './modules/kraken2.nf'

workflow  {
    ch_input = channel.fromList(params.samples).map(it->[[id:it.sample_key],[it.fastq1,it.fastq2]])
    // ch_input.view()
    ch_kraken_database = Channel.value(params.database)
    ch_kraken2_res = kraken2(ch_input, ch_kraken_database)
    ch_bracken_res = bracken(ch_kraken2_res.report, ch_kraken_database)
    
}