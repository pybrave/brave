process fastp {
    publishDir "output/fastp", mode: 'symlink', overwrite: true

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path('*.fastp.fastq.gz') , optional:true, emit: reads
    tuple val(meta), path('*.json')           , emit: json
    tuple val(meta), path('*.html')           , emit: html

    script:
    def prefix = meta.id
    """
    export PATH=/home/jovyan/.conda/envs/fastp/bin:\$PATH
    fastp --in1 ${reads[0]}  --in2 ${reads[1]}  \\
        --out1 ${prefix}_1.fastp.fastq.gz  --out2 ${prefix}_2.fastp.fastq.gz \\
        --json ${prefix}.fastp.json \\
        --html ${prefix}.fastp.html \\
        --thread 10 \\
         --detect_adapter_for_pe \\
         2> ${prefix}.fastp.log
    """

    stub:
    """
    
    """
}