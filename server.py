from starlette.responses import FileResponse
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from enum import Enum

class School_Type(Enum):
    Primary = 1
    Elementary = 2
    Middle = 3
    High = 4
    Undergraduate = 5
    Graduate = 6

class Difficulty(Enum):
    Easy = 1
    Medium = 2
    Hard = 3
    VeryHard = 4

class SettingsInfo(BaseModel):
    title: str
    course: str
    professor: str
    number_of_mcq_questions: int
    number_of_TF_questions: int
    number_of_written_questions: int
    school_type: School_Type
    difficulty: Difficulty
    testing_philosophy: str
    subject_material: list[UploadFile]

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