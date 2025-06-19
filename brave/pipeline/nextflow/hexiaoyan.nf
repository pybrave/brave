include { fromQuery } from 'plugin/nf-sqldb'
include {fastp} from './modules/fastp.nf'
include {bowtie2} from './modules/bowtie2.nf'
// include { metaphlan} from './modules/metaphlan.nf'
include {metaphlanV2 as metaphlan} from './modules/metaphlan.nf'

include {import_metaphlan_profile} from './modules/metaphlan.nf'
// include {kraken2V2 as kraken2} from './modules/kraken2.nf'
include {kraken2} from './modules/kraken2.nf'

include {bracken} from './modules/kraken2.nf'
include {import_kraken_profile} from './modules/kraken2.nf'
include {metaphlan_marker_counts} from './modules/metaphlan.nf'
include {fastqc as fastqc_clean_reads} from './modules/fastqc.nf'
include {fastqc as fastqc_unalignment} from './modules/fastqc.nf'
include {metawrap_assemblyV2 as metawrap_assembly} from './modules/metawrap.nf'
include {samtools_remove_hosts} from './modules/samtools.nf'
include {seqkit as seqkit_unalignment} from './modules/seqkit.nf'
include {seqkitV2 as seqkit_kraken_unclassified} from './modules/seqkit.nf'

include {hdfs_put_single_file} from './modules/hdfs.nf'

workflow{
    ch_verison = Channel.value("v2.0")

    ch_reads_input = channel.fromQuery("SELECT sample_name,fastq1,fastq2 from t_samples WHERE project='hexiaoyan'", db: 'foo')
    // ch_reads_input = ch_reads_input.first()
    ch_reads_input = ch_reads_input.map(it->[[id:it[0]],[it[1],it[2]]])

    ch_clean_reads = fastp(ch_reads_input)
    fastqc_clean_reads(ch_clean_reads.reads, "clean_reads")

    ch_bowtie2_host_index = Channel.value('/data/metagenome_data/bowtie2_index/human/human38')
    ch_bowtie2_res = bowtie2(ch_clean_reads.reads, ch_bowtie2_host_index)
    // ch_bowtie2_res.aligned.view()
    ch_samtools_remove_hosts_res = samtools_remove_hosts(ch_bowtie2_res.aligned)
    fastqc_unalignment(ch_samtools_remove_hosts_res.fastq, "samtools_unalignment")
    seqkit_unalignment(ch_samtools_remove_hosts_res.fastq.collect{it[1]},"seqkit_unalignment")
    hdfs_put_single_file(seqkit_unalignment.out.tsv,"hexiaoyan",ch_verison,"seqkit")
    // ch_metawrap_assembly_res =  metawrap_assembly(ch_samtools_remove_hosts_res.fastq)
    ch_metaphlan_db = Channel.value("/data/wangyang/databases/metaphlan")
    // ch_metaphlan_res  = metaphlan(ch_bowtie2_res.fastq, ch_metaphlan_db)
    ch_metaphlan_res  = metaphlan(ch_samtools_remove_hosts_res.fastq, ch_metaphlan_db)

    import_metaphlan_profile(ch_metaphlan_res.profile,"hexiaoyan",ch_verison)

    // ch_kraken2_res = kraken2(ch_bowtie2_res.fastq, "/data/databases/kraken/pluspf")
    ch_kraken2_res = kraken2(ch_samtools_remove_hosts_res.fastq, "/data/databases/kraken/pluspf")

    ch_bracken_res = bracken(ch_kraken2_res.report, "/data/databases/kraken/pluspf")
    import_kraken_profile(ch_bracken_res.reports,"hexiaoyan",ch_verison)
    // ch_kraken2_res.unclassified_reads_fastq.view()
    seqkit_kraken_unclassified(ch_kraken2_res.unclassified_reads_fastq.collect{it[1]},"seqkit_kraken_unclassified","*.fastq")
    // metaphlan_marker_counts(ch_metaphlan_res.bt2out, ch_metaphlan_db)
}