include {bowtie2} from './modules/bowtie2.nf'
include {samtools_remove_hosts} from './modules/samtools.nf'


workflow  {
    ch_input = channel.fromList(params.samples).map(it->[[id:it.sample_key],[it.fastq1,it.fastq2]])
    ch_bowtie2_host_index = Channel.value(params.genome_index)
    ch_bowtie2_res = bowtie2(ch_input, ch_bowtie2_host_index)    
    ch_samtools_remove_hosts_res = samtools_remove_hosts(ch_bowtie2_res.aligned)


    
}