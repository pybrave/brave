

def parse_data(analysis_dict,database_dict,extra_dict,groups_name,groups,settings,metadata_form):
    return {
        **extra_dict,
        **analysis_dict,
        **database_dict,
        "groups_name":groups_name,
        "groups":groups,
        "pipeline_dir":str(settings.PIPELINE_DIR),
        "metadata_form":metadata_form
    
    }