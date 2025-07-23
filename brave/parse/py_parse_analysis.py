

def parse_data(analysis_dict,database_dict,extra_dict):
    return {
        **extra_dict,
        **analysis_dict,
        **database_dict
    
    }