import os 
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()

class EmbeddingGenerator:
    def __init__(self, model_name="text-multilingual-embedding-002"):
        self.model_name = model_name
        self.client = AzureOpenAI(
            api_key = os.getenv("API_KEY"),
            api_version = os.getenv("OPENAI_API_VERSION", "2024-02-01"),
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"))

    def embed(self, input_text: str):
        response = self.client.embeddings.create(model=self.model_name, input=input_text)
        return response.data[0].embedding
    
    def embed_batch(self, input_texts: list):
        response = self.client.embeddings.create(model=self.model_name, input=input_texts)
        embeddings = [item.embedding for item in response.data]
        return embeddings

if __name__ == "__main__":
    eg = EmbeddingGenerator()
    print(eg.embed("Hello, world!"))
    print(eg.embed_batch(["Hello, world!", "How are you?"]))
    print("\nHold on for a batch of 100...")
    print(eg.embed_batch(["Hello, world!" for i in range(100)]))
    