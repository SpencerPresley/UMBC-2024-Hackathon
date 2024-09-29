from typing import Annotated
from typing import List
import logging

# from .pythonBackend import run
# for spencer
from pythonBackend import run
from starlette.responses import FileResponse
from fastapi import FastAPI, UploadFile, Form, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

class FormSettings(BaseModel):
    title: str
    course: str
    professor: str
    number_of_mcq_questions: int
    number_of_TF_questions: int
    number_of_written_questions: int
    school_type: str
    level: str
    difficulty: str
    testing_philosophy: str
    url_1: str | None
    url_2: str | None
    subject_material:List[UploadFile]

class QAPair(BaseModel):
    question:str
    answer: str
    type: str
    choices: List[str] = ['T', 'F'] #Holds Choices in a multiple Choice question
    
class GeneratedTest(BaseModel):
    questions:List[QAPair]

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
logger.info("Static files mounted")


#Used for converting Multiple Choice Numbers to Letters
def toLetter(num):
    return chr(num + 64)

templates.env.filters['toLetter'] = toLetter
logger.info("toLetter filter added to Jinja2 environment")

@app.get("/")
def read_index(request: Request):
    logger.info("GET request received for index page")
    return templates.TemplateResponse(
        request=request, name="form.html")

@app.post("/generate")
def final(
    data: Annotated[FormSettings, Form()],request: Request
    
):
    logger.info("POST request received for /generate")
    logger.info(f"Form data: {data}")
    try:
        test = run(data)
        logger.info("Test generated successfully")
    except Exception as e:
        logger.error(f"Error generating test: {e}")
        return templates.TemplateResponse(
            request=request, name="error.html", context={"error": str(e)}
        )

    fake_response=GeneratedTest(questions=[QAPair(question="What is 2+2?", answer="4", type="written"),QAPair(question="What is 1+2?",answer="3" , type="written"),QAPair(question="What is 1+3?",answer="4" , type="multiple", choices=["1", "2", "3", "4"]), QAPair(question="Does 2+2=4?", answer="T", type="TF")] )

    return templates.TemplateResponse(
        request=request, name="finshed_test.html", context={"Settings": data,"Test":fake_response}
    )