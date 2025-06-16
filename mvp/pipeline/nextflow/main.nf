include { fromQuery } from 'plugin/nf-sqldb'
include { prokka } from './modules/prokka.nf'
include {fastp} from './modules/fastp.nf'
include {roary} from './modules/roary.nf'
include {spades} from './modules/spades.nf'
include {breseq} from './modules/breseq.nf'

workflow{
    // println("11111111111111")
    // ch_genome_input = channel.fromQuery("select name,fasta from t_genome where project= 'leipu'", db: 'foo')
    // ch_genome_input = ch_genome_input.map(it->[[id:it[0]],[it[1]]])
    // // ch_genome_input.view()
    // ch_prokka_res = prokka(ch_genome_input)
    // ch_prokka_res_gff =  ch_prokka_res.gff.collect({it[1]})
    // ch_prokka_res_gff.view()
    // roary(ch_prokka_res_gff)
    
    // ch_reads_input = channel.fromQuery("SELECT sample_name,fastq1,fastq2 from t_samples WHERE sample_name in ('EG_fecal_iso2_SRR15043922','EG_fecal_iso5_SRR15043921','EG_liver_iso1_SRR15043782','EG_liver_iso2_SRR15043781','EG_liver_iso3_SRR15043780','EG_liver_iso4_SRR15043779','EG_liver_iso5_SRR15043778','EG_liver_iso6_SRR15043777','EG_fecal_iso1_SRR15043776','EG_fecal_iso3_SRR15043775','EG_fecal_iso4_SRR15043774')", db: 'foo')
    // ch_reads_input = ch_reads_input.first()
    ch_reads_input = channel.fromQuery("SELECT sample_name,fastq1,fastq2 from t_samples WHERE project='fecal_liver' and is_available=1 and assay_type='WGS'", db: 'foo')
    ch_reads_input = ch_reads_input.map(it->[[id:it[0]],[it[1],it[2]]])
    ch_clean_reads = fastp(ch_reads_input)
   
    breseq(ch_clean_reads.reads,"/ssd1/wy/workspace2/paper/Wthin_host_evolution_of_a_gut_pathobiont_facilitates_liver_translocation/with_long_reads_assembly/prokka/EG_F1_FE14.gbk")

    // spades-> prokka -> roary
    ch_spades_res =  spades(ch_clean_reads.reads)
    // ch_spades_res.scaffolds.view()
    // https://www.ncbi.nlm.nih.gov/datasets/taxonomy/1353/
    ch_prokka_res = prokka(ch_spades_res.scaffolds,"Bacteria","Enterococcus")
    ch_prokka_res_gff =  ch_prokka_res.gff.collect({it[1]})
    ch_prokka_res_gff.view()
    roary(ch_prokka_res_gff)
}