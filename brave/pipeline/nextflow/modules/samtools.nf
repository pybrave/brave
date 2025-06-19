process samtools_remove_hosts {
    publishDir "output/samtools_remove_hosts", mode: 'symlink', overwrite: true

    input:
    tuple val(meta),path(bam)

    output:
    tuple val(meta),path("*.fastq.gz") ,emit:fastq

    script:
    """
    export PATH=/home/jovyan/.conda/envs/bowtie2/bin:\$PATH

    samtools view  \
        -@ task.cpus \
        -b -f 12 -F 256 \
        ${bam} > ${meta.id}_bothReadsUnmapped.bam 
    
    samtools sort -n  -@ ${task.cpus} \
        ${meta.id}_bothReadsUnmapped.bam \
         -o ${meta.id}_bothReadsUnmapped_sorted.bam

    samtools fastq -@ ${task.cpus} ${meta.id}_bothReadsUnmapped_sorted.bam \
        -1 ${meta.id}_host_removed_R1.fastq.gz \
        -2 ${meta.id}_host_removed_R2.fastq.gz \
        -0 /dev/null -s /dev/null -n

    """

    stub:
    """
    
    """
}

process samtools_remove_hostsV2 {
    publishDir "output/samtools_remove_hosts", mode: 'symlink', overwrite: true

    input:
    tuple val(meta),path(bam)

    output:
    tuple val(meta),path("*.fastq.gz") ,emit:fastq

    script:
    """
    export PATH=/home/jovyan/.conda/envs/bowtie2/bin:\$PATH
    
    samtools view  \
        -@ task.cpus \
        -b -f 12 -F 256 \
        ${bam} > ${meta.id}_bothReadsUnmapped.bam 
    
    samtools sort -n  -@ ${task.cpus} \
        ${meta.id}_bothReadsUnmapped.bam \
         -o ${meta.id}_bothReadsUnmapped_sorted.bam

    samtools fastq -@ ${task.cpus} ${meta.id}_bothReadsUnmapped_sorted.bam \
        -1 ${meta.id}_host_removed_R1.fastq.gz \
        -2 ${meta.id}_host_removed_R2.fastq.gz \
        -0 /dev/null -s /dev/null -n

    """

    stub:
    """
    
    """
}