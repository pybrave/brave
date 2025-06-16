
include {kraken2} from './modules/kraken2.nf'
include {bracken} from './modules/kraken2.nf'

workflow  {
    
    // ch_kraken2_res = kraken2(ch_samtools_remove_hosts_res.fastq, "/data/databases/kraken/pluspf")
    // ch_bracken_res = bracken(ch_kraken2_res.report, "/data/databases/kraken/pluspf")
    
}