process sample2markers {
    publishDir "output/sample2markers/${meta.id}", mode: 'symlink', overwrite: true

    input:
    tuple val(meta), path(bam)
    val pkl

    output:
    tuple val(meta), path("*.json.bz2")

    script:
    """
    export PATH=/home/jovyan/.conda/envs/metaphlan/bin:\$PATH
    samtools view -h ${bam} -o ${meta.id}.sam
    sample2markers.py \
        -i ${meta.id}.sam  \
        -o . \
        -n ${task.cpus} \
        -f sam  \
        -d ${pkl}  
    rm ${meta.id}.sam
    """

    stub:
    """
    
    """
}

process strainphlan {
    publishDir "output/strainphlan", mode: 'symlink', overwrite: true
    input:
    path(json)
    val(reference)
    val(pkl)
    val(clade)
    
    output:
    tuple val(clade),path("*/*")
    tuple val(clade),path("*/RAxML_bestTree.*.StrainPhlAn4.tre") ,emit: bestTree

    
    script:
    def input_reference = reference?"-r ${reference}":""
    """
    [ -d ${clade.label} ] || mkdir -p ${clade.label}
    export PATH=/home/jovyan/.conda/envs/metaphlan/bin:\$PATH
    strainphlan  \
        -s *.json.bz2   \
        -o ${clade.label} \
        -n ${task.cpus}  \
        -c ${clade.value}   \
        --mutation_rates   \
        -d ${pkl} \
        ${input_reference} \
        --marker_in_n_samples 1 --sample_with_n_markers 10 --phylophlan_mode accurate 
    """

    stub:
    """
 
    """
}

process  tree_pairwisedists{
    publishDir "output/strainphlan/${clade.label}", mode: 'symlink', overwrite: true
    input:
    tuple val(clade),path(tree)

    output:
    tuple val(clade),path("*.tsv")

    script:
    """
    /ssd1/wy/workspace2/software/pyphlan/tree_pairwisedists.py  -n  ${tree} > ${clade.label}_tree_pairwisedists.tsv
    """

    stub:
    """
    
    """
}