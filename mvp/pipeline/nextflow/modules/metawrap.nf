process metawrap_assembly{
    publishDir "output/metawrap_assembly", mode: 'symlink', overwrite: true

    input:
    tuple val(meta),path(reads)
    output:
    // tuple val(meta),path("${meta.id}/scaffolds.fasta"), emit:scaffolds
    tuple val(meta),path("*")
    
    script:
    def reads1 = reads[0].toString().replace(".gz","")
    def reads2 = reads[1].toString().replace(".gz","")

    """
    gunzip -c ${reads[0]} > ${reads1}
    gunzip -c ${reads[1]} > ${reads2}
    export PATH=/home/jovyan/.conda/envs/metawrap-env/bin:/ssd1/wy/workspace2/software/metaWRAP/bin:\$PATH
    metawrap assembly \
        -1 ${reads1} \
        -2 ${reads2} \
        -m ${task.memory.toGiga()} -t ${task.cpus} \
        --metaspades -o ${meta.id}
    """
}

process metawrap_assemblyV2{

    input:
    tuple val(meta),path(reads)
    output:
    // tuple val(meta),path("${meta.id}/scaffolds.fasta"), emit:scaffolds
    
    tuple val(meta),path("*/final_assembly.fasta"), emit: fasta
    tuple val(meta),path("*/*")
    
    script:
    def reads1 = reads[0].toString().replace(".gz","")
    def reads2 = reads[1].toString().replace(".gz","")

    """
    #gunzip -c ${reads[0]} > ${reads1}
    #gunzip -c ${reads[1]} > ${reads2}
    export PATH=/home/jovyan/.conda/envs/metawrap-env/bin:/ssd1/wy/workspace2/software/metaWRAP/bin:\$PATH
    metawrap assembly \
        -1 ${reads[0]} \
        -2 ${reads[1]} \
        -m ${task.memory.toGiga()} -t ${task.cpus} \
        --metaspades -o ${meta.id}
    """
}