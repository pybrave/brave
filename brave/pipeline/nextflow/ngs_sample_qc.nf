include {fastp} from './modules/fastp.nf'

workflow  {

    ch_input = channel.fromList(params.samples).map(it->[[id:it.sample_key],[it.fastq1,it.fastq2]])
    ch_clean_reads = fastp(ch_input)

    
}