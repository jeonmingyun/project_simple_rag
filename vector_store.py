import os
from typing import List, Dict, Any
import chromadb
from google import genai
from dotenv import load_dotenv

# Load env variables
load_dotenv()

class VectorStore:
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "gemini_rag", embedding_model: str = "models/gemini-embedding-001"):
        # Ensure path is absolute to prevent confusion
        abs_db_path = os.path.abspath(db_path)
        self.client = chromadb.PersistentClient(path=abs_db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedding_model = embedding_model
        
    def _get_document_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate document embeddings using Gemini API."""
        try:
            # Check API Key configuration
            current_key = os.getenv("GEMINI_API_KEY")
            if not current_key or current_key == "your_gemini_api_key_here":
                raise ValueError("GEMINI_API_KEY is not set or invalid in .env file.")
            
            client = genai.Client(api_key=current_key)
                
            # Gemini embedding batch size limit is 2048 documents, batching in 100s for safety
            batch_size = 100
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                response = client.models.embed_content(
                    model=self.embedding_model,
                    contents=batch,
                )
                # In google-genai, response.embeddings is a list of objects, each containing .values
                embeddings = [emb.values for emb in response.embeddings]
                all_embeddings.extend(embeddings)
            return all_embeddings
        except Exception as e:
            print(f"Error generating document embeddings: {e}")
            raise e
            
    def _get_query_embedding(self, query: str) -> List[float]:
        """Generate query embedding using Gemini API."""
        try:
            current_key = os.getenv("GEMINI_API_KEY")
            if not current_key or current_key == "your_gemini_api_key_here":
                raise ValueError("GEMINI_API_KEY is not set or invalid in .env file.")
                
            client = genai.Client(api_key=current_key)
            
            response = client.models.embed_content(
                model=self.embedding_model,
                contents=query,
            )
            # Return the values list of the first (and only) embedding
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            raise e

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Adds documents to the vector store with manual embeddings."""
        if not documents:
            return
            
        ids = [doc["id"] for doc in documents]
        texts = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self._get_document_embeddings(texts)
        
        print("Upserting documents to ChromaDB...")
        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        print("Successfully added documents to ChromaDB.")

    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Queries the vector store for most similar documents."""
        query_emb = self._get_query_embedding(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=top_k
        )
        
        formatted_results = []
        if results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            ids = results["ids"][0]
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            
            for i in range(len(docs)):
                formatted_results.append({
                    "id": ids[i],
                    "content": docs[i],
                    "metadata": metas[i],
                    "distance": distances[i]
                })
        return formatted_results

    def get_collection_count(self) -> int:
        return self.collection.count()
