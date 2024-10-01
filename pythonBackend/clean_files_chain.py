import json
import os
from dotenv import load_dotenv
import logging
import tempfile
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image
import pytesseract
import asyncio
import aiofiles
import atexit
import glob
os.environ["OCR_AGENT"] = "tesseract"
os.environ['USER_AGENT'] = "LangChainScript/1.0 (Python/3.9; Research)"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='chains.log',
    filemode='w'
)

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredPowerPointLoader, PyMuPDFLoader, UnstructuredURLLoader, WebBaseLoader


from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from pydantic import BaseModel
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from .custom_prompts import clean_files_system_prompt, clean_files_human_prompt, clean_files_json_format

from .question_generation_prompt import question_generate_chain, judge_chain

from langchain_community.document_loaders import OnlinePDFLoader

class ParserStyle(BaseModel):
    title: str
    content: str

class CleanedFile(BaseModel):
    cleaned_content: str

load_dotenv()
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)

parser = JsonOutputParser(pydantic_object=CleanedFile)

online_pdf_loader_dict: dict[str, bool] = {}

async def run(formData, file_path: str = None, key: str = None):
    logging.info("Starting run function")
    # from ..server import FormSettings, GeneratedTest
    # for spencer
    from server import FormSettings, GeneratedTest
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
        url_1 = formData.url_1 if formData.url_1 else None
        url_2 = formData.url_2 if formData.url_2 else None
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
        logging.info("Starting to process files")


        tasks = []
        for uploaded_file in formData.subject_material:
            logging.info(f"Processing file: {uploaded_file.filename}")
            loader = await get_loader(uploaded_file=uploaded_file)
            tasks.append(process_file(loader=loader, filename=uploaded_file.filename))
        
        urls = [url for url in [url_1, url_2] if url is not None]
        logging.info(f"URLs: {urls}")
        logging.info(f"Processing {len(formData.subject_material)} files and {len(urls)} URLs")
        for url in urls:
            logging.info(f"Processing URL: {url}")
            loader = await get_loader(uploaded_file=url, url_bool=True)
            tasks.append(process_file(loader=loader, filename=url))
             
        try:
            results = await asyncio.gather(*tasks)
        except Exception as e:
            logging.error(f"Error processing tasks: {str(e)}")
            return None        

        pages = []
        full_response = ""
        for result in results: 
            if type(result) == list:
                pages.append(result)
            else:
                full_response += result
                
        logging.info(f"Pages: {pages}")
        logging.info(f"Full response: {full_response}")
        pydantic_test = None
        test_kwargs = {
            "llm": llm,
            "title": title,
            "course": course,
            "professor": professor,
            "number_of_mcq_questions": number_of_mcq_questions,
            "number_of_TF_questions": number_of_TF_questions,
            "number_of_written_questions": number_of_written_questions,
            "school_type": school_type,
            "difficulty": difficulty,
            "testing_philosophy": testing_philosophy,
        }

        test_list = await process_pages(pages=pages, full_response=full_response, **test_kwargs)
        logging.info(f"Generated test list with {len(test_list)} tests")
        judge_kwargs = {
            "course": course,
            "professor": professor,
            "number_of_mcq_questions": number_of_mcq_questions,
            "number_of_TF_questions": number_of_TF_questions,
            "number_of_written_questions": number_of_written_questions,
            "school_type": school_type,
            "difficulty": difficulty,
            "testing_philosophy": testing_philosophy,
            "raw_tests_objects": test_list
        }
        logging.info(f"Preparing judge_kwargs with {len(judge_kwargs)} parameters")

        test_str = ""
            
        if len(online_pdf_loader_dict.keys()) > 0 and len(test_list) > 1:
            test_str = "FIRST TEST\n\n" + "".join(f"{json.dumps(test.model_dump(), indent=4)}\n\nNEXT TEST\n\n" for test in test_list) + "END OF TESTS"
            logging.info(f"All Tests: {test_str}")
            result = await judge_chain(test_str=test_str, **judge_kwargs)
            pydantic_test = result
        elif len(online_pdf_loader_dict.keys()) > 0 and len(test_list) == 1:
            test_str = json.dumps(test_list[0].model_dump(), indent=4)
            result = await judge_chain(test_str=test_str, **judge_kwargs)
            pydantic_test = result
        else:
            pydantic_test = test_list[0]

        logging.info(f"FINAL TEST:\n{json.dumps(pydantic_test.model_dump(), indent=4)}")
        logging.info(f"All tasks completed. Number of results: {len(results)}")
        logging.info(f"Generated {len(test_list)} tests")
        return pydantic_test
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        for i, uploaded_file in enumerate(formData.subject_material):
            logging.error(f"File {i+1}: {uploaded_file.filename}")
        return None
    
    finally:
        logging.info("Cleaning up temp files")
        cleanup_temp_files()
        logging.info("Temp files cleaned")
        logging.info("Run function completed")

async def process_pages(pages = None, full_response = None, **kwargs):
    logging.info(f"Processing pages: {len(pages) if pages else 0}, full_response: {'Yes' if full_response else 'No'}")
    tasks = []
    if pages is not None:
        for page in pages:
            tasks.append(question_generate_chain(
                clean_response=page, **kwargs
            ))
    if full_response is not None:
        tasks.append(question_generate_chain(
            clean_response=full_response, **kwargs
        ))
    logging.info(f"Created {len(tasks)} tasks for question generation")
    results = await asyncio.gather(*tasks)
    logging.info(f"Completed question generation. Number of results: {len(results)}")
    return results

async def process_file(*, loader, filename):
    logging.info(f"Processing {filename}")
    logging.info(f"Using loader type: {type(loader).__name__} for {filename}")
    if online_pdf_loader_dict.get(filename, False):
        logging.info(f"Processing {filename} as an online PDF using {type(loader).__name__}")
        pages = await loader.aload()
        logging.info(f"Successfully loaded {filename} as an online PDF")
        logging.info(f"Loaded {len(pages)} pages from {filename}")
        logging.info(f"Pages: {pages}")
        return pages
    
    logging.info(f"Processing {filename} as a regular document using {type(loader).__name__}")
    docs = None
    if isinstance(loader, WebBaseLoader):
        docs = await asyncio.to_thread(loader.load)  # Run synchronous load method in a separate thread
    else:
        docs = await loader.aload()
    
    logging.info(f"Successfully loaded {len(docs)} documents from: {filename}")
    logging.info(f"Docs: {docs} for {filename} using {type(loader).__name__}")
    full_response = ""
    for i, doc in enumerate(docs):
        logging.info(f"Document {i+1} ({filename}) of {len(docs)}")
        full_response += await clean_files_chain(doc=doc)
        logging.info(f"Successfully cleaned document {i+1} from {filename}")

    return full_response


async def clean_files_chain(*, doc: str, key: str = None):
    logging.info("Starting clean_files_chain")
    logging.info(f"Document: {doc}")
    # print(f"Key: {key}")
    system_prompt, human_prompt = get_clean_files_prompts()
    prompt = ChatPromptTemplate.from_messages(
        [
            system_prompt,
            human_prompt,
        ]
    )
    chain = get_clean_files_chain(
        llm=llm, 
        prompt=prompt, 
        system_prompt=system_prompt, 
        human_prompt=human_prompt
    )
    logging.info("Invoking chain")
    response = await chain.ainvoke({
        "document": doc,
        "clean_files_json_format": clean_files_json_format
    })
    logging.info(f"Response: {response}")
    logging.info("Finished clean_files_chain")
    return response["cleaned_content"]

def get_clean_files_prompts():
    system_prompt = SystemMessagePromptTemplate.from_template(
        clean_files_system_prompt.template
    )
    human_prompt = HumanMessagePromptTemplate.from_template(
        clean_files_human_prompt.template
    )

    return system_prompt, human_prompt

def get_clean_files_chain(*, llm, prompt, system_prompt, human_prompt):
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

async def write_response_to_file(*, response, file_path: str):
    async with aiofiles.open(file_path, "w") as f:
        await f.write(json.dumps(response, indent=4))

async def get_loader(*, uploaded_file, url_bool=False):
    logging.info(f"Getting loader for {'URL' if url_bool else 'file'}: {uploaded_file}")
    loader_log_message = f"Getting loader for {'URL' if url_bool else 'file'}: {uploaded_file}"
    loader_type_log_message = f"Using loader type: "
    loader_type_log_message_suffix = f" for {uploaded_file}"
    if url_bool:
        if uploaded_file.startswith('http') and not uploaded_file.endswith('.pdf'):
            online_pdf_loader_dict[uploaded_file] = False
            loader = WebBaseLoader(web_paths=[uploaded_file])
            logging.info(f"{loader_type_log_message}{type(loader).__name__}{loader_type_log_message_suffix}")
            return loader
        elif uploaded_file.startswith('http') and uploaded_file.endswith('.pdf'):
            online_pdf_loader_dict[uploaded_file] = True
            loader = OnlinePDFLoader(
                uploaded_file,
            )
            logging.info(f"{loader_type_log_message}{type(loader).__name__}{loader_type_log_message_suffix}")
            return loader

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    temp_file.close()  # Close the file so aiofiles can open it
    
    async with aiofiles.open(temp_file_path, 'wb') as f:
        content = await uploaded_file.read()  # Read the file content asynchronously
        await f.write(content) 
        
    file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
    logging.info(f"File extension: {file_extension}")
    if file_extension == '.pdf':
        logging.info(f"Processing PDF file: {uploaded_file.filename}")
        loader = PyMuPDFLoader(temp_file_path)
        logging.info(f"{loader_type_log_message}{type(loader).__name__}{loader_type_log_message_suffix}")
        return loader
        #return PyPDFLoader(file_path=temp_file_path, extract_images=True)
    elif file_extension == '.txt':
        logging.info(f"Processing TXT file: {uploaded_file.filename}")
        loader = TextLoader(temp_file_path)
        logging.info(f"{loader_type_log_message}{type(loader).__name__}{loader_type_log_message_suffix}")
        return loader
    elif file_extension in ['.docx', '.doc']:
        logging.info(f"Processing DOCX/DOC file: {uploaded_file.filename}")
        loader = Docx2txtLoader(temp_file_path)
        logging.info(f"{loader_type_log_message}{type(loader).__name__}{loader_type_log_message_suffix}")
        return loader
    elif file_extension == '.pptx':
        logging.info(f"Processing PPTX file: {uploaded_file.filename}")
        loader = UnstructuredPowerPointLoader(temp_file_path)
        logging.info(f"{loader_type_log_message}{type(loader).__name__}{loader_type_log_message_suffix}")
        return loader
    elif file_extension in ['.png', '.jpeg', '.jpg']:
        logging.info(f"Processing image file: {uploaded_file.filename}")
        img = Image.open(temp_file_path).convert("L")
        text = pytesseract.image_to_string(img, lang="eng")
        logging.info(f"Loader set for type .{file_extension}")
        logging.info(f"Text: {text}")
        loader = TextLoader(text.encode())
        logging.info(f"{loader_type_log_message}{type(loader).__name__}{loader_type_log_message_suffix}")
        return loader
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
        
def cleanup_temp_files():
    temp_dir = tempfile.gettempdir()
    pattern = os.path.join(temp_dir, 'tmp*')
    for temp_file in glob.glob(pattern):
        try:
            os.remove(temp_file)
            logging.info(f"Deleted temp file: {temp_file}")
        except Exception as e:
            logging.error(f"Error deleting temp file: {temp_file} -> ERROR:{e}")

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    pdf_file_path = os.path.join(current_directory, "files", "ExampleFileForDev.pdf")
    asyncio.run(run(None, pdf_file_path))
    