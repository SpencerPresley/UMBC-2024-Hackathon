from starlette.responses import FileResponse
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def read_index():
    return FileResponse('form.html')