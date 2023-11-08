from typing import Union

from fastapi import FastAPI,Request,File, UploadFile,Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import speech_recognition as sr 
from pydub import AudioSegment
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.llms import Cohere
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import RetrievalQA
from langchain.vectorstores import Pinecone,Qdrant
import os
import io
import pinecone
from typing import Union


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.environ["COHERE_API_KEY"] = "P5qlLVKqvPGIixGiGVmrKe1yXEQIbrcFoNMJn5ax"

pinecone.init(      
	api_key='6520df82-5caa-4e7c-bccd-74fd82583533',      
	environment='gcp-starter'      
) 

# initialize embeddings 
embeddings = CohereEmbeddings(model = "multilingual-22-12")

index_name = 'dbase'

docsearch = Pinecone.from_existing_index(index_name, embeddings)

r = sr.Recognizer()


@app.get("/")
def read_root():
    return {"Hello": "World"}


""" @app.post("/data")
async def get_data(request: Request):
    # Retrieve data from the frontend
    data = await  request.json()
    
    # Process the data or perform any desired operations
    print(data)
    rd = "recieved"
    # Return a response
    return rd """

#Voice
@app.post("/upload-voice")
async def upload_image(data: UploadFile = File(...)):

    return {"results": "hello"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    sound = file
    mf = io.BytesIO(file)
    print(type(mf))
    #audio = AudioSegment.from_file(mf)
    #audio = AudioSegment.from_bytes()
    return {"file_size": len(file)}


""" @app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    print(type(file))
    #myfile = file.read()
    #audio = AudioSegment.from_file(file)
    return {"filename": file.filename}
 """

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    print(type(file))
    myfile = await file.read()
    
    #contents = base64.b64decode(myfile) 
    #print(contents)
    """ with open(myfile, 'rb') as f:
        contents = f.read()
    audio = AudioSegment.from_file(contents) """
    audio_segment = AudioSegment.from_file(io.BytesIO(myfile), format="m4a")
    output_filename = "output.wav"
    audio_segment.export(output_filename, format="wav")
    # open the file
    with sr.AudioFile(output_filename) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
        print(text)
    #myfile = file.read()
    #audio = AudioSegment.from_file(contents)
    #return {"filename": file.filename}
    return text



# make our prompt 
prompt_template = """
Act as a chatbot.

generate response to the question based on the text provided.

If the text doesn't contain the answer, reply that the answer is not available and can request for more assistance by contacting us by telephone or sending a mail to customer service representative.

the Telephone Numbers:Tel: (+233) 302 611 560 Toll free: 0800 124 000 and the mail is gh.customersupport@gtbank.com

Text: {context}

Question: {question}
"""


PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chain_type_kwargs = {"prompt": PROMPT}


# This function takes the prompt as a parameter and returns the answer based on our documents on our vector storage
def question_and_answer(question):
    qa = RetrievalQA.from_chain_type(llm=Cohere(model="command-nightly", temperature=0), 
                                 chain_type="stuff", 
                                 retriever = docsearch.as_retriever(search_type="mmr"), 
                                 chain_type_kwargs=chain_type_kwargs, 
                                 return_source_documents=True)
                                 

    answer = qa({"query": question})
   
    return answer['result']

#print(question_and_answer("Hi"))


@app.post("/data")
async def get_data(request: Request):
    # Retrieve data from the frontend
    data = await request.json()
    
    # Process the data or perform any desired operations
    print(data['body'])
    rd = "recieved"
    # Return a response
    return rd

@app.post("/chat")
async def get_data(request: Request):
    # Retrieve data from the frontend
    data = await request.json()
    chatMsg= data['body']
    print(chatMsg)
    qa = RetrievalQA.from_chain_type(llm=Cohere(model="command-nightly", temperature=0), 
                                 chain_type="stuff", 
                                 retriever=docsearch.as_retriever(search_type="mmr"), 
                                 chain_type_kwargs=chain_type_kwargs, 
                                 return_source_documents=True)
                                 

    answer = qa({"query": chatMsg})

    #return answer['result']
    # Process the data or perform any desired operations
    #print(data['body'])
    rd = "recieved"
    # Return a response
    return answer['result']