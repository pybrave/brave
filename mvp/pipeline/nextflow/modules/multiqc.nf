process multiqc {
    publishDir "output/multiqc", mode: 'symlink', overwrite: true

    input:
    path  multiqc_files, stageAs: "?/*"

    output:
    path "*multiqc_report.html", emit: report
    path "*_data"              , emit: data
    path "*_plots"             , optional:true, emit: plots
    path "multiqc_data/multiqc_data.json" , emit: json

    script:
    """
    export PATH=/home/jovyan/.conda/envs/multiqc/bin:\$PATH
    
    multiqc -f .
    """

    stub:
    """
    
    """
}