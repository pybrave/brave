process spades{
    publishDir "output/spades", mode: 'symlink', overwrite: true

    input:
    tuple val(meta),path(reads)
    output:
    tuple val(meta),path("${meta.id}/scaffolds.fasta"), emit:scaffolds
    tuple val(meta),path("*")
    
    script:
    """
    /ssd1/wy/workspace2/software/SPAdes-4.1.0-Linux/bin/spades.py \
         --isolate  \
         -1 ${reads[0]} \
         -2 ${reads[1]} \
         -o ${meta.id} \
         -t $task.cpus
    """
}


process spades_with_long_reads {
    publishDir "output/spades", mode: 'copy', overwrite: true

    input:
    tuple val(meta),path(reads)
    path(long_reads)
    output:
    tuple val(meta),path("pacbio_assembly_${meta.id}/scaffolds.fasta"), emit:scaffolds
    tuple val(meta),path("*")
    
    script:
    """
    /ssd1/wy/workspace2/software/SPAdes-4.1.0-Linux/bin/spades.py \
         --isolate  \
         -1 ${reads[0]} \
         -2 ${reads[1]} \
         -o pacbio_assembly_${meta.id} \
         --pacbio ${long_reads} \
         -t $task.cpus
    """
}