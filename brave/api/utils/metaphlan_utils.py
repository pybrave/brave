import pandas as pd
from functools import reduce
from itertools import chain
def get_last_num(clade_name,num):
    clade_name_list = clade_name.split('|')
    return clade_name_list[len(clade_name_list)-num]

def get_last(clade_name):
    clade_name_list = clade_name.split('|')
    return clade_name_list[len(clade_name_list)-1]
def set_rank(taxonomy):
    if taxonomy.startswith("t__"):
        return "SGB"
    if taxonomy.startswith("s__"):
        return "SPECIES"
    elif  taxonomy.startswith("g__"):
        return "GENUS"
    elif  taxonomy.startswith("f__"):
        return "FAMILY"
    elif  taxonomy.startswith("o__"):
        return "ORDER"
    elif  taxonomy.startswith("c__"):
        return "CLASS"
    elif  taxonomy.startswith("p__"):
        return "PHYLUM"
    elif  taxonomy.startswith("k__"):
        return "KINGDOM"
def rename_taxonomy(taxonomy):
    if taxonomy.startswith("t__"):
        return taxonomy.replace("t__","").replace("_"," ")
    if taxonomy.startswith("s__"):
        return taxonomy.replace("s__","").replace("_"," ")
    elif  taxonomy.startswith("g__"):
        return taxonomy.replace("g__","").replace("_"," ")
    elif  taxonomy.startswith("f__"):
        return taxonomy.replace("f__","").replace("_"," ")
    elif  taxonomy.startswith("o__"):
        return taxonomy.replace("o__","").replace("_"," ")
    elif  taxonomy.startswith("c__"):
        return taxonomy.replace("c__","").replace("_"," ")
    elif  taxonomy.startswith("p__"):
        return taxonomy.replace("p__","").replace("_"," ")
    elif  taxonomy.startswith("k__"):
        return taxonomy.replace("k__","").replace("_"," ")
def get_one_df(file,sample_key):
    df = pd.read_csv(file,sep="\t",comment="#",header=None)
    df.columns = ["clade_name","ncbi_tax_id","relative_abundance","additional_species"]
    df = df.rename({"relative_abundance":sample_key},axis=1)
    df = df.drop("additional_species",axis=1)
    df = df.set_index(["clade_name","ncbi_tax_id"])
    return df

    # metaphlan_sam_abundance = db_dict['metaphlan_sam_abundance']
def get_abundance(metaphlan_sam_abundance):
    df_list = [get_one_df(item['content']['profile'],item['sample_name']) for item in metaphlan_sam_abundance]
    df = reduce(lambda x,y:pd.merge(x,y,left_index=True,right_index=True, how="outer"),df_list)
    df = df.reset_index()
    df['taxonomy'] = df.apply(lambda x : get_last(x['clade_name']) ,axis=1)
    df['tax_id'] = df.apply(lambda x : get_last(x['ncbi_tax_id']) ,axis=1)
    df['rank'] = df.apply(lambda x : set_rank(x['taxonomy']) ,axis=1)
    df['taxonomy'] = df.apply(lambda x : rename_taxonomy(x['taxonomy']) ,axis=1)
    df = df.set_index(["clade_name","ncbi_tax_id","taxonomy","tax_id","rank"])
    df = df.fillna(0)
    
    # df.to_pickle("test/test.pkl")

    return df

# def get_metadata(control_sample,treatment_sample,control_group,treatment_group):
#     control_meta = pd.DataFrame([(item.sample_key,control_group) for item in control_sample],columns=['sample_key','group'])
#     treatment_meta = pd.DataFrame([(item.sample_key,treatment_group) for item in treatment_sample],columns=['sample_key','group'])
#     metadata = pd.concat([control_meta, treatment_meta], ignore_index=True)
#     metadata = metadata.set_index("sample_key")
#     return metadata

def get_metadata_group(db_dict,group,group_name):
    return pd.DataFrame([(item['sample_name'],group_name) for item in db_dict[group] ], columns=['sample_name','group'])

def get_metadata(db_dict,groups):
   df_list = [get_metadata_group(db_dict,group,group_name) for group,group_name in groups.items()]
   metadata = pd.concat(df_list, ignore_index=True)
   metadata = metadata.set_index("sample_name")
   return metadata



def get_abundance_metadata(request_param,db_dict,groups):
    samples = sum([db_dict[group] for group in groups],[])
    abundance = get_abundance(samples)
    groups = {group:"-".join(request_param[group]['group']) for group in groups}
    # control_sample = db_dict['control']
    # treatment_sample = db_dict['treatment']
    # control_group = "-".join(request_param['control']['group'])
    # treatment_group = "-".join(request_param['treatment']['group'])
    metadata = get_metadata(db_dict,groups)

    # metadata = get_metadata(control_sample,treatment_sample,control_group,treatment_group)
    # abundance1 = abundance.reset_index(["clade_name","taxonomy","tax_id","rank"])[["clade_name","taxonomy","tax_id","rank"]].reset_index(drop=True)
    rank = "SPECIES"
    if "rank" in request_param:
        rank = request_param['rank']
    abundance = abundance.reset_index(['taxonomy','rank']).reset_index(drop=True).query("rank==@rank").drop("rank",axis=1).set_index("taxonomy").T
    return abundance,metadata,groups


def get_abundance_metadata4(request_param,db_dict,groups):
    samples = sum([db_dict[group] for group in groups],[])
    abundance = get_abundance(samples)
    groups = {group:"-".join(request_param[group]['group']) for group in groups}
    # control_sample = db_dict['control']
    # treatment_sample = db_dict['treatment']
    # control_group = "-".join(request_param['control']['group'])
    # treatment_group = "-".join(request_param['treatment']['group'])
    metadata = get_metadata(db_dict,groups)

    # metadata = get_metadata(control_sample,treatment_sample,control_group,treatment_group)
    abundance1 = abundance.reset_index(["clade_name","taxonomy","tax_id","rank"])[["clade_name","taxonomy","tax_id","rank"]].reset_index(drop=True)
    rank = "SPECIES"
    if "rank" in request_param:
        rank = request_param['rank']
    abundance = abundance.reset_index(['taxonomy','rank']).reset_index(drop=True).query("rank==@rank").drop("rank",axis=1).set_index("taxonomy").T
    return abundance,metadata,groups,abundance1