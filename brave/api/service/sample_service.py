from brave.api.models.core import samples

def find_by_sample_name(conn,sample_name):
    stmt = samples.select().where(samples.c.sample_name==sample_name)
    result = conn.execute(stmt).mappings().first()
    return result

def find_by_sample_name_and_project(conn,sample_name,project):
    stmt = samples.select().where(samples.c.sample_name==sample_name,samples.c.project==project)
    result = conn.execute(stmt).mappings().first()
    return result
    
def add_sample(conn,sample_data:dict):
    stmt = samples.insert().values(sample_data)
    conn.execute(stmt)


def find_by_sample_name_list(conn,sample_name_list):
    stmt = samples.select().where(samples.c.sample_name.in_(sample_name_list))
    result = conn.execute(stmt).mappings().all()
    return result


def find_by_project(conn,project):
    stmt = samples.select().where(samples.c.project==project)
    result = conn.execute(stmt).mappings().all()
    return result

def find_by_project_in_list(conn,project_list):
    stmt = samples.select().where(samples.c.project.in_(project_list))
    result = conn.execute(stmt).mappings().all()
    return result