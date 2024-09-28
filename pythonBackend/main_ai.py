from langchain_community.document_loaders import PyPDFLoader
import os
import json

current_directory = os.path.dirname(os.path.abspath(__file__))
pdf_file_path = os.path.join(current_directory, 'files', 'Example2.pdf')

loader = PyPDFLoader (
    file_path = pdf_file_path,
    extract_images=True
)

docs = []
docs_lazy = loader.lazy_load()
for doc in docs_lazy:
    docs.append(doc)

print(docs)
    
content_string = ''

for doc in docs:
    content_string += doc.page_content
    print(doc.page_content)
    
print(content_string)  
    
content_dict = {}
content_dict['content'] = content_string
with open('content.json', 'w') as f:
    json.dump(content_string, f, indent=4)

    