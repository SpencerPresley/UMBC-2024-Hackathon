from langchain_core.prompts import PromptTemplate

clean_files_json_format = """
{
    "cleaned_content": "The rewritten document"
}
"""
clean_files_system_prompt = PromptTemplate(
    template="""
    You are an AI assistant who will take in a document and rewrite it in a more readable format, you are to correct any formatting mistakes and write any mathematical functions or what appear to be diagrams in plain text.
    
    For context, the document is a piece of academic text used in a classroom setting. This cleaned document will be used to make a test and answer key later, but you are only to rewrite the document to make it more readable as some parts of the document may be formatted incorrectly or may have lost accuracy when scanned in. 
    
    You are to provide you answer in the following json format:
    {clean_files_json_format}
    
    IMPORTANT: You are to only output the json format, do not include any other text or comments. If you do not answer in the json format you have failed.
"""
)

clean_files_human_prompt = PromptTemplate(
    template="""
    Document:
    {document}
"""
)