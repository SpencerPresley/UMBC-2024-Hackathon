import json
import os
from dotenv import load_dotenv
import logging

from PIL import Image
import pytesseract
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='chains.log',
    filemode='w'
)

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredPowerPointLoader

from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from pydantic import BaseModel
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from .custom_prompts import clean_files_system_prompt, clean_files_human_prompt, clean_files_json_format

class QAPair(BaseModel):
    question:str
    answer: str
    type: str
    choices: List[str] = ['T', 'F']#Holds Choices in a multiple Choice question
    
QAPair_json_format = """{
    questions: [
        {
            "question": <string: a question>
            "type": <question type, i.e., multiple choice, written, true/false,
            "answer": <string: the answer to the question>
            "choices": <choices: if true false ['T', 'F'], if multiple choice then ['a', 'b', 'c', etc.,]>
            ]
        }
    ] 
}"""


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.6,
    api_key=os.getenv("OPENAI_API_KEY"),
) 

question_generation_system_prompt = PromptTemplate(
    template="""
    You are an AI assistant tasked with generating reading comprehension questions based on the given input document. Your goal is to help the user assess and deepen their understanding of the material in an educational context.
    
    You should utilize all educational content from the provided document, prioritizing the most emphasized and important concepts.
    
    You will be generating {number_of_mcq_questions} multiple choice questions, {number_of_TF_questions} true/false questions, and {number_of_written_questions} written questions.
    
    You are to provide your answer in the following format:
    {QAPair_json_format}
    If {type} is multiple choice, populate {choices} with three incorrect solution and one correct solution in a random order. If {type} is True/False, leave {choices} as T, F. If {type} is a written question, leave {choices} blank.
    
    If you include anything but the question, type, answer, and and choices within the json, you have failed.
"""
)