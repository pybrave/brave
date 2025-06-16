process seqkit {
    publishDir "output/seqkit", mode: 'symlink', overwrite: true

    input:
    path(fastq_files)
    val(name)

    output:
    path("*.tsv"),emit:tsv

    script:
    """
    export PATH=/home/jovyan/.conda/envs/seqkit/bin:\$PATH
    seqkit -j ${task.cpus} stats *fastq.gz -T  -a > ${name}.tsv

    """

    stub:
    """
    """
}


process seqkitV2 {
    publishDir "output/seqkit", mode: 'symlink', overwrite: true

    input:
    path(fastq_files)
    val(name)
    val(suffix)

    output:
    path("*.tsv"),emit:tsv

    script:
    """
    export PATH=/home/jovyan/.conda/envs/seqkit/bin:\$PATH
    seqkit -j ${task.cpus} stats ${suffix} -T  -a > ${name}.tsv

    """

    stub:
    """
    """
}