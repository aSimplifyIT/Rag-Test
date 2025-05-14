from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from operator import itemgetter
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from typing import List
from uuid import UUID
import pandas as pd
import uuid
import os
import re

load_dotenv()

class VectorDatabaseService:
    def __init__(self):
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.file_name = 'uploaded_files.xlsx'

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
        text_splitter = CharacterTextSplitter(
            separator = "\n",
            chunk_size = int(os.getenv("CHUNK_SIZE")),
            chunk_overlap  = int(os.getenv("CHUNK_OVERLAP")),
            length_function = len,
        )
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
    
    def delete_vectors_by_namespace_id(self, namespace_id):
        print("Delete namespace id type: ", type(namespace_id))
        pinecone_index = self.get_index(os.getenv("PINECONE_INDEX_NAME"))
        stats = pinecone_index.describe_index_stats()
        if namespace_id in stats.get("namespaces", {}):
            pinecone_index.delete(delete_all=True, namespace=namespace_id)
    
    def add_vectors(self, vectors, pinecone_index, unique_nanespace_id: UUID):
        print("Start adding vectors")
        batch_size=int(os.getenv("VECTOR_STORE_BATCH"))
        for i in range(0, len(vectors), batch_size):
            batch_vectors = vectors[i:i + batch_size]
            pinecone_index.upsert(
                vectors=batch_vectors,
                namespace=str(unique_nanespace_id)
            )
            print(f"Upserted batch {i // batch_size + 1} with {len(batch_vectors)} vectors")
    
    def get_simial_result(self, user_query_vector, index):
        top_k = int(os.getenv("TOP_RESULTS"))
        include_metadata = os.getenv("INCLUDE_METADATA", "true").lower() == "true"
        
        namespace_ids = self.get_all_namespace_ids_from_excel()  # This should return a list of namespace strings
        all_matches = []

        for namespace_id in namespace_ids:
            try:
                result = index.query(
                    namespace=namespace_id,
                    vector=user_query_vector,
                    top_k=top_k,
                    include_metadata=include_metadata
                )
                if "matches" in result:
                    for match in result["matches"]:
                        match["namespace"] = namespace_id
                        all_matches.append(match)
            except Exception as e:
                print(f"Failed to query namespace {namespace_id}: {e}")

        sorted_matches = sorted(all_matches, key=itemgetter("score"), reverse=True)
        top_matches = sorted_matches[:top_k]

        context = ""
        for idx, match in enumerate(top_matches):
            print(f"[{match['namespace']}] Score: {match['score']}")
            context += f"\nReference {idx + 1} (namespace: {match['namespace']}):\n"
            context += match["metadata"].get("original_text", "")

        print("Extracted Content Length:", len(context))
        return context
    
    def add_file_in_excel(self, new_file_name) -> UUID:
        try:
            name, ext = os.path.splitext(new_file_name)
            unique_id = uuid.uuid4()
            new_data = {
                'File Name': [name],
                'File Extension': [ext],
                'Namespace Id': [str(unique_id)]
            }
            df_new = pd.DataFrame(new_data)

            if os.path.exists(self.file_name):
                df_existing = pd.read_excel(self.file_name, engine='openpyxl')
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                df_combined.to_excel(self.file_name, index=False, engine='openpyxl')
                print("Data appended successfully!")
            else:
                df_new.to_excel(self.file_name, index=False, engine='openpyxl')
                print("Excel file created and data added successfully!")

            return unique_id
        except Exception as e:
            print(str(e))

    def get_files_from_excel(self):
        if os.path.exists(self.file_name):
            df = pd.read_excel(self.file_name, engine='openpyxl')
            return df
        else:
            print("Excel file does not exist.")
            return pd.DataFrame()

    def get_all_namespace_ids_from_excel(self):
        if os.path.exists(self.file_name):
            df = pd.read_excel(self.file_name, engine='openpyxl')
            if 'Namespace Id' in df.columns:
                return df['Namespace Id'].dropna().unique().tolist()
            else:
                print("'Namespace Id' column not found.")
                return []
        else:
            print("Excel file does not exist.")
            return []
    
    def get_record_by_file_name(self, file_name):
        if not os.path.exists(self.file_name):
            self.add_file_in_excel(file_name)
        
        df = pd.read_excel(self.file_name, engine='openpyxl')
        record = df[df['File Name'] == file_name]
        if record.empty:
            return None
            # print("Startt")
            # self.add_file_in_excel(file_name)
            # df = pd.read_excel(self.file_name, engine='openpyxl')
            # record = df[df['File Name'] == file_name]

        if not record.empty:
            return record.iloc[0]['Namespace Id']

    def delete_record_by_file_name(self, file_name):
        if os.path.exists(self.file_name):
            df = pd.read_excel(self.file_name, engine='openpyxl')
            new_df = df[df['File Name'] != file_name]
            print(len(df))
            print(len(new_df))

            if len(new_df) == len(df):
                print("Record not found. Nothing deleted.")
            else:
                new_df.to_excel(self.file_name, index=False, engine='openpyxl')
                print(f"Record with File name'{file_name}' deleted successfully.")
        else:
            print("Excel file does not exist.")        
      