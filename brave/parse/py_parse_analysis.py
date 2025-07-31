

def parse_data(analysis_dict,database_dict,extra_dict,groups_name,groups):
    return {
        **extra_dict,
        **analysis_dict,
        **database_dict,
        "groups_name":groups_name,
        "groups":groups
    
    }