from langchain_community.document_loaders import PyMuPDFLoader
from langchain_chroma import Chroma
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os
import re
from dotenv import load_dotenv

load_dotenv()

class RAGSystem:
    def __init__(self):
        self.file_path = None
        self.filename = None
        self.msg_hist = []
        self.emb_func = HuggingFaceEndpointEmbeddings(repo_id= "BAAI/bge-small-en-v1.5")
        self.llm = ChatGroq(model = "openai/gpt-oss-120b")
        self.vec_store = None



    def create_vec_store(self):
        self.file_path = os.path.join("/home/rabboni/Desktop/talk_with_pdf/data/files", os.listdir("/home/rabboni/Desktop/talk_with_pdf/data/files")[0])
        #cleaning file name for vector store
        self.filename = re.sub(r"[^a-zA-Z0-9]", "", os.listdir("/home/rabboni/Desktop/talk_with_pdf/data/files")[0])
        
        self.vec_store = Chroma(
            embedding_function = self.emb_func ,
            collection_name= self.filename,
            persist_directory = "/home/rabboni/Desktop/talk_with_pdf/data/vectorstore"
        )

        splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
        loader = PyMuPDFLoader(self.file_path)
        docs = loader.lazy_load()
        for doc in docs:
            chunks = splitter.split_documents([doc])
            self.vec_store.add_documents(chunks)
        os.remove(self.file_path)


    def __docs_prcx(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)
    

    def retrive(self, quary : str):


        retriver = self.vec_store.as_retriever(search_kwargs = {"k" : 2})

        parser = StrOutputParser()

        prompt = ChatPromptTemplate([
            ("system", """you are an pdf reader u will take message history, question and context from userand answer it,if question is a general purpose answer it from your knowledge or if its is releated to subject and u dont know answer reject polietly, and also at last provide details from where u got this info"""),
            ("placeholder", "{msg_hist}"),
            ("human", "Question : {question} \n Context : {context}")
        ], input_varaibles = ["msg_hist", "question", "context"])


        parllel_chain = RunnableParallel({
            "msg_hist" : lambda x : x["msg_hist"],
            "question" : lambda x : x["question"],
            "context" :lambda x : self.__docs_prcx(retriver.invoke(x["question"]))
        })

        chain = parllel_chain | prompt | self.llm | parser

        responce = chain.invoke({"question" : quary, "msg_hist" : self.msg_hist})


        if len(self.msg_hist) >= 10:
            self.msg_hist = self.msg_hist[2:]
            self.msg_hist.extend([HumanMessage(quary), AIMessage(responce)])
            return responce
        else:
            self.msg_hist.extend([HumanMessage(quary), AIMessage(responce)])
            return responce

if __name__ == "__main__":
    print(os.listdir("/home/rabboni/Desktop/talk_with_pdf/data/vectorstore"))
