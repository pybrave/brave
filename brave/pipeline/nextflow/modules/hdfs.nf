process hdfs_put_single_file {
    input:
    path(input_file)
    val(project)
    val(version)
    val(software)
    

    script:
    """
    export PATH=/ssd1/wy/workspace2/software/hadoop-3.1.3/bin:\$PATH
    hdfs dfs -mkdir -p  /workspace/${project}/${version}/${software} 
    hdfs dfs -put -f ${input_file} /workspace/${project}/${version}/${software}/
    """

    stub:
    """
    
    """
}

process hdfs_put_single_file_meta {
    input:
    tuple val(meta),path(input_file)
    val(project)
    val(version)
    val(software)
    

    script:
    """
    export PATH=/ssd1/wy/workspace2/software/hadoop-3.1.3/bin:\$PATH
    hdfs dfs -mkdir -p  /workspace/${project}/${version}/${software}
    hdfs dfs -put  ${input_file} /workspace/${project}/${version}/${software}/
    """

    stub:
    """
    
    """
}