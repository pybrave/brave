process kraken2 {
    publishDir "output/kraken2/${meta.id}", mode: 'symlink', overwrite: true

    input:
    tuple val(meta),path(reads)
    path  db

    output:
    tuple val(meta), path('*.classified{.,_}*')     , optional:true, emit: classified_reads_fastq
    tuple val(meta), path('*.unclassified#{.,_}*')   , optional:true, emit: unclassified_reads_fastq
    tuple val(meta), path('*classifiedreads.txt')   , optional:true, emit: classified_reads_assignment
    tuple val(meta), path('*report.txt')                           , emit: report

    script:
    """
    PATH=/home/jovyan/.conda/envs/kraken2/bin:\$PATH
    kraken2 \
        --db $db \
        --threads $task.cpus \
        --report ${meta.id}.kraken2.report.txt \
        --gzip-compressed \
        --unclassified-out ${meta.id}.unclassified#.fastq \
        --classified-out ${meta.id}.classified#.fastq \
        --output ${meta.id}.kraken2.classifiedreads.txt \
        ${reads}
    """

    stub:
    """
    
    """
}
process kraken2V2 {
    publishDir "output/kraken2/${meta.id}", mode: 'symlink', overwrite: true

    input:
    tuple val(meta),path(reads)
    path  db

    output:
    tuple val(meta), path('*.classified{.,_}*')     , optional:true, emit: classified_reads_fastq
    tuple val(meta), path('*.unclassified{.,_}*')   , optional:true, emit: unclassified_reads_fastq
    tuple val(meta), path('*classifiedreads.txt')   , optional:true, emit: classified_reads_assignment
    tuple val(meta), path('*report.txt')                           , emit: report

    script:
    def reads1 = reads[0].toString().replace(".fastq.1.gz","_1.fastq")
    def reads2 = reads[1].toString().replace(".fastq.2.gz","_2.fastq")

    """
    mv ${reads[0]} ${reads1}
    mv ${reads[1]} ${reads2}
    PATH=/home/jovyan/.conda/envs/kraken2/bin:\$PATH
    kraken2 \
        --db $db \
        --threads $task.cpus \
        --paired \
        --report ${meta.id}.kraken2.report.txt \
        --unclassified-out ${meta.id}.unclassified#.fastq \
        --classified-out ${meta.id}.classified#.fastq \
        --output ${meta.id}.kraken2.classifiedreads.txt \
        ${reads1} ${reads2}
    """
    // --paired \

    stub:
    """
    
    """
}
process bracken {
    publishDir "output/bracken/${meta.id}", mode: 'copy', overwrite: true

    input:
    tuple val(meta),path(report)
    path(db)

    output:
    tuple val(meta), path("${meta.id}.*.tsv")        , emit: reports

    script:
    """
    PATH=/home/jovyan/.conda/envs/kraken2/bin:\$PATH
    bracken \\
        -l D \\
        -d '${db}' \\
        -i '${report}' \\
        -o '${meta.id}.D.kraken.tsv'
    bracken \\
        -l K \\
        -d '${db}' \\
        -i '${report}' \\
        -o '${meta.id}.K.kraken.tsv'
    bracken \\
        -l P \\
        -d '${db}' \\
        -i '${report}' \\
        -o '${meta.id}.P.kraken.tsv'

    bracken \\
        -l C \\
        -d '${db}' \\
        -i '${report}' \\
        -o '${meta.id}.C.kraken.tsv'

    bracken \\
        -l O \\
        -d '${db}' \\
        -i '${report}' \\
        -o '${meta.id}.O.kraken.tsv'

    bracken \\
        -l F \\
        -d '${db}' \\
        -i '${report}' \\
        -o '${meta.id}.F.kraken.tsv'


    bracken \\
         -l G  \\
        -d '${db}' \\
        -i '${report}' \\
        -o '${meta.id}.G.kraken.tsv'
    bracken \\
         -l S  \\
        -d '${db}' \\
        -i '${report}' \\
        -o '${meta.id}.S.kraken.tsv'

    bracken \\
        -d '${db}' \\
        -l S1 \\
        -i '${report}' \\
        -o '${meta.id}.S1.kraken.tsv'

    
    """

    stub:
    """
    
    """
}



process kraken2_map {
    publishDir "output/bracken/${meta.id}", mode: 'copy', overwrite: true

    input:
    tuple val(meta), path(report)
    // path  db


    output:
    tuple val(meta), path('*kreport2mpa.txt') , emit: kreport2mpawy

    script:
    def prefix = task.ext.prefix ?: "${meta.id}"

    """
    kreport2mpa.py -r '${report}'  --percentages --keep-spaces -o ${prefix}_kreport2mpa.txt 
    """


}

process import_kraken_profile {
    input:
    tuple val(meta), path(profile)
    val(project)
    val(version)
    // output:
    // val identifier

    script:
    """
    # profile, sample_key, sample_name,project       
    ipython /ssd1/wy/workspace2/nextflow/bin/import_kraken.ipynb  ${meta.id} ${meta.id}  ${project} ${version}
    """

    stub:
    """
    
    """
}