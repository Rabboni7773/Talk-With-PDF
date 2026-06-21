from langchain_community.document_loaders import PyMuPDFLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.chat_history import InMemoryChatMessageHistory
import chromadb
import uuid
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()
store = {}
class RAGSystem:
    def __init__(self):
        self.file_path = None
        self.filename = None
        self.msg_hist = []
        self.emb_func = HuggingFaceEndpointEmbeddings(repo_id= "BAAI/bge-small-en-v1.5", huggingfacehub_api_token=os.getenv("HF_API"))
        self.llm = ChatGroq(model = "openai/gpt-oss-120b", api_key= os.getenv("GROQ_API_KEY"), max_tokens=2048)
        self.chroma_client = chromadb.PersistentClient(path = "./chroma_db")
        self.vec_store = Chroma(
            client= self.chroma_client,
            embedding_function = self.emb_func,
            collection_name = f"session_{uuid.uuid4()}"
        )



    def create_vec_store(self):

        storage_dir = "/app/file_storage"

        if not os.path.exists(storage_dir) or not os.listdir(storage_dir):
            print("No files found in storage directory.")
            return

        self.file_path = os.path.join(storage_dir, os.listdir(storage_dir)[0])
        self.filename = re.sub(r"[^a-zA-Z0-9]", "", os.listdir(storage_dir)[0])
        
        splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
        loader = PyMuPDFLoader(self.file_path)
        docs = loader.lazy_load()
        for doc in docs:
            chunks = splitter.split_documents([doc])
            self.vec_store.add_documents(chunks)

        if os.path.exists(self.file_path):
            os.remove(self.file_path)


    def __docs_prcx(self, docs):
        return "\n\n".join(doc.page_content + "\n" + json.dumps(doc.metadata) for doc in docs)
    
    def __get_chat_history(self, session_id : str):
        if session_id in store:
            return store[session_id]
        else:
            store[session_id] = InMemoryChatMessageHistory()
            return store[session_id]
    

    def retrive(self, quary : str, session_id : str):


        retriver = self.vec_store.as_retriever(search_kwargs = {"k" : 2})

        parser = StrOutputParser()

        prompt = ChatPromptTemplate([
            ("system", """you are an pdf reader u will take message history, question and context from userand answer it,if question is a general purpose answer it from your knowledge or if its is releated to subject and u dont know answer reject polietly, and also at last provide details from where u got this info and only provide info, dont provide source for general questions"""),
            MessagesPlaceholder("history"),
            ("human", "Question : {quary} \n Context : {context}")
        ])


        parllel_chain = RunnableParallel({
            "quary" : lambda x : x["quary"],
            "history" : lambda x : x["history"],
            "context" :lambda x : self.__docs_prcx(retriver.invoke(x["quary"]))
        })

        chain = parllel_chain | prompt | self.llm | parser

        main_chain = RunnableWithMessageHistory(
            chain,
            self.__get_chat_history,
            input_messages_key="quary",
            history_messages_key="history"
        )

        responce = main_chain.invoke({"quary" : quary}, config={"configurable" : {"session_id" : session_id}})
        return responce
