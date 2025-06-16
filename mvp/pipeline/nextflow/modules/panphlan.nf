// Download the reference genomes
process  panphlan_download{
    publishDir "output/panphlan", mode: 'symlink', overwrite: true
    input:
    val species_name

    output:
    path("*")

    script:
    """
    export PATH=/home/jovyan/.conda/envs/panphlan/bin:\$PATH
    
    """

    stub:
    """
    
    """
}