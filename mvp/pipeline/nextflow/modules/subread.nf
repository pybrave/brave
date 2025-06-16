process feature_counts {
    tag "$meta.id"
    publishDir "output/feature_counts/${meta.id}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(bam),path(gff)

    output:
    tuple val(meta),path("*.count")
     tuple val(meta),path("*.summary")

    script:
    """
    export PATH=/home/jovyan/.conda/envs/subread/bin:\$PATH
    featureCounts -T ${task.cpus} -p  \
        -a  ${gff}  \
        -F GFF \
        -o ${meta.id}.count \
        -t gene  \
        -g ID  ${bam}

    """

    stub:
    """
    
    """
}