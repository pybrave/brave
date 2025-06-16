include { fromQuery } from 'plugin/nf-sqldb'
include {fastp} from './modules/fastp.nf'
include {bowtie2V2 as bowtie2} from './modules/bowtie2.nf'
// include { bowtie2} from './modules/bowtie2.nf'

include {metaphlanV2 as metaphlan} from './modules/metaphlan.nf'
include {import_metaphlan_profile} from './modules/metaphlan.nf'
include {kraken2} from './modules/kraken2.nf'
include {bracken} from './modules/kraken2.nf'
include {import_kraken_profile} from './modules/kraken2.nf'
include {metaphlan_marker_counts} from './modules/metaphlan.nf'
include {metaphlan_strain_tracker} from './modules/metaphlan.nf'
include {fastqc as fastqc_clean_reads} from './modules/fastqc.nf'
include {fastqc as fastqc_unalignment} from './modules/fastqc.nf'
include {metaphlan_bowtie2} from './modules/metaphlan.nf'
include {metaphlan_sam} from './modules/metaphlan.nf'
include {metawrap_assemblyV2 as metawrap_assembly} from './modules/metawrap.nf'
include {samtools_remove_hosts} from './modules/samtools.nf'
include {multiqc} from './modules/multiqc.nf'
include {seqkit as seqkit_unalignment} from './modules/seqkit.nf'

workflow{


    
    ch_bam_input = channel.fromQuery("SELECT sample_name,project,content from sample_analysis_result WHERE project='${params.project}' and analysis_name='bowtie2_align_host' and file_type='bam' and analysis_verison='${params.version}' ", db: 'foo')
    ch_bam_input = ch_bam_input.map(it->[[id:it[0],project:it[1]],[it[2]]])
    ch_samtools_remove_hosts_res = samtools_remove_hosts(ch_bam_input)
    ch_metawrap_assembly_res =  metawrap_assembly(ch_samtools_remove_hosts_res.fastq)
    // ch_metaphlan_db_index = Channel.value("/data/wangyang/databases/metaphlan/mpa_vJun23_CHOCOPhlAnSGB_202403")
    // ch_metaphlan_bowtie2_res = metaphlan_bowtie2(ch_samtools_remove_hosts_res.fastq,ch_metaphlan_db_index )



}