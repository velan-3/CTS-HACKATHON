import os
import re
import warnings
from langchain_huggingface  import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

warnings.filterwarnings("ignore")


class Model:
    
    def __init__(self):
        os.environ['HUGGINGFACEHUB_API_TOKEN'] = "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"
        #self.summarization()
        self.embedding  = None
        self.vectordbl = None
        #self.preprocesspdf()
        
    def pdfprocessing(self,pdf_filename):
        file_path = os.path.join('./upload', pdf_filename)
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        print("pdf loaded")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=300)
        texts = text_splitter.split_documents(documents)
        print("document splitted")
        #persist_directory = 'db'
        #global embedding
        self.embedding = HuggingFaceEmbeddings()
        print("Embedding done")
        self.vectordbl = Chroma.from_documents(documents=texts, embedding=self.embedding)
        print("storage done")
        #self.vectordbl.persist()
        print("DB storage done")
        
    def summarization(self):
        #global embedding
        #embeddings = HuggingFaceEmbeddings()
        print('Loading db')
        # persist_directory = 'db'
        # self.vectordbl = Chroma(persist_directory=persist_directory, 
        #             embedding_function=self.embedding)
        llm = HuggingFaceHub(repo_id='mistralai/Mistral-7B-Instruct-v0.2',model_kwargs={'temperature':0.1,'max_new_tokens':6000})
        global input
        input = "Provide a detailed analysis and summarization of complete Blood count, Liver tests, Kidney tests, Cholesterol tests from the report."

        prompt1 = ChatPromptTemplate.from_template("""
You are a medical professional analyzing a patient's medical lab report. Your task is to extract the provided test results and provide a concise analysis based on the provided context.

Provide the summarization in the following format:

1.Patient Details:
    - Patient Name, Age , Gender

2. Lab Test Details:
    - Test Name: Specify all the tests names here. 
    
3. Blood Test Results:
    - Cover all relevant blood test results details (e.g., Haemoglobin, PCV, MCV, MCH, MCHC, RDW, Platelets, Differential Leucocyte Count, NLR) each point should be on a new line.

4. Liver Function Test Results:
    - Cover all relevant liver function test results details (e.g., Total Bilirubin, Bilirubin Direct, Bilirubin Indirect, ALT, AST, Alkaline Phosphate) each point on a new line.

5. Kidney Function Test Results:
    - Cover all relevant kidney function test results details (e.g., Creatinine, Urea, Blood Urea Nitrogen, Calcium, Sodium, Potassium, Uric Acid, Chloride). Ensure each result is included and correctly interpreted. Each point should be on a new line.

6. Cholesterol Test Results:
    - Cover all relevant Cholesterol test results details (e.g., Total Cholesterol, Triglycerides, HDL, LDL).

7. Explanation:
    - Provide a brief summary of the test results and what they indicate about the patient's health (each point should be on a new line).

8. Recommendations:
    - Provide medical advice or next steps based on the test results (each point should be on a new line).

Context: {context}
Question: {input}

""")

        chain = create_stuff_documents_chain(llm=llm,prompt=prompt1)
        retriever = self.vectordbl.as_retriever()
        global retreival_chain
        retreival_chain = create_retrieval_chain(
            retriever,
            chain
        )
        return 'PDF process successfull'
    def run_retrieval(self):
        print("document retreiving")
        global input
        response = retreival_chain.invoke({
            "input": input,
        })
        text = dict(response)
        print(text)
        if self.vectordbl:
            self.vectordbl.delete_collection()
            self.vectordbl = None
        answer_pattern = re.compile(r'Answer:\s*(.*)', re.DOTALL)

        question_pattern = re.compile(r'Question.*?\.\s*(.*)', re.DOTALL)

        extracted_wordings = []
    
        for key, value in text.items():
            if isinstance(value, str):  
            
                match = answer_pattern.search(value)
                if match:
                    extracted_wordings.append(match.group(1))
                else:
                    match = question_pattern.search(value)
                    if match:
                        extracted_wordings.append(match.group(1))
        if extracted_wordings:
            return extracted_wordings[0]
        else:
            print("No answers or questions found.")
        
    def Extraction(self,query,context):
        print('Loading db')
        #persist_directory = 'db'
        print("Query")
        llm = HuggingFaceHub(repo_id='mistralai/Mistral-7B-Instruct-v0.2',model_kwargs={'temperature':0.1,'max_new_tokens':1000})
        input = query
        document = Document(page_content=context, metadata={})
        #self.embedding = HuggingFaceEmbeddings()
        #vectordb = Chroma(persist_directory=persist_directory, 
        #           embedding_function=self.embedding)
        prompt = ChatPromptTemplate.from_template("""
        You are a medical professional analyzing patient's medical lab reports which contains test details about complete blood count,liver tests,kidney tests and cholesterol test. Your task is to provide the answer for the user's query based on the provided context
        Context: {context}
        Question: {input}""")
        chain = create_stuff_documents_chain(llm=llm,prompt=prompt)
        #retriever = vectordb.as_retriever()
        # retreival_chain = create_retrieval_chain(
        #     retriever,
        #     chain
        # )
        response = chain.invoke({
            "input": input,
            "context": [document]
        })
        text = response
        print(text)
        answer_pattern = re.compile(r'Answer:\s*(.*)', re.DOTALL)
        extracted_wordings = []
        match = answer_pattern.search(text)
        if match:
            extracted_wordings.append(match.group(1))  

        if extracted_wordings:
            return extracted_wordings[0]
        else:
            print("No answers or questions found.")
            return 'Query processing is done'
