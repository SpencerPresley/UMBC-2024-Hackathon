import json
import os
from dotenv import load_dotenv
import logging
from typing import List

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
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from pydantic import BaseModel
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser, PydanticOutputParser

class QAPair(BaseModel):
    question:str
    answer: str
    type: str
    choices: List[str] = ['T', 'F']  # Holds Choices in a multiple Choice question
    


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.6,
    api_key=os.getenv("OPENAI_API_KEY"),
) 

def question_generate_chain(clean_response: str, llm, title, course, professor
                            number_of_mcq_questions, number_of_TF_questions, number_of_written_questions,
                            school_type, difficulty, testing_philosophy):
    question_generation_json_format = get_json_format()
    question_generation_system_prompt, question_generation_human_prompt = get_templates()
    system_prompt = SystemMessagePromptTemplate.from_template(question_generation_system_prompt.template)
    human_prompt = HumanMessagePromptTemplate.from_template(question_generation_human_prompt.template)
    prompt = ChatPromptTemplate.from_messages(
        [
            system_prompt,
            human_prompt,
        ]
    )
    chain = get_question_generate_chain(
        clean_response=clean_response,
        llm=llm,
        title=title,
        course=course,
        professor=professor,
        number_of_mcq_questions=number_of_mcq_questions,
        number_of_TF_questions=number_of_TF_questions,
        number_of_written_questions=number_of_written_questions,
        school_type=school_type,
        difficulty=difficulty,
        testing_philosophy=testing_philosophy,
        prompt=prompt,
        question_generation_json_format=question_generation_json_format
    )
    pydantic_return_object = chain.invoke(clean_response)
    return pydantic_return_object    
    
def get_question_generate_chain(*, clean_response: str, llm, title, course, professor
                            number_of_mcq_questions, number_of_TF_questions, number_of_written_questions,
                            school_type, difficulty, testing_philosophy, prompt,
                            question_generation_json_format
                            ):
    parser = PydanticOutputParser(pydantic_object=QAPair)
    chain = (
        RunnablePassthrough.assign(
            question_generation_system_prompt = lambda x: question_generation_system_prompt.format(
                QAPair_json_format=x["question_generation_json_format"],
                number_of_mcq_questions=x["number_of_mcq_questions"],
                number_of_TF_questions=x["number_of_TF_questions"],
                number_of_written_questions=x["number_of_written_questions"],
                type=x["type"],
                choices=x["choices"]
                difficulty=x["difficulty"],
                school_type=x["school_type"]
                testing_philosophy=x["testing_philosophy"]
                course=x["course"]
            ),
            question_generation_human_prompt = lambda x: question_generation_human_prompt.format(
                document=x["document"]
            )
        )
        | prompt
        | llm
        | parser
    )
    return chain

def get_templates():
    question_generation_system_prompt = PromptTemplate(
    template="""
    You are an AI assistant tasked with generating reading comprehension questions based on the given input document. Your goal is to help the user assess and deepen their understanding of the material in an educational context.
    
    You should utilize all educational content from the provided document, prioritizing the most emphasized and important concepts. 
    
    - Course Name: {course}
    
    Requested test settings:
    - The difficulty level: {difficulty}
    - The school level: {school_type}
    - Testing Philosophy: {testing_philosophy}
    
    You will be generating {number_of_mcq_questions} multiple choice questions, {number_of_TF_questions} true/false questions, and {number_of_written_questions} written questions.
    
    You are to provide your answer in the following format:
    {QAPair_json_format}
    If {type} is multiple choice, populate {choices} with three incorrect solution and one correct solution in a random order. If {type} is True/False, leave {choices} as T, F. If {type} is a written question, leave {choices} blank.
    
    If you include anything but the question, type, answer, and and choices within the json, you have failed.
    """
    )

    question_generation_human_prompt = PromptTemplate(
        template = """
        Document:
        {document}
    """
    )
    
    return question_generation_system_prompt, question_generation_human_prompt

def get_json_format():
    QAPair_json_format = """
    {
        questions: [
            {
                "question": <string: a question>
                "type": <question type, i.e., multiple choice, written, true/false,
                "answer": <string: the answer to the question>
                "choices": <choices: if true false ['T', 'F'], if multiple choice then ['a', 'b', 'c', etc.,]>
                ]
            }
        ] 
    }
    """
    return QAPair_json_format


    