def get_ids(values):
    if isinstance(values, dict):
        if "file" in values:
            return [values['file']]
        elif "sample" in values:
            return values['sample']
        elif "value" in values and  "label" in values:
            return values['value']
        else:
            return []
    return values

def get_group(values):
    if isinstance(values, dict):
        if "group" in  values:
            if type(values["group"]) is dict:
                group_dict = values["group"]
                return { k:"-".join(v) for k,v in group_dict.items()}

            if len(values["group"]) ==1:
                return values["group"][0]
            elif len(values["group"]) >1:
                return "-".join(values["group"])
    return "-"

def get_re_group(values):
    if isinstance(values, dict):
        group_name = values.get("group_name","-")
        if isinstance(group_name, dict):
            group_name = {k:v for k,v in group_name.items() if v is not None  and  v!=""}
            # if not group_name:
            #     return "-"
        return group_name
    return "-"
def get_colors(values):
    if isinstance(values, dict):
        return values.get("color","-")
    return "-"
# def get_columns(values,samples_dict):
#     if isinstance(values, dict):
#         if "file" in  values:
#             sample_name_list = [ {
#                  "colname_name":item,
#                 **samples_dict.get(item,{})
#             } for item in values["sample"]]
            
#             return sample_name_list
#     return "-"