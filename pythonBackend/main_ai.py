from langchain_community.document_loaders import PyPDFLoader
import os
import json

current_directory = os.path.dirname(os.path.abspath(__file__))
pdf_file_path = os.path.join(current_directory, "files", "ExampleFileForDev.pdf")

loader = PyPDFLoader(
    file_path=pdf_file_path,
    extract_images=True,
)

docs = []
docs_lazy = loader.load_and_split()
# for doc in docs_lazy:
#     print(doc)
#     input("Press Enter to continue...")
#     # docs.append(doc.page_content)


dict_data = {}
doc_str = "".join([doc.page_content for doc in docs_lazy])
dict_data["data"] = doc_str
with open("data.json", "w") as f:
    json.dump(dict_data, f, indent=4)

pages = []
metadata = []

for doc in docs_lazy:
    pages.append(doc.page_content)
    metadata.append(doc.metadata)

# print(pages)

content_dict = {}
content_dict["content"] = pages
content_dict["metadata"] = metadata
with open("content.json", "w") as f:
    json.dump(content_dict, f, indent=4)
