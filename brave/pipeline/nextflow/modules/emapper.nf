process emapper {
    publishDir "output/prokka/${meta.id}", mode: 'symlink', overwrite: true

    input:
    tuple  val(meta),path(faa)

    output:
    tuple  val(meta),path("*")

    script:
    """
    export PATH=/home/jovyan/.conda/envs/eggnog-mapper/bin:\$PATH
    emapper.py  --data_dir  /data/wangyang/databases/eggnog-mapper-data   \
        --itype proteins   \
        -m diamond  \
        --cpu $task.cpus  \
        --output ${meta.id} \
        -i ${faa}

    sed -i  '5s/^#//' ${meta.id}.emapper.annotations  
    """

    stub:
    """
    
    """
}