from sqlalchemy import and_

def build_where_clause(model_instance, table,field_list ):
    conditions = []
    for field, value in model_instance.dict(exclude_none=True).items():
        if field in field_list:
            column = getattr(table.c, field)
            conditions.append(column == value)
    return and_(*conditions)
