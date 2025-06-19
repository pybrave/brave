process roary {
    publishDir "output/roary", mode: 'copy', overwrite: true
    input:
        path(gff)
    output:
        path("*")
    
    script:
    """
    export PATH=/home/jovyan/.conda/envs/roary/bin:\$PATH
    roary -f . -e -n -v  *.gff
    """
}