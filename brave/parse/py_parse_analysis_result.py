import glob
import os
import json 

# "dir_path":dir_path,
# "analysis": result,
# "output_file":item['output_file'],
# "args":moduleArgs

def get_content(file,file_list,suffix,replace_map):
    content_dict = {}
   
    if suffix:
        # file_list = glob.glob(f"{file}/*")
        for item in file_list:
            analysis_name = get_analysis_name(item,suffix)
            filename = os.path.basename(item).replace(f"{analysis_name}.","").replace(analysis_name,"")
            if filename in replace_map:
                filename = replace_map[filename]
            content_dict[filename] = item
    else:
        # file_list = glob.glob(f"{file}/*/*")
        for item in file_list:
            analysis_name = get_analysis_name(item,suffix)
            filename = os.path.basename(item).replace(analysis_name,"")
            content_dict[filename] = item
    return json.dumps(content_dict)

        

def get_analysis_name(file,suffix):
    if suffix:
        return os.path.basename(file).replace(suffix,"")
    else:
        return os.path.dirname(file)

def parse(dir_path,analysis,output_file_name,pattern,suffix,replace_map):
    if not replace_map:
        replace_map = {}

    file_list = glob.glob(f"{dir_path}/{pattern}")
    result_data = []
    for file in file_list:
        analysis_name = get_analysis_name(file,suffix)
        content = get_content(file,file_list,suffix,replace_map)
        result_data.append((analysis_name, output_file_name,"json",content))


    return result_data





# def get_content(file):
#     return json.dumps({
#         "bam":file,
#         "log":file.replace(".bam","")+".bowtie2.log"
#     })

# def parse(dir_path,analysis):
#     file_list = glob.glob(f"{dir_path}/*/*.bam")
#     result_data = [(os.path.basename(file).replace(".bam",""),"bowtie2","json",get_content(file)) for file in file_list]
#     return result_data



# def get_json(file):
#     return json.dumps({
#         "fastq1":file,
#         "fastq2":file.replace("_host_removed_R1.fastq.gz","_host_removed_R2.fastq.gz")
#     })

# def parse(dir_path,analysis):
#     file_list = glob.glob(f"{dir_path}/*_host_removed_R1.fastq.gz")
#     result_data = [(os.path.basename(file).replace("_host_removed_R1.fastq.gz",""),"samtools","json",get_json(file)) for file in file_list]
#     return result_data

