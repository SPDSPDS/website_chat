# server.py

import os

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import (WebBaseLoader, UnstructuredURLLoader)
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

from langchain.docstore.document import Document
from unstructured.cleaners.core import remove_punctuation,clean,clean_extra_whitespace
from langchain import OpenAI
from langchain.chains.summarize import load_summarize_chain

import http.server
import json

global_url = ''

def getSummary(url):
    print("Getting summary...")
    # Given an URL, create a langchain Document to further processing
    loader = UnstructuredURLLoader(urls=[url],
        mode="elements",
        post_processors=[clean,remove_punctuation,clean_extra_whitespace])
    elements = loader.load()
    selected_elements = [e for e in elements if e.metadata['category']=="NarrativeText"]
    print(selected_elements)
    full_clean = " ".join([e.page_content for e in selected_elements])
    tmp_doc = Document(page_content=full_clean, metadata={"source":url})

    # Loading environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Given an URL return the summary from OpenAI model
    # Use a ChatOpenAI model
    llm = ChatOpenAI(model_name='gpt-3.5-turbo')
    chain = load_summarize_chain(llm, chain_type="stuff")
    summary = chain.run([tmp_doc])
    return {'result': clean_extra_whitespace(summary)} 

def getResponse(url, prompt):
    
    global global_url
    global vectordb

    # Loading environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if url != global_url:
        global_url = url

        # Cleaning the vectordb
        for collection in vectordb._client.list_collections():
            ids = collection.get()['ids']
            print(1, ids)
            # print('REMOVE %s document(s) from %s collection' % (str(len(ids)), collection.name))
            if len(ids): collection.delete(ids)
            vectordb.persist()

        vectordb.delete_collection()
        vectordb.persist()

        # Load data from the specified URL
        loader = WebBaseLoader(url)
        data = loader.load()

        # Split the loaded data
        text_splitter = CharacterTextSplitter(separator='\n', 
                                        chunk_size=500, 
                                        chunk_overlap=40)
        docs = text_splitter.split_documents(data)

        # Create OpenAI embeddings
        openai_embeddings = OpenAIEmbeddings()

        # Create a Chroma vector database from the documents
        vectordb = Chroma.from_documents(documents=docs, 
                                        embedding=openai_embeddings,
                                        persist_directory=DB_DIR)

        # Persist such database optionally
        vectordb.persist()

    # Create a retriever from the Chroma vector database
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    # Use a ChatOpenAI model
    llm = ChatOpenAI(model_name='gpt-3.5-turbo')

    # Create a RetrievalQA from the model and retriever
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    # Run the prompt and return the response
    response = qa(prompt)

    return response

class MyRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Read the incoming POST data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        # Process the data (you can customize this part)
        post_data = json.loads(post_data)

        url = post_data['url']
        prompt = post_data['prompt']
        
        print(url)
        print(prompt)
        print(post_data)

        if str.lower(prompt) == "summarize":
            response_data = getSummary(url)
        else:
            response_data = getResponse(url, prompt)
        print(response_data)

        # Send the response as JSON
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', 8000)  # Change the port if needed
    httpd = http.server.HTTPServer(server_address, MyRequestHandler)
    print(f'Starting server on port {server_address[1]}...')

    ABS_PATH: str = os.path.dirname(os.path.abspath(__file__))
    DB_DIR: str = os.path.join(ABS_PATH, "dbChroma")
    global vectordb
    vectordb = Chroma(persist_directory=DB_DIR)
    httpd.serve_forever()

