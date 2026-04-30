from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List
from langchain.agents import create_agent
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA
from dotenv import load_dotenv

import streamlit as st
import time
import pymupdf
import re

# load env
load_dotenv()


# Text Pipeline (Opening, Extracting, Sectionwise chunking into dictionary)
doc = pymupdf.open("./article.pdf")

text = ""
filtered_matches = ["abstract\n"]
counter = 1

for page in doc:
    text += page.get_text().lower()

pattern = re.compile(r'\d\.\n(?:\w+(?:[-\s]\w+){0,4})\n')

matches = pattern.findall(text)

for match in matches:
    if match.startswith(f"{counter}.\n"):
        filtered_matches.append(match)
        counter += 1

sections = {}
for i in range(len(filtered_matches)):
    start = text.find(filtered_matches[i])
    end = text.find(filtered_matches[i + 1]) if i + \
        1 < len(filtered_matches) else len(text)

    section_name = re.sub(r'\s+', ' ', filtered_matches[i]).strip()

    section_content = re.sub(r'\s+', ' ', text[start:end]).strip()
    section_content = section_content.replace(section_name, '', 1).strip()

    sections[section_name] = section_content

# # prints key and values of the extracted text with number of character per section
# for key, value in sections.items():
#     print(f"Section: {key}\n")
#     print(f"Content: {len(value)} characters\n")

# print(len(sections))
# print(sections)

# Pydantic class


class Section(BaseModel):
    summary: str = Field(
        ..., description="A concise summary of the main ideas presented in the text.")
    key_points: List[str] = Field(
        ..., description="A list of the key points or takeaways from the text.")

# API Call


llama_instant = "llama-3.1-8b-instant"
llama_versatile = "llama-3.3-70b-versatile"
gpt_oss = "openai/gpt-oss-120b"
response_dict = {}


model = ChatGroq(model=gpt_oss)
agent = create_agent(model=model, response_format=Section)

for key, value in sections.items():
    response = agent.invoke({"messages": [{"role": "system", "content": "You are a helpful assistant that summarizes research articles and gives key points."}, {
                            "role": "user", "content": value}]})
    response_dict[key] = response
    print(f"Section: {key}\n")
    print(response["structured_response"])
    time.sleep(15) 

# RAG


# Document loading
file_path = "./article.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

# Text splitting
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  
    chunk_overlap=200,  
    add_start_index=True,  
)
all_splits = text_splitter.split_documents(docs)

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store = FAISS.from_documents(all_splits, embeddings)

# Generation
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.0)

# Retrieval
retriever = vector_store.as_retriever(
	 search_type="similarity",
	 search_kwargs={"k": 5}
	)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",)

#
query = "What is shap?"
response = qa_chain.invoke({"query": query})

print(response["result"])