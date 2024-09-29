import json
import os
from dotenv import load_dotenv
import logging
import tempfile

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


class CleanedFile(BaseModel):
    cleaned_content: str

load_dotenv()
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.6,
    api_key=os.getenv("OPENAI_API_KEY"),
)

parser = JsonOutputParser(pydantic_object=CleanedFile)

def run(formData, file_path: str = None, key: str = None):
    from ..server import FormSettings, GeneratedTest
    
    # Access form data fields
    try:
        title = formData.title
        course = formData.course
        professor = formData.professor
        number_of_mcq_questions = formData.number_of_mcq_questions
        number_of_TF_questions = formData.number_of_TF_questions
        number_of_written_questions = formData.number_of_written_questions
        school_type = formData.school_type
        difficulty = formData.difficulty
        testing_philosophy = formData.testing_philosophy
    except Exception as e:
        logging.error(f"Error accessing form data: {e}")
        return
    
    logging.info("Form data accessed")
    logging.info(f"Form Title: {title}")
    logging.info(f"Form Course: {course}")
    logging.info(f"Form Professor: {professor}")
    logging.info(f"Form Number of MCQ Questions: {number_of_mcq_questions}")
    logging.info(f"Form Number of TF Questions: {number_of_TF_questions}")
    logging.info(f"Form Number of Written Questions: {number_of_written_questions}")
    logging.info(f"Form School Type: {school_type}")
    logging.info(f"Form Difficulty: {difficulty}")
    logging.info(f"Form Testing Philosophy: {testing_philosophy}")
    logging.info("Moving to files...")
    try:    
        for uploaded_file in formData.subject_material:
<<<<<<< Updated upstream
            logging.info(f"Processing file: {uploaded_file.filename}")
            loader = get_loader(uploaded_file)
            docs = loader.load()
=======
            logging.info(f"File name: {uploaded_file.filename}")
            loader = get_loader(uploaded_file.filename)
            docs = load_data(loader)
>>>>>>> Stashed changes
            full_response = ""
            for i, doc in enumerate(docs):
                logging.info(f"Document {i+1} ({uploaded_file.filename}) of {len(docs)}")
                full_response += clean_files_chain(doc)
            write_response_to_file(full_response, "cleaned_content.json")
            logging.info("Cleaned content written to file")
    except Exception as e:
        logging.error(f"Error processing file: {uploaded_file.filename}")
        logging.error(f"Error loading data: {e}")
        return
    
def load_data(loader):
    raw_docs = loader.load_and_split()
    logging.info("Docs loaded using .load_and_split()")
    docs = [doc.page_content for doc in raw_docs]
    return docs

def clean_files_chain(doc: str, key: str = None):
    print(f"Document: {doc}")
    # print(f"Key: {key}")
    system_prompt, human_prompt = get_clean_files_prompts()
    prompt = ChatPromptTemplate.from_messages(
        [
            system_prompt,
            human_prompt,
        ]
    )
    chain = get_clean_files_chain(llm, prompt, system_prompt, human_prompt)
    response = chain.invoke({
        "document": doc,
        "clean_files_json_format": clean_files_json_format
    })
    return response["cleaned_content"]

def get_clean_files_prompts():
    system_prompt = SystemMessagePromptTemplate.from_template(
        clean_files_system_prompt.template
    )
    human_prompt = HumanMessagePromptTemplate.from_template(
        clean_files_human_prompt.template
    )

    return system_prompt, human_prompt

def get_file_data(file_path: str):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def get_clean_files_chain(llm, prompt, system_prompt, human_prompt):
    chain = (
        RunnablePassthrough.assign(
            system_prompt = lambda x: system_prompt.format(clean_files_json_format=x["clean_files_json_format"]),
            human_prompt = lambda x: human_prompt.format(document=x["document"])
        ) 
        | prompt 
        | llm 
        | parser
    )
    return chain

def write_response_to_file(response, file_path: str):
    with open(file_path, "w") as f:
        json.dump(response, f, indent=4)
        


def get_loader(uploaded_file):  
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(uploaded_file.file.read())
    file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
    logging.info(f"File extension: {file_extension}")
    if file_extension == '.pdf':
        logging.info(f"Processing PDF file: {uploaded_file.filename}")
        return PyPDFLoader(file_path=temp_file_path, extract_images=True)
    elif file_extension == '.txt':
        logging.info(f"Processing TXT file: {uploaded_file.filename}")
        return TextLoader(temp_file_path)
    elif file_extension in ['.docx', '.doc']:
        logging.info(f"Processing DOCX/DOC file: {uploaded_file.filename}")
        return Docx2txtLoader(temp_file_path)
    elif file_extension == '.pptx':
        logging.info(f"Processing PPTX file: {uploaded_file.filename}")
        return UnstructuredPowerPointLoader(temp_file_path)
    elif file_extension in ['.png', '.jpeg', '.jpg']:
        logging.info(f"Processing image file: {uploaded_file.filename}")
        img = Image.open(temp_file_path).convert("L")
        text = pytesseract.image_to_string(img, lang="eng")
        logging.info(f"Loader set for type .{file_extension}")
        logging.info(f"Text: {text}")
        return TextLoader(text.encode())
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
        
        
if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    pdf_file_path = os.path.join(current_directory, "files", "ExampleFileForDev.pdf")
    run(pdf_file_path, "content")
    