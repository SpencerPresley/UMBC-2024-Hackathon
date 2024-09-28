from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, \
    UnstructuredPowerPointLoader, WebBaseLoader
from PIL import Image
import pytesseract
import re
import os
import json
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs.log',
    filemode='w'
)

file_name = "Example2.txt"
current_directory = os.path.dirname(os.path.abspath(__file__))
doc_file_path = os.path.join(current_directory, "files", file_name)
logging.info(f'File: {file_name} loaded at path: {doc_file_path}')

if doc_file_path.endswith('.pdf'):
    loader = PyPDFLoader(
        file_path=doc_file_path,
        extract_images=True,
    )
    logging.info("Loader set for type .PDF")
    
    
elif doc_file_path.endswith('.docx'):
    loader = Docx2txtLoader(
        file_path = doc_file_path
    )
    logging.info("Loader set for type .docx")
elif doc_file_path.endswith('.txt'):
    loader = TextLoader(
        file_path = doc_file_path
    )
    logging.info("Loader set for type .txt")

elif doc_file_path.endswith('.pptx'):
    loader = UnstructuredPowerPointLoader(
        file_path=doc_file_path
    )
    logging.info("Loader set for type .pptx")

elif doc_file_path.endswith('.png', '.jpeg', '.jpg'):
    img = Image.open(doc_file_path).convert("L")  # Open and convert image to grayscale
    text = pytesseract.image_to_string(img, lang="eng")  # Convert image to text
    logging.info("Loader set for type .png, .jpeg, or .jpg")

    
    
else:
    pass  # Indicate invalid filetype


docs = []
docs_lazy = loader.load_and_split()
logging.info("Docs loaded using .load_and_split()")
# for doc in docs_lazy:
#     print(doc)
#     input("Press Enter to continue...")
#     # docs.append(doc.page_content)


dict_data = {}
doc_str = "".join([doc.page_content for doc in docs_lazy])
logging.info("Docs joined together in one string")
dict_data["data"] = doc_str
logging.info("Doc string inserted into dictionary.")
with open("data.json", "w") as f:
    json.dump(dict_data, f, indent=4)
    logging.info("Dictionary dumped to json: {f}")

pages = []
metadata = []

for doc in docs_lazy:
    pages.append(re.sub(r'\s+', ' ', doc.page_content).strip())  # Clean data output
    metadata.append(doc.metadata)
logging.info(f"Pages, and metadata added.")
logging.info(f"Pages: {pages}")
logging.info(f"Metadata: {metadata}")
content_dict = {}
content_dict["content"] = pages
content_dict["metadata"] = metadata
logging.info("Pages and metadata inserted into dictionary.")
with open("content.json", "w") as f:
    json.dump(content_dict, f, indent=4)
    logging.info("Content dictionary dumped to json file: {f}")

def load_website(link):
    loader = WebBaseLoader(
        web_path=link
    )
    logging.info("WebBaseLoader initiated with web_path: {link}")
    