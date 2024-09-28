from starlette.responses import FileResponse
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def read_index():
    return FileResponse('form.html')




@app.get("/final")
async def final():
    # get have form values
    # mess with files
    # llm stuff
    # finshed test/answer key
    
    return FileResponse('finshed-test.html')