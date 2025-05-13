## Project Overview

The "Ask Quran" chatbot is designed to provide users with accurate responses to their queries based on Quranic text. The system retrieves relevant Quranic verses, presents them in Arabic along with their translations, and includes references (Surah name and verse number).

## How It Works

**How It Works:** The user submits a question or request for information.<br>
**Retrieval:** The system searches a structured dataset of Quranic text and translations stored in a vector database.<br>
**Processing:** A Retrieval-Augmented Generation (RAG) approach ensures that the response is contextually relevant. The Large Language Model (LLM) further refines the answer.<br>
**Response Generation:** The chatbot presents the final response, including:<br>

- The most relevant Quranic verse (in Arabic)
- Its translation
- The Surah name and verse number

## Technologies Used

This repository includes a wide range of technologies and tools used in various machine learning and data science projects:

- **Programming Languages:** Python
- **Libraries/Frameworks:**
  - Vector Databases & Retrieval: Pinecone, pinecone-client, pinecone-text, pinecone-notebooks
  - LLM & AI Integration: OpenAI, LangChain-Community, LangChain-HuggingFace
  - Data Processing: Pandas, OpenPyXL, PyPDF2
  - Web Development & APIs: FastAPI, Uvicorn
  - Scraping & Parsing: BeautifulSoup (bs4), Requests
  - Validation & Environment Handling: Pydantic, Dotenv, Python-Multipart
    pinecone-client, pinecone-text, pinecone-notebooks, langchain-community, pinecone, langchain-huggingface, PyPDF2
    openai==0.28.0, fastapi, uvicorn, bs4, requests, pandas, openpyxl, pydantic, dotenv, python-multipart,
    py-automapper, psycopg2, pyjwt, expiring-dict, alembic
- **Tools & Platforms:**
  - Vector Database: Pinecone
  - Backend Database: PostgreSQL
  - Backend Services: FastAPI
  - Version Control: Git and GitHub
  - Development Environment: Visual Studio Code

## Project Setup

- **Virtual Environment:**
  - (Create) python -m venv _<env_name>_
  - (activate-Windows) _<env_name>_\Scripts\activate
  - (activate-Mac/Linux) source _<env_name>_/bin/activate<br>
- **Libraries Install/Uninstall:**
  - pip install -r requirements.txt (install all libraries which are include in requirements.txt)
  - pip uninstall -r requirements.txt -y (uninstall all libraries which are installed in the project)<br>
    **Note:** Always install libraries inside the activated virtual environment to ensure project dependencies are properly managed.
- **Start Project:**
  - Open the terminal and navigate to the WebApi directory: **cd WebApi**
  - Run the application: **python app.py**
  - Once the application starts, open **Swagger UI** in your browser: http://127.0.0.1:8000/docs
- **Database Migration:**
  - alembic init alembic
  - add your models in the _<alembic/env.py e.g target_metadata = [<model_name>.metadata]>_
  - alembic revision -m _<migration_name>_
  - alembic upgrade head
