

def parse_data(analysis_dict,
               database_dict,
               colors,
               extra_dict,groups_name,re_groups_name,groups,settings,metadata_form):
    # sample_list = [{
    #                     "sample_name":item["sample_name"],
    #                     "sample_source":item["sample_source"],
    #                     "analysis_result_id":item["analysis_result_id"],
    #                     "sample_id":item["sample_id"]
    #                 }
    #                for v in analysis_dict.values() 
    #                for item in v]
    
    return {
        # "sample_list":sample_list,
        **extra_dict,
        **analysis_dict,
        **database_dict,
        "colors":colors,
        "groups_name":groups_name,
        "re_groups_name":re_groups_name,
        "groups":groups,
        "pipeline_dir":str(settings.PIPELINE_DIR),
        "metadata_form":metadata_form
    
    }