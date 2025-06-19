include { fromQuery } from 'plugin/nf-sqldb'
include {fastp} from './modules/fastp.nf'
include {bowtie2V2 as bowtie2} from './modules/bowtie2.nf'
include {metaphlanV2 as metaphlan} from './modules/metaphlan.nf'
include {import_metaphlan_profile} from './modules/metaphlan.nf'
include {kraken2} from './modules/kraken2.nf'
include {bracken} from './modules/kraken2.nf'
include {fastqc as fastqc_unalignment} from './modules/fastqc.nf'
include {metawrap_assemblyV2 as metawrap_assembly} from './modules/metawrap.nf'
include {samtools_remove_hostsV2 as samtools_remove_hosts} from './modules/samtools.nf'
include {seqkit as seqkit_unalignment} from './modules/seqkit.nf'

workflow{
    ch_reads_input = channel.fromQuery("SELECT sample_name,fastq1,fastq2 from t_samples WHERE project='leipu'  and sample_composition='meta_genome' and sequencing_technique='NGS' and sequencing_target='DNA'", db: 'foo')
    // ch_reads_input = ch_reads_input.first()
    ch_reads_input = ch_reads_input.map(it->[[id:it[0]],[it[1],it[2]]])
    // ch_reads_input.view()
    ch_clean_reads = fastp(ch_reads_input)
    ch_bowtie2_host_index = Channel.value('/data/databases/mouse/bowtie2/Mus_musculus.GRCm39.dna_sm.toplevel.fa')
    ch_bowtie2_res = bowtie2(ch_clean_reads.reads, ch_bowtie2_host_index)
    
    ch_samtools_remove_hosts_res = samtools_remove_hosts(ch_bowtie2_res.aligned)
    fastqc_unalignment(ch_samtools_remove_hosts_res.fastq, "samtools_unalignment")
    seqkit_unalignment(ch_samtools_remove_hosts_res.fastq.collect{it[1]},"seqkit_unalignment")

    ch_metawrap_assembly_res =  metawrap_assembly(ch_samtools_remove_hosts_res.fastq)

    ch_metaphlan_db = Channel.value("/data/wangyang/databases/metaphlan")
    // ch_metaphlan_res  = metaphlan(ch_bowtie2_res.fastq, ch_metaphlan_db)
    ch_metaphlan_res  = metaphlan(ch_samtools_remove_hosts_res.fastq, ch_metaphlan_db)

    // import_metaphlan_profile(ch_metaphlan_res.profile,"leipu","v2.0")

    ch_kraken2_res = kraken2(ch_samtools_remove_hosts_res.fastq, "/data/databases/kraken/pluspf")
    // ch_kraken2_res = kraken2(ch_bowtie2_res.fastq, "/data/databases/kraken/pluspf")
    bracken(ch_kraken2_res.report, "/data/databases/kraken/pluspf")
    

}