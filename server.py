from typing import Annotated
from typing import List

from starlette.responses import FileResponse
from fastapi import FastAPI, UploadFile, Form, File
from pydantic import BaseModel

class FormSettings(BaseModel):
    title: str
    course: str
    professor: str
    number_of_mcq_questions: int
    number_of_TF_questions: int
    number_of_written_questions: int
    school_type: str
    difficulty: str
    testing_philosophy: str
    subject_material:List[UploadFile]

app = FastAPI()

@app.get("/")
def read_index():
    return FileResponse('form.html')

@app.post("/generate")
def final(
    data: Annotated[FormSettings, Form()]
    
):
    print("hi")
    # get have form values
    # mess with files
    # llm stuff
    # finshed test/answer key

    return FileResponse('finshed_test.html')