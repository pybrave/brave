include { fromQuery } from 'plugin/nf-sqldb'
include { prokka } from './modules/prokka.nf'
include {fastp} from './modules/fastp.nf'
include {fastp as fastp2} from './modules/fastp.nf'

include {roary} from './modules/roary.nf'
include {spades} from './modules/spades.nf'
include {breseq} from './modules/breseq.nf'
include {gdtools_compare} from './modules/gdtools.nf'
include {spades_with_long_reads} from './modules/spades.nf'

workflow{
    // println("11111111111111")
    // ch_genome_input = channel.fromQuery("select name,fasta from t_genome where project= 'leipu'", db: 'foo')
    // ch_genome_input = ch_genome_input.map(it->[[id:it[0]],[it[1]]])
    // // ch_genome_input.view()
    // ch_prokka_res = prokka(ch_genome_input)
    // ch_prokka_res_gff =  ch_prokka_res.gff.collect({it[1]})
    // ch_prokka_res_gff.view()
    // roary(ch_prokka_res_gff)
    ch_reads_input = channel.fromQuery("SELECT sample_name,fastq1,fastq2 from t_samples WHERE id=696", db: 'foo')
    ch_reads_input = ch_reads_input.map(it->[[id:it[0]],[it[1],it[2]]])
    // ch_reads_input.view()
    ch_clean_reads_ref = fastp(ch_reads_input)
    pacbio_fastq = Channel.value("/ssd1/wy/workspace2/leipu/pacbio_fastq/hifi_reads.fastq.gz")
    ch_spades_res =  spades_with_long_reads(ch_clean_reads_ref.reads,pacbio_fastq)
    // ch_spades_res.scaffolds.view()
    ch_prokka_res = prokka(ch_spades_res.scaffolds,"Bacteria","Ligilactobacillus")
    // ch_prokka_res.gbk.view()
    // ch_clean_reads_ref.reads.combine(ch_prokka_res.gbk).view()
    ch_reads_input_all = channel.fromQuery("SELECT sample_name,fastq1,fastq2 from t_samples WHERE project='leipu'  and is_available=1", db: 'foo')
    ch_reads_input_all = ch_reads_input_all.map(it->[[id:it[0]],[it[1],it[2]]])
    ch_clean_reads = fastp2(ch_reads_input_all)

//     ch_spades_res =  spades(ch_clean_reads.reads)
//     // ch_spades_res.scaffolds.view()
//     // https://www.ncbi.nlm.nih.gov/datasets/taxonomy/1622/
//     ch_prokka_res = prokka(ch_spades_res.scaffolds,"Bacteria","Ligilactobacillus")
//     ch_prokka_res_gff =  ch_prokka_res.gff.collect({it[1]})
//     // ch_prokka_res_gff.view()
//     roary(ch_prokka_res_gff)

    reference = Channel.value("/ssd1/wy/workspace2/leipu/leipu_workspace3/output/spades/pacbio_assembly_OSP-3/scaffolds.fasta")
    // ch_clean_reads.reads.view()
    ch_prokka_res.gbk.map(it->it[1]).view()
    ch_breseq_res =  breseq(ch_clean_reads.reads, reference)
    // annotated_gd_files = ch_breseq_res.annotated_gd.collect({it[1]})
    // annotated_gd_files.view()
//     gdtools_compare(annotated_gd_files, reference)
}