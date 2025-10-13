from brave.main import create_app
import uvicorn
import typer
import os
from brave.api.config.db import init_engine
# from brave.api.config.config import get_settings
from brave.api.config.db import meta,Base

app = typer.Typer()



@app.command()
def main(
    host: str = typer.Option("0.0.0.0", help="Host to bind"), 
    port: int =  typer.Option(5000, help="Port to bind"),
    reload: bool =  typer.Option(False, help="reload"),
    use_https: bool =  typer.Option(False, help="Use https"),
    base_dir: str =typer.Option(None, help="Base directory"),
    work_dir: str =typer.Option(None, help="Work directory"),
    store_dir: str =typer.Option(None, help="Store directory"),
    pipeline_dir: str =typer.Option(None, help="Pipeline directory"),
    literature_dir: str =typer.Option(None, help="Literature directory"),
    mysql_url: str =typer.Option(None, help="Mysql url"),
    # db_type: str =typer.Option("sqlite", help="Db type[ mysql, sqlite ]"),
    executer_type: str =typer.Option("docker", help="Executer Type [local, docker]")
    
    ):
    
    
    # os.environ["DB_TYPE"] = db_type
    os.environ["EXECUTER_TYPE"] = executer_type
    if store_dir:
        os.environ["STORE_DIR"] = store_dir
    if mysql_url:
        os.environ["MYSQL_URL"] = mysql_url
    if base_dir:
        os.environ["BASE_DIR"] = base_dir
    if work_dir:
        os.environ["WORK_DIR"] = work_dir
    if pipeline_dir:
        os.environ["PIPELINE_DIR"] = pipeline_dir
    if literature_dir:
        os.environ["LITERATURE_DIR"] = literature_dir


    # settings = get_settings()
    engine = init_engine()

    meta.create_all(engine)
    Base.metadata.create_all(bind=engine)

    cret_path = os.path.join(os.path.dirname(__file__), "cert")

    # typer.echo(f"base_dir={base_dir}, host={host}, port={port}")
    if use_https:
        uvicorn.run("brave.main:create_app", 
                    host=host, 
                    port=port, 
                    ssl_keyfile=f"{cret_path}/key.pem",
                    ssl_certfile=f"{cret_path}/cert.pem",
                    factory=True,
                    reload=reload)
    else:
        uvicorn.run("brave.main:create_app", 
                    host=host, 
                    port=port, 
                    factory=True,
                    reload=reload)


if __name__ == "__main__":
    app()