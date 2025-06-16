process  breseq {
    publishDir "output/breseq/${reference_name}", mode: 'symlink', overwrite: true

    input:
    tuple val(meta),path(reads)
    path(reference)
    val(reference_name)

    output:
    tuple val(meta),path("${meta.id}/data/annotated.gd") , emit:annotated_gd
    tuple val(meta),path("${meta.id}/*")

    script:
    """
    export PATH=/home/jovyan/.conda/envs/bowtie2/bin:\$PATH
    /ssd1/wy/workspace2/software/breseq-0.39.0-Linux-x86_64/bin/breseq \
        -j $task.cpus  \
        -r ${reference}   \
        --name ${meta.id} \
        ${reads[0]}  \
        ${reads[1]}  \
        -o ${meta.id}
        
    """

    stub:
    """
    
    """
}