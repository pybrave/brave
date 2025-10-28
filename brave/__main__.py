from brave.main import create_app
import uvicorn
import typer
import os
from brave.api.config.db import init_engine
# from brave.api.config.config import get_settings
from brave.api.config.db import meta,Base
from importlib.metadata import version, PackageNotFoundError

app = typer.Typer()


def version_callback(value: bool):
  if value:
        try:
            pkg_version = version("pybrave")  # 这里写你的包名
        except PackageNotFoundError:
            pkg_version = "unknow"  # 如果包未安装
        print(f"Brave Version {pkg_version}")
        raise typer.Exit()

@app.command(help="Bioinformatics Reactive Analysis and Visualization Engine.  https://pybrave.github.io/brave-doc/")
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the Brave's version.",
    ),
    host: str = typer.Option("0.0.0.0", help="Host to bind"), 
    port: int =  typer.Option(5000, help="Port to bind"),
    reload: bool =  typer.Option(False, help="reload"),
    use_https: bool =  typer.Option(False, help="Use https"),
    base_dir: str =typer.Option(None, help="Base directory"),
    work_dir: str =typer.Option(None, help="Work directory"),
    store_dir: str =typer.Option(None, help="Store directory"),
    code_dir: str =typer.Option(None, help="Code directory"),
    package_dir: str =typer.Option(None, help="Package directory"),
    analysis_dir: str =typer.Option(None, help="Analysis directory"),
    data_dir: str =typer.Option(None, help="Data directory"),
    neo4j_bolt: str =typer.Option(None, help="Neo4j bolt url neo4j:password@bolt://localhost:7687"),
    pipeline_dir: str =typer.Option(None, help="Pipeline directory"),
    literature_dir: str =typer.Option(None, help="Literature directory"),
    mysql_url: str =typer.Option(None, help="Mysql url"),
    # db_type: str =typer.Option("sqlite", help="Db type[ mysql, sqlite ]"),
    executer_type: str =typer.Option("docker", help="Executer Type [local, docker]")
    
    ):
    
    # os.environ["DB_TYPE"] = db_type
    os.environ["EXECUTER_TYPE"] = executer_type
    if neo4j_bolt:
        os.environ["NEO4J_BOLT"] = neo4j_bolt
    if code_dir:
        os.environ["CODE_DIR"] = code_dir
    if package_dir:
        os.environ["PACKAGE_DIR"] = package_dir
    if data_dir:
        os.environ["DATA_DIR"] = data_dir
    if analysis_dir:
        os.environ["ANALYSIS_DIR"] = analysis_dir
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