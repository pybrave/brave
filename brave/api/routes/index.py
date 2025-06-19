from fastapi import APIRouter
html_index = APIRouter()


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    index_path = os.path.join(frontend_path, "index.html")
    return FileResponse(index_path)