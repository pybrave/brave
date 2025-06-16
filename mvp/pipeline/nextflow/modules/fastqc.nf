process fastqc {
    publishDir "output/fastqc/${name}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(reads)
    val(name)

    output:
    tuple val(meta), path("*.html"), emit: html
    tuple val(meta), path("*.zip") , emit: zip

    script:
    """
    export PATH=/home/jovyan/.conda/envs/fastqc/bin:\$PATH
    fastqc -t ${task.cpus} -o . ${reads}
    """

    stub:
    """
    
    """
}

process fastqcV2 {
    publishDir "output/fastqc/${name}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(reads)
    val(name)

    output:
    tuple val(meta), path("*.html"), emit: html
    tuple val(meta), path("*.zip") , emit: zip
    
    script:
    def reads1 = reads[0].toString().replace(".fastq.1.gz","_1.fastq")
    def reads2 = reads[1].toString().replace(".fastq.2.gz","_2.fastq")

    """
    mv ${reads[0]} ${reads1}
    mv ${reads[1]} ${reads2}
    export PATH=/home/jovyan/.conda/envs/fastqc/bin:\$PATH
    fastqc -t ${task.cpus} -o . ${reads1} ${reads2}
    """

    stub:
    """
    
    """
}