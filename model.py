import os
import re
from langchain_huggingface  import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter




class Model:
    
    def __init__(self):
        # Set the Hugging Face API key
        os.environ['HUGGINGFACEHUB_API_TOKEN'] = "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"
        self.summarization()
        #self.preprocesspdf()
        
    def pdfprocessing(self,pdf_filename):
        file_path = os.path.join('./upload', pdf_filename)
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        print("pdf loaded")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        print("document splitted")
        persist_directory = 'db3'
        embedding = HuggingFaceEmbeddings()
        print("Embedding done")
        vectordb = Chroma.from_documents(documents=texts, embedding=embedding,persist_directory=persist_directory)
        print("storage done")
        vectordb.persist()
        print("DB storage done")
        vectordb = None
        
    def summarization(self):
        embeddings = HuggingFaceEmbeddings()
        print('embedding done')
        persist_directory = 'db3'
        vectordb = Chroma(persist_directory=persist_directory, 
                    embedding_function=embeddings)
        llm = HuggingFaceHub(repo_id='mistralai/Mistral-7B-Instruct-v0.2',model_kwargs={'temperature':0.1,'max_new_tokens':5000})
        global input
        input = "Give the report analysis of blood tests (include Hemoglobin or Haemoglobin,PCV,MCV,MCH,MCHC,RDW,Platelets,Absolute Leucocyte), liver tests(including Total Bilirubin,Bilirubin Direct,Bilirubin Indirect,ALT,AST,Protein,Alkaline Phosphate,Protein,Albumin,Globulin,Ag Ratio) and kidney tests (including creatine,Urea,Blood urea nitrogen,calcium,sodium,potassium,uric acid,chloride ) in the provided format"
        
        
        prompt1 = ChatPromptTemplate.from_template(""" Answer the user's question as a doctor summarizing the report by using the context. Provide the answer in the following format:

Lab Test Details:
- Test Name: includes Blood test, Liver function test, Kidney function test
- Blood Test Results: include blood test results (each point should be on a new line)
- Liver and Kidney Test Results: include both liver function and kidney function tests, including bilirubin tests (each point should be on a new line)
- Cholesterol Test Results: include cholesterol test results (each point should be on a new line)
- Explanation: Summarize the test results shortly  and their implications for the patient's health(each point should be on a new line)
- Recommendations: Doctor's recommendations based on the test (each point should be on a new line)

Context: {context}
Question: {input}

""")
        chain = create_stuff_documents_chain(llm=llm,prompt=prompt1)
        retriever = vectordb.as_retriever()
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
        pattern = re.compile(r'Answer:\s*(.*)', re.DOTALL)
        extracted_wordings = []
        for key, value in text.items():
            if isinstance(value, str):  # Checking if value is a string
                match = pattern.search(value)
        if match:
            extracted_wordings.append(match.group(1))  # Use group(1) since there's only one group

        # Return or print the first extracted answer
        if extracted_wordings:
            return extracted_wordings[0]
        else:
            print("No answers found.")
        

