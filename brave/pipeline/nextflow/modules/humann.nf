process  humann{
    publishDir "output/humann", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(reads),path(profile)

    output:
    tuple val(meta), path("${meta.id}/*"), emit: all
    tuple val(meta),path("${meta.id}/*pathabundance.tsv"), emit:pathabundance
    tuple val(meta),path("${meta.id}/*genefamilies.tsv"), emit:genefamilies
    tuple val(meta),path("${meta.id}/*pathcoverage.tsv"), emit:pathcoverage

    script:
    """
    cat $reads >  ${meta.id}.clean.gz
    export PATH=/home/jovyan/.conda/envs/humann3.9/bin:\$PATH
    humann --nucleotide-database /data/databases/humann/chocophlan_v31_201901 \
        --protein-database /data/databases/humann/uniref90_v201901_ec_filtered \
        --input ${meta.id}.clean.gz    \
        --threads ${task.cpus}  \
        --taxonomic-profile ${profile} \
        -o ${meta.id}
    rm ${meta.id}.clean.gz
    mv ${meta.id}/${meta.id}_humann_temp/${meta.id}_bowtie2_aligned.tsv ${meta.id}
    mv ${meta.id}/${meta.id}_humann_temp/${meta.id}_diamond_aligned.tsv  ${meta.id}
    mv ${meta.id}/${meta.id}_humann_temp/${meta.id}.log  ${meta.id}
    rm -rf ${meta.id}/${meta.id}_humann_temp
    """

    stub:
    """
    
    """
}