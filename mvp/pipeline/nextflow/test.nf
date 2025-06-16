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
    // ch_reads_input = channel.fromQuery("SELECT sample_name,fastq1,fastq2 from t_samples WHERE project='test'", db: 'foo')
    // // ch_reads_input = ch_reads_input.first()
    // ch_reads_input = ch_reads_input.map(it->[[id:it[0]],[it[1],it[2]]])
    // // ch_reads_input.view()
    // ch_clean_reads = fastp(ch_reads_input)
    // fastqc_clean_reads(ch_clean_reads.reads,"clean_reads")

    // ch_bowtie2_host_index = Channel.value('/data/metagenome_data/bowtie2_index/human/human38')
    // ch_bowtie2_res = bowtie2(ch_clean_reads.reads, ch_bowtie2_host_index)
    // ch_bowtie2_res.aligned.subscribe { it -> 
    //     def outputDir = file("/data2/wangyang/storeDir/test3")
    //     def targetFile = outputDir.resolve(it[1].getName())
    //     it[1].copyTo(targetFile)
    //     println "Got:${targetFile}" }
    // ch_metawrap_assembly_res =  metawrap_assembly(ch_bowtie2_res.fastq)

    // ch_bowtie2_res.aligned.view()
    // ch_bowtie2_res.aligned.map()

    
    ch_bam_input = channel.fromQuery("SELECT sample_name,project,contant_path from sample_analysis_result WHERE project='${params.project}' and analysis_name='bowtie2_align_host' and file_type='bam' and analysis_verison='${params.version}' ", db: 'foo')
    ch_bam_input = ch_bam_input.map(it->[[id:it[0],project:it[1]],[it[2]]])
    // ch_bam_input.view()
    ch_samtools_remove_hosts_res = samtools_remove_hosts(ch_bam_input)
    ch_metawrap_assembly_res =  metawrap_assembly(ch_samtools_remove_hosts_res.fastq)
    ch_metaphlan_db_index = Channel.value("/data/wangyang/databases/metaphlan/mpa_vJun23_CHOCOPhlAnSGB_202403")
    ch_metaphlan_bowtie2_res = metaphlan_bowtie2(ch_samtools_remove_hosts_res.fastq,ch_metaphlan_db_index )



    // seqkit_unalignment(ch_samtools_remove_hosts_res.fastq.collect{it[1]},"seqkit_unalignment")



    // // ch_fastqc_unalignment_res = fastqc_unalignment(ch_samtools_remove_hosts_res.fastq, "unalignment")
    // ch_metaphlan_db = Channel.value("/data/wangyang/databases/metaphlan")
    // ch_metaphlan_res  = metaphlan(ch_bowtie2_res.fastq, ch_metaphlan_db)
    
    // ch_metaphlan_bowtie2_res = metaphlan_bowtie2(ch_clean_reads.reads,ch_metaphlan_db_index )
    // metaphlan_sam(ch_metaphlan_bowtie2_res.aligned, ch_metaphlan_db)
    // import_metaphlan_profile(ch_metaphlan_res.profile,"test","v2.0")
    // ch_kraken2_res = kraken2(ch_bowtie2_res.fastq, "/data/databases/kraken/pluspf")
    // ch_bracken_res = bracken(ch_kraken2_res.report, "/data/databases/kraken/pluspf")
    // import_kraken_profile(ch_bracken_res.reports,"test","v2.0")
    // metaphlan_marker_counts(ch_metaphlan_res.bt2out, ch_metaphlan_db)
    // metaphlan_strain_tracker(ch_metaphlan_res.bt2out, ch_metaphlan_db,"s__Prevotella_nigrescens")
    
    
    
    // ch_reads_query = channel.fromQuery("SELECT sample_name,sample_key,project from t_samples WHERE project='test'", db: 'foo')
    // ch_reads_query = ch_reads_query.map(it->[[id:it[0]],[it[1],it[2]]])
    // ch_reads_query.view()
    // ch_metaphlan_res.profile.map(it->[it[0]['id'],it[1]]).join(ch_reads_query,by:0).view()
    // ch_multiqc_files = Channel.empty()  
    // ch_multiqc_files = ch_multiqc_files.mix(ch_fastqc_unalignment_res.zip.collect{it[1]}.ifEmpty([]))
    // multiqc(ch_multiqc_files)

}