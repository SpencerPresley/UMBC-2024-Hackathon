import json
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader

from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from pydantic import BaseModel
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from custom_prompts import (
    clean_files_system_prompt,
    clean_files_human_prompt,
    clean_files_json_format,
)


class CleanedFile(BaseModel):
    cleaned_content: str


load_dotenv()
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.6,
    api_key=os.getenv("OPENAI_API_KEY"),
)

parser = JsonOutputParser(pydantic_object=CleanedFile)

def run(file_path: str, key: str):
    loader = PyPDFLoader(
        file_path=file_path,
        extract_images=True,
    )
    docs = load_data(loader)
    full_response = ""
    for i, doc in enumerate(docs):
        print(f"Document {i+1} of {len(docs)}")
        full_response += clean_files_chain(doc)
    write_response_to_file(full_response, "cleaned_content.json")
    
def load_data(loader):
    raw_docs = loader.load_and_split()
    print(raw_docs)
    input("Press Enter to continue 1...")
    docs = [doc.page_content for doc in raw_docs]
    input("Press Enter to continue 2...")
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
        
if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    pdf_file_path = os.path.join(current_directory, "files", "ExampleFileForDev.pdf")
    run(pdf_file_path, "content")