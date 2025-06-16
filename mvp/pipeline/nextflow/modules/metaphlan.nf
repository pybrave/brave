process metaphlan {
    publishDir "output/metaphlan/${meta.id}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(reads)
    val(metaphlan_db_latest)

    output:
    tuple val(meta), path("*_profile.txt")   ,                emit: profile
    tuple val(meta), path("*.biom")          ,                emit: biom
    tuple val(meta), path('*.bowtie2out.txt'), optional:true, emit: bt2out

    script:
    """
    export PATH=/home/jovyan/.conda/envs/metaphlan/bin:\$PATH
    mv ${reads[0]} reads1.fastq
    mv ${reads[1]} reads2.fastq
    metaphlan \
        --nproc $task.cpus \
        --input_type fastq \
        reads1.fastq,reads2.fastq \
        --bowtie2out ${meta.id}.bowtie2out.txt \
        --biom ${meta.id}.biom \
        --output_file ${meta.id}_profile.txt \
        --bowtie2db $metaphlan_db_latest  \
        --index mpa_vJun23_CHOCOPhlAnSGB_202403  
    """

    stub:
    """
    
    """
}


process metaphlanV2 {
    publishDir "output/metaphlan/${meta.id}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(reads)
    val(metaphlan_db_latest)

    output:
    tuple val(meta), path("*_profile.txt")   ,                emit: profile
    tuple val(meta), path("*.biom")          ,                emit: biom
    tuple val(meta), path('*.bowtie2out.txt'), optional:true, emit: bt2out

    script:
    """
    export PATH=/home/jovyan/.conda/envs/metaphlan/bin:\$PATH
    metaphlan \
        --nproc $task.cpus \
        --input_type fastq \
        ${reads[0]},${reads[1]} \
        --bowtie2out ${meta.id}.bowtie2out.txt \
        --biom ${meta.id}.biom \
        --output_file ${meta.id}_profile.txt \
        --bowtie2db $metaphlan_db_latest  \
        --index mpa_vJun23_CHOCOPhlAnSGB_202403  
    """

    stub:
    """
    
    """
}


process metaphlan_marker_counts {
    publishDir "output/metaphlan_marker_counts/${meta.id}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(bowtie2out)
    val(metaphlan_db_latest)

    output:
    tuple val(meta), path("*")
    // tuple val(meta), path("*_profile.txt")   ,                emit: profile
    // tuple val(meta), path("*.biom")          ,                emit: biom
    // tuple val(meta), path('*.bowtie2out.txt'), optional:true, emit: bt2out

    script:
    """
    export PATH=/home/jovyan/.conda/envs/metaphlan/bin:\$PATH
    metaphlan \
        --nproc $task.cpus \
        -t marker_counts   \
        --input_type bowtie2out  \
        ${bowtie2out} \
        --output_file ${meta.id}_marker_counts.0.txt \
        --bowtie2db $metaphlan_db_latest  \
        --index mpa_vJun23_CHOCOPhlAnSGB_202403  
    
    awk -F'\\t' 'NR < 5 || \$2 != 0' ${meta.id}_marker_counts.0.txt > ${meta.id}_marker_counts.txt
    rm  ${meta.id}_marker_counts.0.txt
    """

    stub:
    """
    
    """
}

process metaphlan_strain_tracker {
    publishDir "output/metaphlan_strain_tracker/${meta.id}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(bowtie2out)
    val(metaphlan_db_latest)
    val(clade)

    output:
    tuple val(meta), path("*")
    // tuple val(meta), path("*_profile.txt")   ,                emit: profile
    // tuple val(meta), path("*.biom")          ,                emit: biom
    // tuple val(meta), path('*.bowtie2out.txt'), optional:true, emit: bt2out

    script:
    """
    export PATH=/home/jovyan/.conda/envs/metaphlan/bin:\$PATH
    metaphlan \
        --nproc $task.cpus \
        -t clade_specific_strain_tracker   \
        --clade ${clade}  \
        --input_type bowtie2out  \
        ${bowtie2out} \
        --output_file ${meta.id}_marker_abundance.txt \
        --bowtie2db $metaphlan_db_latest  \
        --index mpa_vJun23_CHOCOPhlAnSGB_202403  
    
    """

    stub:
    """
    
    """
}

process import_metaphlan_profile {
    input:
    tuple val(meta), path(profile)
    val(project)
    val(version)
    // output:
    // val identifier

    script:
    """
    # profile, sample_key, sample_name,project        
    ipython /ssd1/wy/workspace2/nextflow/bin/import_metaphlan.ipynb ${profile} ${meta.id} ${meta.id}  ${project} ${version}
    """

    stub:
    """
    
    """
}

// https://github.com/biobakery/MetaPhlAn/blob/master/metaphlan/metaphlan.py
// bowtie2 --sam-no-hd --sam-no-sq --no-unal --very-sensitive -S metagenome.sam -x ${mpa_dir}/metaphlan_databases/mpa_v30_CHOCOPhlAn_201901 -U metagenome.fastq\
process metaphlan_bowtie2 {
    publishDir "output/metaphlan_bowtie2/${meta.id}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(reads)
    val(reference)

    output:
    tuple val(meta), path("*.{bam,sam}"), emit: aligned, optional:true
    tuple val(meta), path("*.log")      , emit: log
    tuple val(meta), path("*fastq.gz")  , emit: fastq, optional:true


    script:
    """
    export PATH=/home/jovyan/.conda/envs/metaphlan/bin:\$PATH
    bowtie2 \
        -x ${reference} \
        -U ${reads[0]},${reads[1]} \
        --no-unal --very-sensitive \
        --seed 1992 \
        --threads ${task.cpus} \
        2> >(tee ${meta.id}.bowtie2.log >&2)  \
        | samtools view --threads $task.cpus -bS \
        | samtools sort -@ ${task.cpus} -o ${meta.id}.sorted.bam
    samtools index ${meta.id}.sorted.bam
    """
        // bowtie2 \
        // -x ${reference} \
        // -U ${reads[0]},${reads[1]} \
        // --sam-no-hd --sam-no-sq --no-unal --very-sensitive \
        // --threads ${task.cpus} \
        // -S ${meta.id}.sam \
        // 2> >(tee ${meta.id}.bowtie2.log >&2) 
    // if [ -f ${meta.id}.unmapped.fastq.1.gz ]; then
    //     mv ${meta.id}.unmapped.fastq.1.gz ${meta.id}.unmapped_1.fastq.gz
    // fi

    // if [ -f ${meta.id}.unmapped.fastq.2.gz ]; then
    //     mv ${meta.id}.unmapped.fastq.2.gz ${meta.id}.unmapped_2.fastq.gz
    // fi
    stub:
    """
    
    """
}

//  metaphlan metagenome.sam --input_type sam -o profiled_metagenome.txt
process metaphlan_sam {
    publishDir "output/metaphlan_sam/${meta.id}", mode: 'symlink', overwrite: true
    input:
    tuple val(meta),path(bam)
    val(metaphlan_db_latest)

    output:
    tuple val(meta), path("*_profile.txt")   ,                emit: profile
    tuple val(meta), path("*.biom")          ,                emit: biom
    tuple val(meta), path('*.bowtie2out.txt'), optional:true, emit: bt2out

    script:
    """
    export PATH=/home/jovyan/.conda/envs/metaphlan/bin:\$PATH
    samtools view  ${bam} > ${meta.id}.sam
    metaphlan \
        --nproc $task.cpus \
        --input_type sam \
        --nreads ${meta.nreads} \
        --stat_q ${params.stat_q} \
        ${meta.id}.sam \
        --bowtie2out ${meta.id}.bowtie2out.txt \
        --biom ${meta.id}.biom \
        --output_file ${meta.id}_profile.txt \
        --bowtie2db $metaphlan_db_latest  \
        --index mpa_vJun23_CHOCOPhlAnSGB_202403  
    rm ${meta.id}.sam 
    """

    stub:
    """
    
    """
}