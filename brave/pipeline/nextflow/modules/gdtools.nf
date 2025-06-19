process gdtools_compare {
    publishDir "output/gdtools/${reference_name}", mode: 'copy', overwrite: true

    input:
    path(annotated_gd),stageAs:'annotated*.gd'
    path(reference)
    val(reference_name)
    output:
    path("*")

    script:
    """
    export PATH=/home/jovyan/.conda/envs/iqtree/bin:\$PATH
    /ssd1/wy/workspace2/software/breseq-0.39.0-Linux-x86_64/bin/gdtools COMPARE \
        -r ${reference} \
        -o compare.html \
        ${annotated_gd}

    /ssd1/wy/workspace2/software/breseq-0.39.0-Linux-x86_64/bin/gdtools COMPARE \
        -r ${reference} \
        -f TSV \
        -o compare.tsv \
        ${annotated_gd}
    /ssd1/wy/workspace2/software/breseq-0.39.0-Linux-x86_64/bin/gdtools COMPARE \
        -r ${reference} \
        -f GD \
        -o compare.gd \
        ${annotated_gd}

     /ssd1/wy/workspace2/software/breseq-0.39.0-Linux-x86_64/bin/gdtools COUNT \
        -r ${reference} \
        -o count.tsv \
        ${annotated_gd}

    /ssd1/wy/workspace2/software/breseq-0.39.0-Linux-x86_64/bin/gdtools PHYLOGENY \
        -r ${reference} \
        -o phylogeny.phy  \
        ${annotated_gd}
    """

    stub:
    """
    
    """
}


process gdtools_sample {
    publishDir "output/breseq/${reference_name}/${meta.id}/data", mode: 'copy', overwrite: true

    input:
    tuple val(meta),path(gd)
    path(reference)
    val(reference_name)
    output:
    path("*")

    script:
    """
    export PATH=/home/jovyan/.conda/envs/iqtree/bin:\$PATH
   

    /ssd1/wy/workspace2/software/breseq-0.39.0-Linux-x86_64/bin/gdtools COMPARE \
        -r ${reference} \
        -f TSV \
        -o annotated.tsv \
        ${gd}

     /ssd1/wy/workspace2/software/breseq-0.39.0-Linux-x86_64/bin/gdtools COUNT \
        -r ${reference} \
        -o annotated.count  \
        ${gd}
    echo "${reference_name}" > reference.name
  
    """

    stub:
    """
    
    """
}