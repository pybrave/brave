include { fromQuery } from 'plugin/nf-sqldb'
include { prokka } from './modules/prokka.nf'
include {fastp} from './modules/fastp.nf'
include {roary} from './modules/roary.nf'
include {spades} from './modules/spades.nf'
workflow{
    // println("11111111111111")
    ch_genome_input = channel.fromQuery("select name,fasta from t_genome where project= 'leipu'", db: 'foo')
    ch_genome_input = ch_genome_input.map(it->[[id:it[0]],[it[1]]])
    // ch_genome_input.view()
    // https://www.ncbi.nlm.nih.gov/datasets/taxonomy/1622/
    ch_prokka_res = prokka(ch_genome_input,"Bacteria","Ligilactobacillus")
    ch_prokka_res_gff =  ch_prokka_res.gff.collect({it[1]})
    ch_prokka_res_gff.view()
    roary(ch_prokka_res_gff)
    


}