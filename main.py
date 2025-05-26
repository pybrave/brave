# https://github.com/FaztWeb/fastapi-mysql-restapi/blob/main/routes/user.py

from fastapi import FastAPI

from routes.file_parse_plot import file_parse_plot
from routes.sample_result import sample_result
from routes.sample import sample
from routes.analysis import analysis_api
app = FastAPI()

app.include_router(sample_result)
app.include_router(file_parse_plot)
app.include_router(sample)
app.include_router(analysis_api)

# @app.get("/")
# async def read_root():
#     time.sleep(10)
#     print("sleep")
#     print(threading.get_ident())
#     time.sleep(10)
#     print(threading.get_ident())
#     return {"Hello": "World"}
    
# @app.get("/abc")
# def read_root():
#     print("sleep")
#     print(threading.get_ident())
#     time.sleep(10)
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}