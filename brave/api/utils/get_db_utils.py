def get_ids(values):
    if isinstance(values, dict):
        if "sample" in values:
            return values['sample']
        elif "value" in values and  "label" in values:
            return values['value']
        else:
            return []
    return values

def get_group(values):
    if isinstance(values, dict):
        if "group" in  values:
            if len(values["group"]) ==1:
                return values["group"][0]
            elif len(values["group"]) >1:
                return "-".join(values["group"])
    return "-"