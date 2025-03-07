import os

# ollama
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings

# vector store
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma

# rag
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from IPython.display import display, Markdown

def create_gen_vector_store(gen=3, embedding_model='granite-embedding'):
    
    gen_dir = 'gen_' + str(gen) + '/mechanics'

    # Initialize a DirectoryLoader to load documents from the gen member's directory.
    # The loader is configured to show progress and use multithreading for efficiency.
    loader = DirectoryLoader(
        gen_dir,  
        show_progress=True,
        use_multithreading=True)

    # Load the documents from the directory using the loader
    docs = loader.load()
    
    # Create a ChromaDB vector store from the loaded documents. The documents are embedded
    # using a predefined embedding function, and the resulting embeddings are persisted
    # in a directory named 'gen_vector_stores' with a unique subdirectory for the gen member.
   
    embedding_function = OllamaEmbeddings(model=embedding_model)
    
    Chroma.from_documents(
        docs,
        embedding_function,
        persist_directory=f"mechanics_vector_store/chromadb_gen{gen}_{embedding_model}"
        )


def load_gen_vector_store(gen:str,
                          embedding_model:str='granite-embedding'
                          ):
    # print(f'Using embedding model {platform} {embedding_model}')
    embedding_function = OllamaEmbeddings(model=embedding_model)
    
    # Load the ChromaDB vector store from the specified directory
    db_gen = Chroma(
        embedding_function=embedding_function,
        persist_directory=f"mechanics_vector_store/chromadb_gen{gen}_{embedding_model}"
        )
    
    return db_gen




class ChatRAG:
    def __init__(self,
                 gen, 
                 chat_model=None, 
                 embedding_model=None,
                 system_prompt_path='prompt.txt'):
        self._gen = gen
        self._chat_model = chat_model
        self._embedding_model = embedding_model
        self.setup_chat_prompt_template(system_prompt_path)
        self._chat_llm = self.initialize_chat_llm()
        self._conversational_rag = self.initialize_conversational_rag()


    def setup_chat_prompt_template(self, system_prompt_path):
        if system_prompt_path:
            with open(system_prompt_path, 'r') as f:
                system_prompt = f.read().format(context='{context}') # ugly hack to because you can only pass {context} and {question} as input_parameters to the template
        else:
            system_prompt = 'context:\n {context}.'

        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template('Question:```{question}```')
        ]
        self.chat_prompt_template = ChatPromptTemplate.from_messages(messages)

        

    def initialize_chat_llm(self):
        llm = OllamaLLM(model=self._chat_model)
        return llm
    
    def initialize_conversational_rag(self):

        gen_vector_store = load_gen_vector_store(self._gen, self._embedding_model)
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer')
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=self._chat_llm,
            retriever=gen_vector_store.as_retriever(search_kwargs={"k": 10}),
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={'prompt': self.chat_prompt_template}
        )
        return conversation_chain

    def chat(self, user_prompt, render=True, return_response=True):
        answer = self._conversational_rag.invoke(user_prompt)['answer']
        if render:
            display(Markdown(answer))
        
        if return_response:
            return answer
