process bowtie2 {
    tag "$meta.id"
    publishDir "output/bowtie2/${meta.id}", mode: 'symlink', overwrite: true
    // publishDir "/data2/wangyang/storeDir/test/${meta.id}", mode: 'copy', overwrite: true

    // storeDir '/data2/wangyang/storeDir/test2'

    input:
    tuple val(meta),path(reads)
    val(reference)

    output:
    tuple val(meta), path("*.{bam,sam}"), emit: aligned, optional:true
    tuple val(meta), path("*.log")      , emit: log
    tuple val(meta), path("*fastq.*.gz")  , emit: fastq, optional:true


    script:
    """
    export PATH=/home/jovyan/.conda/envs/bowtie2/bin:\$PATH
    bowtie2 \
        -x ${reference} \
        -1 ${reads[0]} -2 ${reads[1]} \
        --threads ${task.cpus} \
        --un-conc  ${meta.id}.unmapped.fastq.gz \
        2> >(tee ${meta.id}.bowtie2.log >&2) \
        | samtools view --threads $task.cpus -bS -o ${meta.id}.bam
    """

    stub:
    """
    
    """
}

process bowtie2V2 {
    tag "$meta.id"
    publishDir "output/bowtie2/${meta.id}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(reads)
    val(reference)

    output:
    tuple val(meta), path("*.{bam,sam}"), emit: aligned, optional:true
    tuple val(meta), path("*.log")      , emit: log
    tuple val(meta), path("*fastq.*.gz")  , emit: fastq, optional:true


    script:
    """
    export PATH=/home/jovyan/.conda/envs/bowtie2/bin:\$PATH
    bowtie2 \
        -x ${reference} \
        -1 ${reads[0]} -2 ${reads[1]} \
        --threads ${task.cpus} \
        --un-conc-gz  ${meta.id}.unmapped.fastq.gz \
        2> >(tee ${meta.id}.bowtie2.log >&2) \
        | samtools view --threads $task.cpus -bS -o ${meta.id}.bam
    """

    stub:
    """
    
    """
}


process bowtie2V3 {
    tag "$meta.id"
    publishDir "output/bowtie2/${meta.id}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(reads),path(reference)
    // tuple val(metaRef),path(reference)

    output:
    tuple val(meta), path("*.{bam,sam}"), emit: aligned, optional:true
    tuple val(meta), path("*.log")      , emit: log
    tuple val(meta), path("*fastq.*.gz")  , emit: fastq, optional:true
    tuple val(meta), path("*.bai")  , emit: bai, optional:true


    script:
    """
    export PATH=/home/jovyan/.conda/envs/bowtie2/bin:\$PATH
    bowtie2 \
        -x ${reference}/${meta.reference} \
        -1 ${reads[0]} -2 ${reads[1]} \
        --threads ${task.cpus} \
        2> >(tee ${meta.id}.bowtie2.log >&2) \
        | samtools view --threads $task.cpus -bS \
        | samtools sort -@ ${task.cpus} -o ${meta.id}.sorted.bam
    samtools index ${meta.id}.sorted.bam
    """

    stub:
    """
    
    """
}
// --un-conc-gz


process bowtie2_index {
    input:
    tuple val(meta),path(fasta)

    output:
    tuple val(meta),path("${meta.id}") ,emit:index

    script:
    """
    export PATH=/home/jovyan/.conda/envs/bowtie2/bin:\$PATH
    [ ! -d ${meta.id} ] && mkdir -p ${meta.id}

    bowtie2-build --threads ${task.cpus} ${fasta} ${meta.id}/${meta.id}

    """

    stub:
    """
    
    """
}