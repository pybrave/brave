def get_ids(values):
    if isinstance(values, dict):
        if "sample" in values:
            return values['sample']
        elif "value" in values and  "label" in values:
            return values['value']
        else:
            return []
    return values