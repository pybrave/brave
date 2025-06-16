include {fastp} from './modules/fastp.nf'
include {bowtie2_index} from './modules/bowtie2.nf'

include {bowtie2V3 as bowtie2} from './modules/bowtie2.nf'
include {feature_counts} from './modules/subread.nf'
workflow {
    ch_input = channel.fromList(params.samples).map(it->[[id:it.sample_key],[it.fastq1,it.fastq2]])
    ch_clean_reads = fastp(ch_input)
    
    ch_genome_assembly_input =  channel.of(params.genome_assembly).map(it->[[id:it.analysis_key],it.fasta])
    // ch_genome_assembly_input.view()
    ch_bowtie2_index_out =  bowtie2_index(ch_genome_assembly_input)
    // ch_bowtie2_index_out.index.view()
    ch_combine_reads_index = ch_clean_reads.reads
        .combine(ch_bowtie2_index_out.index)
        .map(it->[[id:it[0].id,reference:it[2].id],it[1],it[3]])
    // ch_combine_reads_index.view()
    ch_bowtie2_out =  bowtie2(ch_combine_reads_index)
    ch_gff = channel.of(params.genome_gff)
    ch_combine_bam_gff = ch_bowtie2_out.aligned
        .combine(ch_gff)
        .map(it->[[id:it[0].id,reference:it[0].reference,gff:it[2].analysis_key ],it[1],it[2].gff ]).view()

    // ch_gff = channel.value(params.genome_gff.gff)
    feature_counts(ch_combine_bam_gff)
}
