from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from typing import List
import uuid
import os
import re

load_dotenv()

class VectorDatabaseService:
    def __init__(self):
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    def load_dataset(self, file_name: str) -> PdfReader:
        pdfreader = PdfReader(file_name)
        return pdfreader

    def read_data(self, loaded_file: PdfReader) -> str:
        raw_text = ''
        for page in loaded_file.pages:
            content = page.extract_text()
            if content:
                raw_text += content
    
        return raw_text

    def text_splitter(self, extracted_text: str) -> List[str]:
        print("Chunk Size: ", int(os.getenv("CHUNK_SIZE")))
        print("Chunk OVERLAP: ", int(os.getenv("CHUNK_OVERLAP")))
        
        text_splitter = CharacterTextSplitter(
            separator = "\n",
            chunk_size = int(os.getenv("CHUNK_SIZE")),
            chunk_overlap  = int(os.getenv("CHUNK_OVERLAP")),
            length_function = len,
        )
        print("\nSplitted!\n")
        return text_splitter.split_text(extracted_text)

    def create_pinecone_index(self):
        self.pinecone.create_index(
            name=os.getenv("PINECONE_INDEX_NAME"),
            dimension=int(os.getenv("EMBEDDING_MODEL_DIMENSION")),
            metric=os.getenv("SIMILARITY_METRIC"),
            spec=ServerlessSpec(cloud=os.getenv("CLOUD"), region=os.getenv("REGION")),
        )
        print("Index Created!")

    def get_indexes(self):
        return self.pinecone.list_indexes()

    def get_index(self, index_name):
        return self.pinecone.Index(index_name)

    def create_vectors(self, text_in_chunks: List[str], embedding_model: HuggingFaceEmbeddings) -> list:
        print("length of text chunks: ", len(text_in_chunks))
        print("Start creating embeddings!")
        vectors = []
        for text in text_in_chunks:
            vector = embedding_model.embed_query(text)
            vectors.append({
                "id": f"{uuid.uuid4()}",
                "values": vector,
                "metadata": {"original_text":text}
            })

        print("Length of vectors: ", len(vectors))
        return vectors
    
    def create_vector(self, text: str, embedding_model: HuggingFaceEmbeddings):
        return embedding_model.embed_query(text)
    
    def add_vectors(self, vectors, pinecone_index):
        print("Start adding vectors")
        batch_size=int(os.getenv("VECTOR_STORE_BATCH"))
        for i in range(0, len(vectors), batch_size):
            batch_vectors = vectors[i:i + batch_size]
            pinecone_index.upsert(
                vectors=batch_vectors,
                namespace=os.getenv("PINECONE_NAMESPACE")
            )
            print(f"Upserted batch {i // batch_size + 1} with {len(batch_vectors)} vectors")
    
    def get_simial_result(self, user_query_vector, index):
        print("Top Results: ", int(os.getenv("TOP_RESULTS")))
        result = index.query(
            namespace=os.getenv("PINECONE_NAMESPACE"),
            vector=user_query_vector,
            top_k=int(os.getenv("TOP_RESULTS")),
            include_metadata=os.getenv("INCLUDE_METADATA").lower() == "true"
        )

        context = ""
        for a in range(len(result['matches'])):
            print("Score:", result['matches'][a]['score'])
            context += f"\nreference {a+1}: \n"
            context += result["matches"][a]["metadata"]["original_text"]

        return context