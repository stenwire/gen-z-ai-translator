# genz_translator.py
from sentence_transformers import SentenceTransformer
import chromadb
from data.genz_data import genz_dictionary
from dotenv import load_dotenv
import os

load_dotenv()


class GenZTranslator:
    def __init__(self, model_name='all-MiniLM-L6-v2', db_path="./chroma_db", llm_provider="google", llm_model_name="gemini-2.5-flash-lite"):
        self.model = SentenceTransformer(model_name)
        self.llm_model_name = llm_model_name
        self.llm_provider = llm_provider
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="genz_lingua")
        self._load_dictionary_into_db()

    def _load_dictionary_into_db(self):
        # Check if collection is empty to avoid re-adding on every run
        if self.collection.count() == 0:
            print("Loading Gen Z dictionary into ChromaDB...")
            documents = [f"{entry['term']}: {entry['definition']} (Example: {entry['example']})" for entry in genz_dictionary]
            metadatas = genz_dictionary # Store original dictionary entries as metadata
            ids = [f"genz-{i}" for i in range(len(genz_dictionary))]

            embeddings = self.model.encode(documents).tolist() # Generate embeddings

            self.collection.add(
                embeddings=embeddings,
                documents=documents, # Store the combined text for retrieval verification
                metadatas=metadatas,
                ids=ids
            )
            print(f"Loaded {len(genz_dictionary)} entries.")
        else:
            print(f"ChromaDB already contains {self.collection.count()} entries. Skipping load.")

    def get_relevant_genz_terms(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Retrieves the top_k most semantically relevant Gen Z terms for a given query.
        """
        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=['metadatas'] # We only need the original metadata (dictionary entries)
        )
        return results['metadatas'][0] if results['metadatas'] else []

    def translate_to_genz(self, text: str):
        if not isinstance(text, str) or not text.strip():
            return "Error: Invalid or empty input text."
        try:
            relevant_terms = self.get_relevant_genz_terms(text, top_k=7)
            terms_for_llm = ""
            if relevant_terms:
                terms_for_llm = "Here are some relevant Gen Z terms and their meanings you *must* try to incorporate naturally, along with emojis:\n"
                for term_data in relevant_terms:
                    terms_for_llm += f"- **{term_data['term']}**: {term_data['definition']} (Example: {term_data['example']})\n"
            else:
                terms_for_llm = "No specific dictionary terms were highly relevant, but use general Gen Z slang and emojis naturally."

            if self.llm_provider == "google":
                import google.generativeai as genai
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    return "Error: Missing GOOGLE_API_KEY."
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.llm_model_name)
                system_instruction = f"""
                You are an expert in 2025 Gen Z slang and emojis. Your task is to convert the user's message into authentic 2025 Gen Z slang.
                Maintain the original meaning and tone, and incorporate relevant emojis naturally.
                {terms_for_llm}
                Do NOT explain your translation or refer to the dictionary. Just provide the Gen Z version.
                """
                response = model.generate_content(
                    system_instruction + f"\nUser message: {text}\nGen Z conversion:",
                    generation_config=genai.types.GenerationConfig(temperature=0.7)
                )
                return response.text
            elif self.llm_provider == "openai":
                import openai
                openai.api_key = os.getenv("OPENAI_API_KEY")
                if not openai.api_key:
                    return "Error: Missing OPENAI_API_KEY."
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"""
                            You are an expert in 2025 Gen Z slang and emojis. Your task is to convert the user's message into authentic 2025 Gen Z slang.
                            Maintain the original meaning and tone, and incorporate relevant emojis naturally.
                            {terms_for_llm}
                            Do NOT explain your translation or refer to the dictionary. Just provide the Gen Z version.
                            """},
                        {"role": "user", "content": f"User message: {text}\nGen Z conversion:"}
                    ],
                    temperature=0.7,
                )
                return response.choices[0].message.content
            else:
                return "Error: Unsupported LLM provider."
        except Exception as e:
            return f"Error: Failed to translate due to {str(e)}. Please try again."

    def translate_to_english(self, text: str):
        if not isinstance(text, str) or not text.strip():
            return "Error: Invalid or empty input text."
        try:
            relevant_terms = self.get_relevant_genz_terms(text, top_k=7)
            terms_for_llm = ""
            if relevant_terms:
                terms_for_llm = "Here are some relevant Gen Z terms and their meanings that might be in the text:\n"
                for term_data in relevant_terms:
                    terms_for_llm += f"- **{term_data['term']}**: {term_data['definition']} (Example: {term_data['example']})\n"
            else:
                terms_for_llm = "No specific dictionary terms were highly relevant, but try to interpret any Gen Z slang."

            if self.llm_provider == "google":
                import google.generativeai as genai
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    return "Error: Missing GOOGLE_API_KEY."
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.llm_model_name)
                system_instruction = f"""
                You are an expert in 2025 Gen Z slang. Your task is to translate the user's message from Gen Z slang into standard, clear English.
                Maintain the original meaning and tone.
                {terms_for_llm}
                Do NOT explain your translation. Just provide the standard English version.
                """
                response = model.generate_content(
                    system_instruction + f"\nUser message: {text}\nEnglish conversion:",
                    generation_config=genai.types.GenerationConfig(temperature=0.7)
                )
                return response.text
            elif self.llm_provider == "openai":
                import openai
                openai.api_key = os.getenv("OPENAI_API_KEY")
                if not openai.api_key:
                    return "Error: Missing OPENAI_API_KEY."
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"""
                            You are an expert in 2025 Gen Z slang. Your task is to translate the user's message from Gen Z slang into standard, clear English.
                            Maintain the original meaning and tone.
                            {terms_for_llm}
                            Do NOT explain your translation. Just provide the standard English version.
                            """},
                        {"role": "user", "content": f"User message: {text}\nEnglish conversion:"}
                    ],
                    temperature=0.7,
                )
                return response.choices[0].message.content
            else:
                return "Error: Unsupported LLM provider."
        except Exception as e:
            return f"Error: Failed to translate due to {str(e)}. Please try again."

# Example usage:
if __name__ == "__main__":
    import os
    LLM = os.getenv("LLM", "google")
    translator = GenZTranslator()

    print("\n--- Testing Retrieval ---")
    query = "I am the coolest kid in my school"
    relevant = translator.get_relevant_genz_terms(query)
    print(f"Relevant terms for '{query}':")
    for term in relevant:
        print(f"- {term['term']}: {term['definition']}")

    print("\n--- Testing Translation ---")
    # Set your API keys as environment variables or directly in the code
    # For Google Gemini:
    # export GOOGLE_API_KEY='your_google_api_key'
    # For OpenAI:
    # export OPENAI_API_KEY='your_openai_api_key'

    if LLM == "google":
        llm_model_name = "gemini-2.5-flash-lite"
        genai_translation = translator.translate_to_genz("I am the coolest kid in my school.")
        print(f"\nOriginal: I am the coolest kid in my school.")
        print(f"Gen Z (Gemini): {genai_translation}")

        genai_translation_2 = translator.translate_to_genz("I'm really excited for the party tonight, it's going to be awesome!")
        print(f"\nOriginal: I'm really excited for the party tonight, it's going to be awesome!")
        print(f"Gen Z (Gemini): {genai_translation_2}")

    if LLM == "openai":
        llm_model_name="gpt-4"
        openai_translation = translator.translate_to_genz("I am the coolest kid in my school.")
        print(f"\nOriginal: I am the coolest kid in my school.")
        print(f"Gen Z (OpenAI): {openai_translation}")