import os
from typing import List, Dict, Any
from google import genai
from dotenv import load_dotenv
from vector_store import VectorStore

# Load env variables
load_dotenv()

class RAGEngine:
    def __init__(self, vector_store: VectorStore, model_name: str = "gemini-flash-latest"):
        self.vector_store = vector_store
        self.model_name = model_name
        
    def query(self, query_text: str, top_k: int = 4) -> Dict[str, Any]:
        """Queries the vector store and generates an answer using Gemini model based on context."""
        try:
            # 1. Retrieve relevant documents
            sources = self.vector_store.query(query_text, top_k=top_k)
            
            # 2. Build context
            context_parts = []
            for idx, src in enumerate(sources):
                doc_title = src["metadata"].get("source", "Unknown Document")
                content = src["content"]
                context_parts.append(f"문서 [{idx+1}] (출처: {doc_title}, 유사도 거리: {src['distance']:.4f}):\n{content}")
                
            context = "\n\n".join(context_parts)
            
            # 3. Create prompt
            prompt = f"""당신은 질문에 답변하는 친절하고 정확한 AI 비서입니다.
아래에 제공된 [컨텍스트]를 바탕으로 사용자의 [질문]에 한국어로 정확하게 답변해 주세요.
제공된 컨텍스트와 무관한 답변을 지어내거나 외부 지식을 바탕으로 추측해서 답변하지 마세요.
만약 제공된 컨텍스트에서 답변을 찾을 수 없는 경우, "제공된 문서에서 관련 정보를 찾을 수 없습니다."라고 솔직하게 답변해 주세요.

[컨텍스트]
{context if context else '제공된 컨텍스트가 없습니다.'}

[질문]
{query_text}

[답변]"""

            # 4. Generate answer
            current_key = os.getenv("GEMINI_API_KEY")
            if not current_key or current_key == "your_gemini_api_key_here":
                raise ValueError("GEMINI_API_KEY is not set or invalid in .env file.")
                
            client = genai.Client(api_key=current_key)
            
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            return {
                "query": query_text,
                "answer": response.text,
                "sources": sources
            }
        except Exception as e:
            print(f"Error in RAG Engine query: {e}")
            raise e
