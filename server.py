from typing import Annotated
from typing import List

from starlette.responses import FileResponse
from fastapi import FastAPI, UploadFile, Form, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

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
    data: Annotated[FormSettings, Form()],request: Request
    
):
    print("hi")
    
    return templates.TemplateResponse(
        request=request, name="finshed_test.html", context={"Title": data.title,"Class":data.course,"Professor":data.professor}
    )