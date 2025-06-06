def get_ids(values):
    if isinstance(values, dict):
        if "sample" in values:
            return values['sample']
    return values