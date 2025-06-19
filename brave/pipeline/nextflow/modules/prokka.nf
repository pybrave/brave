process prokka {
    publishDir "output/prokka/${meta.id}", mode: 'symlink', overwrite: true


    input:
    tuple  val(meta),path(fasta)
    val(kingdom)
    val(genus)

    output:
    tuple val(meta),path("*.fna"), emit:fna
    tuple val(meta),path("*.gff"), emit:gff 
    tuple val(meta),path("*.gbk"), emit:gbk 
    tuple val(meta),path("*.faa"), emit:faa 
    // path("*.tbl"), emit:tbl 
    // path("*.faa"), emit:faa 
    // path("*.fsa"), emit:fsa 
    // path("*.tsv"), emit:tsv 
    // path("*.log"), emit:log
    tuple val(meta), path("*")

    script:
    """
    export PATH=/home/jovyan/.conda/envs/prokka/bin:\$PATH
    #sleep 600
    prokka --locustag LM --addgenes  --rfam   --force --kingdom ${kingdom} --genus ${genus} --outdir .  --prefix ${meta.id}  ${fasta}
    """

    stub:
    """
    
    """
}
