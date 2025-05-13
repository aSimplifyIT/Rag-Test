from common.constant import Constants
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pandas as pd
import requests
import uuid
import os

load_dotenv()

constants = Constants()

class ScrapperService():
    def __init__(self):
        self.scrape_base_url = os.getenv("QURAN_SCRAPPER_BASE_URL")
        self.data = []

    def quran_scrapper(self):
        try:
            for a in range(1, len(constants.surah_names)+1):
                scrape_url = f"{self.scrape_base_url}/{a}#{a}"
                response = requests.get(scrape_url)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")

                    surah_in_english = soup.find("h2", string=True)
                    surah_in_arabic = soup.find("h2", dir="rtl")

                    surah_name_en = surah_in_english.text.strip() if surah_in_english else "Not Found"
                    surah_name_ar = surah_in_arabic.text.strip() if surah_in_arabic else "Not Found"

                    verses = soup.find_all("div", id=lambda x: x and x.startswith("verse"))

                    for verse in verses:
                        arabic_div = verse.find("div", dir="rtl")
                        arabic_text = arabic_div.text.strip() if arabic_div else "Arabic text not found"

                        english_div = verse.find("div", dir="ltr")
                        english_text = english_div.text.strip() if english_div else "English translation not found"

                        if(english_text != "In the name of Allah, the Compassionate, the Merciful."):
                            self.data.append([f"{constants.surah_names[a-1]}", surah_name_ar, surah_name_en, arabic_text, english_text])
                else:
                    print(f"Failed to retrieve page. Status code: {response.status_code}")

        except Exception as e:
            print(f"An error occurred in method 'quran_scrapper': {e}")

    def save_to_excel(self):
        try:
            df = pd.DataFrame(self.data, columns=["SurahNameEnglish", "SurahNameArabic", "SurahTranslate", "Verse", "Translation"])
            file_name = os.getenv("SCRAPE_DATA_STORE")
            df.to_excel(file_name, index=False, engine="openpyxl")

        except Exception as e:
            print(f"An error occurred in method 'save_to_file': {e}")

    def make_chunks_and_vectors(self, embedding_model):
        try:
            chunks = []
            current_chunk = {
                "translations": [],
                "surahs": [],
                "verses": [],
                "length": 0
            }

            read_data = pd.read_excel(os.getenv("SCRAPE_DATA_STORE"))
            os.remove(os.getenv("SCRAPE_DATA_STORE"))
            for i in range(len(read_data)):
                translation_length = len(read_data.Translation[i])

                if translation_length <= (int(os.getenv("CHUNK_SIZE")) - current_chunk["length"]):
                    current_chunk["translations"].append(read_data.Translation[i])
                    current_chunk["surahs"].append(read_data.SurahNameEnglish[i])
                    current_chunk["verses"].append(read_data.Verse[i])
                    current_chunk["length"] += translation_length

                else:
                    chunks.append(current_chunk)
                    current_chunk = {
                        "translations": [read_data.Translation[i]],
                        "surahs": [read_data.SurahNameEnglish[i]],
                        "verses": [read_data.Verse[i]],
                        "length": translation_length
                    }

            vectors = []
            for chunk in chunks:
                vector = embedding_model.embed_query("\n".join(chunk["translations"]))
                vectors.append({
                    "id": f"{uuid.uuid4()}",
                    "values": vector,
                    "metadata": {"surahs": chunk["surahs"], "verses": chunk["verses"], "translation": chunk["translations"]}
                })
            
            return vectors
        
        except Exception as e:
            print(f"An error occurred in method 'make_chunks_and_vectors': {e}")