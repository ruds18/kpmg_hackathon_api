import os
from flask import Flask
from flask_cors import CORS
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain import HuggingFaceHub

app = Flask(__name__)
CORS(app)

def get_token():
    # Ensure you have a HuggingFace Hub API token
    try:
        return "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"
    except KeyError:
        print("Error: Please set a `HUGGINGFACEHUB_API_TOKEN` environment variable.")
        return


def get_text(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def get_base():
    pdf_path = "./Previous Draft_Form 10-Q.pdf"

    if not os.path.exists(pdf_path):
        print("Error: PDF file not found. Please check the path and try again.")
        return

    text = get_text(pdf_path)

    # Split text into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Create embeddings
    embeddings = HuggingFaceEmbeddings()

    knowledge_base = FAISS.from_texts(chunks, embeddings)

    return knowledge_base


def run_bot(user_prompt):
        user_question = user_prompt
        # if user_question.lower() == "quit":
          

        # if not user_question:
        #     print("Please enter a question or type 'quit' to exit.")
            

        docs = knowledge_base.similarity_search(user_question)
        llm = HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature": 5, "max_length": 64},
                             huggingfacehub_api_token=get_token())
        chain = load_qa_chain(llm, chain_type="stuff")
        response = chain.run(input_documents=docs, question=user_question)
        return response

knowledge_base = get_base()



@app.route('/api/ml')
def predict():
     user_prompt = "What is the par value per share of Convertible preferred stock?"
     output =  run_bot(user_prompt)
     return {"output":output}