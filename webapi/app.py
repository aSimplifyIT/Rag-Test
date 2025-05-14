import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.vector_database_service import VectorDatabaseService
from services.model_service import ModelService
from services.scrapper_service import ScrapperService
from services.user_service import UserService
from services.conversation_service import ConversationService
from services.message_service import MessageService
from common.Requests.conversation_request import ConversationRequest
from common.Requests.user_create import UserCreate
from common.Requests.user_login import UserLogin
from common.Requests.recent_query_request import RecentQueryRequest
from common.Requests.text_request import TextRequest
from common.enums import MessageRole
from webapi.web_base import WebBase
from webapi.security import authorize
from webapi.cache_handler import CacheHandler

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import asyncio
import openai

vector_db_service = VectorDatabaseService()
model_service = ModelService()
scrapper_service = ScrapperService()
user_service = UserService()
conversation_service = ConversationService()
message_service = MessageService()
web_base = WebBase()
cache_handler = CacheHandler()

app = FastAPI()
app.add_middleware(CORSMiddleware,allow_origins="*",allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.add_exception_handler(HTTPException, web_base.http_exception_handler)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/quran_scrapper", dependencies=[Depends(authorize)])
async def quran_scrapper():
    try:
        scrapper_service.quran_scrapper()
        scrapper_service.save_to_excel()
        embedding_model = model_service.get_embedding_model()
        vectors = scrapper_service.make_chunks_and_vectors(embedding_model)

        pinecone_indexes = vector_db_service.get_indexes()
        if os.getenv("PINECONE_INDEX_NAME") not in pinecone_indexes.names():
            vector_db_service.create_pinecone_index()
        pinecone_index = vector_db_service.get_index(os.getenv("PINECONE_INDEX_NAME"))

        vector_db_service.add_vectors(vectors, pinecone_index)

        return {"Quran scrapped successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    try:
        with open(file.filename, "wb") as f:
            f.write(await file.read())

        loaded_file = vector_db_service.load_dataset(file.filename)
        extracted_text = vector_db_service.read_data(loaded_file)
        text_in_chunks = vector_db_service.text_splitter(extracted_text)

        pinecone_indexes = vector_db_service.get_indexes()
        if os.getenv("PINECONE_INDEX_NAME") not in pinecone_indexes.names():
            vector_db_service.create_pinecone_index()

        pinecone_index = vector_db_service.get_index(os.getenv("PINECONE_INDEX_NAME"))

        embedding_model = model_service.get_embedding_model()
        vectors = vector_db_service.create_vectors(text_in_chunks, embedding_model)

        unique_nanespace_id = vector_db_service.add_file_in_excel(file.filename)
        vector_db_service.add_vectors(vectors, pinecone_index, unique_nanespace_id)

        os.remove(file.filename)

        return web_base.generate_result_response(result={"File added successfuly"})
    
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)

@app.get("/files")
async def get_files():
    try:
        df = vector_db_service.get_files_from_excel()
        files = []
        if not df.empty:
            for _, row in df.iterrows():
                if row.get("File Name", "") != "appended_text":
                    files.append({
                        "name": row.get("File Name", ""),
                        "extension": row.get("File Extension", "")
                    })

        return web_base.generate_result_response(result={"files": files})

    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)
    
async def openai_stream(previous_conversation):
    try:
        print("Previous: ", previous_conversation)
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=previous_conversation,
            stream=True
        )

        print("Response completed")
        agent_response = "" 
        for chunk in response:
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content")

            if content:
                agent_response += content
                yield f"{content}\n\n"
                await asyncio.sleep(0)

    except Exception as e:
        print(f"error: {str(e)}")

@app.post("/conversation")
async def conversation(request: ConversationRequest):
    try:
        user_query = request.user_query
        embedding_model = model_service.get_embedding_model()
        user_query_vector = vector_db_service.create_vector(user_query, embedding_model)
        pinecone_index = vector_db_service.get_index(os.getenv("PINECONE_INDEX_NAME"))
        similar_context = vector_db_service.get_simial_result(user_query_vector, pinecone_index)
        system_prompt = model_service.system_prompt(similar_context)

        previous_conversation = []
        if request.chat_history:
            previous_conversation = [msg.dict() for msg in request.chat_history]
            previous_conversation = [{**item, 'content': f'{{"message":"{item["content"]}"}}' if item['role'] == 'assistant' else item['content']} for item in previous_conversation]
            previous_conversation.insert(0, {"role": MessageRole.SYSTEM.name.lower(), "content": system_prompt})
            previous_conversation.append({"role": MessageRole.USER.name.lower(), "content": user_query})
        if not request.chat_history:
            previous_conversation.insert(0, {"role": MessageRole.SYSTEM.name.lower(), "content": system_prompt})
            previous_conversation.append({"role": MessageRole.USER.name.lower(), "content": user_query})

        print("previous adjusted")
        return StreamingResponse(openai_stream(previous_conversation), media_type="text/event-stream")
        
    except HTTPException as e:
        return web_base.generate_error_response(errors=[e.detail], status_code=e.status_code)

    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)

@app.post("/add_recent_query")
async def add_recent_query(request: RecentQueryRequest):
    try:
        key=f"test-user"
        cache_handler.set(key, [
            {
                "role": MessageRole.ASSISTANT.name.lower(),
                "content": request.assistant_respnose
            }
        ])
        
        return web_base.generate_result_response(result={"recent query added"})
    
    except HTTPException as e:
        return web_base.generate_error_response(errors=[e.detail], status_code=e.status_code)

    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500) 
 
@app.get("/user_conversations")
async def get_user_conversations(current_user: dict = Depends(authorize)):
    try:
        user_id = current_user.get("user_id")
        conversations_read = conversation_service.get_conversations_by_user_id(user_id)

        return web_base.generate_result_response(conversations_read)

    except HTTPException as e:
        return web_base.generate_error_response(errors=[e.detail], status_code=e.status_code)
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)

@app.get("/get_chat_messages")
async def get_chat_messages():
    try:
        key ="test-user"
        if cache_handler.is_key_exist(key):
            cache_history = cache_handler.get(key)
            return web_base.generate_result_response(cache_history)
        
        return web_base.generate_result_response(result={})
        
    except HTTPException as e:
        return web_base.generate_error_response(errors=[e.detail], status_code=e.status_code)
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)

@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id, current_user: dict = Depends(authorize)):
    try:
        user_id = current_user.get("user_id")
        is_success = conversation_service.delete_conversation(conversation_id, user_id)
        if is_success:
            return web_base.generate_result_response(result={"Delete successfully"})
        else:
            return web_base.generate_error_response(errors=["Conversation not found"], status_code=400)
    
    except HTTPException as e:
        return web_base.generate_error_response(errors=[e.detail], status_code=e.status_code)
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)

@app.post("/user_signup")
async def user_create(user_create_request: UserCreate):
    try:
        if user_create_request.password != user_create_request.confirm_password:
            raise HTTPException(status_code=400, detail="Password did not match")
        
        if user_service.check_user_exist(user_create_request.email):
            raise HTTPException(status_code=400, detail="Already taken")
        
        user_read = user_service.user_create(user_create_request)
        return web_base.generate_result_response(result=user_read)
    
    except HTTPException as e:
        return web_base.generate_error_response(errors=[e.detail], status_code=e.status_code)
    
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)

@app.post("/user_login")
async def user_login(user_login_request: UserLogin):
    try:
        user = user_service.get_user_by_email(user_login_request.email)
        is_exist = user_service.verify_login_user(user, user_login_request.password)
        if not is_exist:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        token = user_service.generate_jwt_token(user.Id, user.Email, user.FirstName, user.LastName)
        return web_base.generate_result_response(result=token)
    
    except HTTPException as e:
        return web_base.generate_error_response(errors=[e.detail], status_code=e.status_code)
    
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)

@app.delete("/file")
async def delete_file(file_name: str):
    try:
        namespace_id = vector_db_service.get_record_by_file_name(file_name)
        vector_db_service.delete_vectors_by_namespace_id(namespace_id)
        vector_db_service.delete_record_by_file_name(file_name)

        return web_base.generate_result_response(result={f"file {file_name} delete successfully"})
    
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)

@app.post("/text")
async def add_text(test_request: TextRequest):
    try:
        file_path = "appended_text.txt"
        
        if os.path.exists(file_path):
            name, ext = os.path.splitext(file_path)
            namespace_id = vector_db_service.get_record_by_file_name(name)
            if namespace_id != None:
                vector_db_service.delete_vectors_by_namespace_id(namespace_id)
                vector_db_service.delete_record_by_file_name(name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_request.text + '\n')

        text_in_chunks = vector_db_service.text_splitter(test_request.text)

        pinecone_indexes = vector_db_service.get_indexes()
        if os.getenv("PINECONE_INDEX_NAME") not in pinecone_indexes.names():
            vector_db_service.create_pinecone_index()

        pinecone_index = vector_db_service.get_index(os.getenv("PINECONE_INDEX_NAME"))

        embedding_model = model_service.get_embedding_model()
        vectors = vector_db_service.create_vectors(text_in_chunks, embedding_model)

        unique_nanespace_id = vector_db_service.add_file_in_excel(file_path)
        vector_db_service.add_vectors(vectors, pinecone_index, unique_nanespace_id)

        return web_base.generate_result_response(result={"Text added successfully"})
    
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)

@app.get("/text")
async def read_text():
    try:
        file_path = "appended_text.txt"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return web_base.generate_result_response(result={"text": content})
        else:
            return web_base.generate_result_response(result={"text": ""})
        
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)
    
@app.delete("/text")
async def delete_file():
    try:
        file_path = "appended_text.txt"
        if os.path.exists(file_path):
            name, ext = os.path.splitext(file_path)
            namespace_id = vector_db_service.get_record_by_file_name(name)
            vector_db_service.delete_vectors_by_namespace_id(namespace_id)
            vector_db_service.delete_record_by_file_name(name)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")
            return web_base.generate_result_response(result={"Text empty"})
        else:
            return web_base.generate_result_response(result={"Text empty"})
        
    except Exception as e:
        return web_base.generate_error_response(errors=[str(e)], status_code=500)
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)