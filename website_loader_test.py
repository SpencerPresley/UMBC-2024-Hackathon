from langchain_community.document_loaders import WebBaseLoader, OnlinePDFLoader
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
import json
load_dotenv()

# OCR_AGENT = os.getenv("OCR_AGENT")
os.environ["OCR_AGENT"] = "tesseract"
os.environ['USER_AGENT'] = "LangChainScript/1.0 (Python/3.9; Research)"
loader = OnlinePDFLoader(
    'http://faculty.salisbury.edu/~sxpark/cosc450_1.pdf',
)

docs = loader.load_and_split()
# for i, doc in enumerate(docs):
#     print(f"Page {i+1}:")
#     print(f"Metadata:\n{doc.metadata}\n\n")
#     print(f"Page Content:\n{doc.page_content}\n\n")
    
doc_str = ''.join([doc.page_content for doc in docs]).replace("\n", "")
with open('ScrapeExample.txt', 'w') as f:
    f.write(doc_str)
    
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

class ParserStyle(BaseModel):
    title: str
    content: str
    
    
json_template = """
{
    "title": str,
    "content": str
}
"""
hm_template = PromptTemplate(template="""
                                ## Scraped PDF Content:\n{doc_str}
                                """)
sm_template = PromptTemplate(template="""
                                "You are an AI assistant tasked with restructuring the contents of a PDF which has been scraped from a website. The current structure results in unclear slide partitions. Your job is to restructure the content into clear and organized sections, each corresponding to a separate slide. The output should be a well-structured string where each slide is delineated by a clear marker, such as '--- SLIDE BREAK ---'. This will help in organizing the content for better readability and usability. Your output should be a JSON object with the following structure: {json_template}. IMPORTANT: Always return your output in the JSON format specified. IMPORTANT: If you do not return your output in the specified json, you have failed."
                                """
                            )

system_message = SystemMessagePromptTemplate.from_template(sm_template.template)
human_message = HumanMessagePromptTemplate.from_template(hm_template.template)
parser = JsonOutputParser(pydantic_object=ParserStyle)
messages = [
    system_message,
    human_message,
]

prompt = ChatPromptTemplate.from_messages(messages)

chain = RunnablePassthrough.assign(hm_template = lambda x: hm_template.format(doc_str=x["doc_str"]), sm_template = lambda x: sm_template.format(json_template=x["json_template"])) | prompt | llm | parser
chain_result = chain.invoke({
    "doc_str": doc_str,
    "json_template": json_template
})
with open('ScrapeExample.json', 'w') as f:
    json.dump(chain_result, f, indent=4)