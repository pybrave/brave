include { fromQuery } from 'plugin/nf-sqldb'
include { prokka } from './modules/prokka.nf'
include {fastp} from './modules/fastp.nf'
include {roary} from './modules/roary.nf'
include {spades} from './modules/spades.nf'
include {breseq} from './modules/breseq.nf'
include {gdtools_compare} from './modules/gdtools.nf'
include {gdtools_sample} from './modules/gdtools.nf'
include {emapper} from './modules/emapper.nf'
workflow{
    // println("11111111111111")
    // ch_genome_input = channel.fromQuery("select name,fasta from t_genome where project= 'leipu'", db: 'foo')
    // ch_genome_input = ch_genome_input.map(it->[[id:it[0]],[it[1]]])
    // // ch_genome_input.view()
    // ch_prokka_res = prokka(ch_genome_input)
    // ch_prokka_res_gff =  ch_prokka_res.gff.collect({it[1]})
    // ch_prokka_res_gff.view()
    // roary(ch_prokka_res_gff)
    
    ch_reads_input = channel.fromQuery("SELECT sample_name,fastq1,fastq2 from t_samples WHERE project='leipu'  and is_available=1 and sample_composition='single_genome' and sequencing_technique='NGS' and sequencing_target='DNA'", db: 'foo')
    // ch_reads_input = ch_reads_input.first()
    ch_reads_input = ch_reads_input.map(it->[[id:it[0]],[it[1],it[2]]])
    // ch_reads_input.view()
    ch_clean_reads = fastp(ch_reads_input)
    ch_spades_res =  spades(ch_clean_reads.reads)
    // ch_spades_res.scaffolds.view()
    // https://www.ncbi.nlm.nih.gov/datasets/taxonomy/1622/
    // ch_prokka_res = prokka(ch_spades_res.scaffolds,"Bacteria","Ligilactobacillus")
    // ch_prokka_res_gff =  ch_prokka_res.gff.collect({it[1]})
    // roary(ch_prokka_res_gff)
    ch_fasta = Channel.of("/ssd1/wy/workspace2/leipu/leipu_workspace2/output/genomes/OCF-1-PACBIO-HIFI/OCF-1-PACBIO-HIFI.fasta")
     .map(it->[[id:"OCF-1-PACBIO-HIFI"],[it]])
    // ch_fasta.view()
    ch_prokka_res = prokka(ch_fasta,"Bacteria","Ligilactobacillus")

    // reference = Channel.value("/ssd1/wy/workspace2/leipu/leipu_workspace/output/prokka/S-1-1-assembly/S-1-1-assembly.gbk")
    // reference_name = "OSP-3-PACBIO-HIFI"
    reference = Channel.value("/ssd1/wy/workspace2/leipu/leipu_workspace2/output/prokka/OCF-1-PACBIO-HIFI/OCF-1-PACBIO-HIFI.gbk")
    reference_name = "OCF-1-PACBIO-HIFI"
    ch_breseq_res =  breseq(ch_clean_reads.reads, reference, reference_name)
    gdtools_sample(ch_breseq_res.annotated_gd,reference,reference_name)
    annotated_gd_files = ch_breseq_res.annotated_gd.collect({it[1]})
    annotated_gd_files.view()
    gdtools_compare(annotated_gd_files, reference,reference_name)
    // ch_prokka_res.faa.view()
    emapper(ch_prokka_res.faa)



    
}