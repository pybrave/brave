import glob
import os
import json 


def get_content(file):
    return json.dumps({
        "genefamilies":file,
        "pathabundance":file.replace("_genefamilies.tsv","_pathabundance.tsv"),
        "pathabundance":file.replace("_genefamilies.tsv","_pathcoverage.tsv"),
        "pathabundance":file.replace("_genefamilies.tsv","_bowtie2_aligned.tsv"),
        "pathabundance":file.replace("_genefamilies.tsv","_diamond_aligned.tsv"),
        "pathabundance":file.replace("_genefamilies.tsv",".log"),
    })

def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*/*_genefamilies.tsv")
    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file).replace("_genefamilies.tsv",""),"humann","json",get_content(file)) for file in file_list]
    # print(result_data)
    return result_data
