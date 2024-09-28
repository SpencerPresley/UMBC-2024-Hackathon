from typing import Annotated
from typing import List

from starlette.responses import FileResponse
from fastapi import FastAPI, UploadFile, Form, File


app = FastAPI()

@app.get("/")
def read_index():
    return FileResponse('form.html')

@app.post("/generate")
def final(
    title: str = Form(...),
    course: str = Form(...),
    professor: str = Form(...),
    number_of_mcq_questions: int = Form(...),
    number_of_written_questions: int = Form(...),
    number_of_TF_questions: int = Form(...),
    school_type: str = Form(...),
    testing_philosophy: str = Form(...),
    difficulty: str = Form(...),
    subject_material: list[UploadFile] = File(...)
    
):
    print("hi")
    # get have form values
    # mess with files
    # llm stuff
    # finshed test/answer key

    return FileResponse('finshed_test.html')