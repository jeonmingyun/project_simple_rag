import os
import sys
from dotenv import load_dotenv
from document_loader import load_and_chunk_documents
from vector_store import VectorStore
from rag_engine import RAGEngine

# Load environment variables from .env file
load_dotenv()

def print_header(title: str):
    print("\n" + "="*60)
    print(f" {title} ".center(60, "="))
    print("="*60)

def main():
    print_header("Gemini API & ChromaDB RAG System")
    
    # 1. Check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("[ERROR] .env 파일에 GEMINI_API_KEY가 설정되지 않았거나 기본값입니다.")
        print("프로젝트 루트의 .env 파일에 올바른 API 키를 입력해 주세요.")
        print("API 키 발급처: https://aistudio.google.com/")
        sys.exit(1)
        
    # 2. Setup folders
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    db_dir = os.path.join(base_dir, "chroma_db")
    
    os.makedirs(data_dir, exist_ok=True)
    
    # 3. Initialize components
    print("[INFO] 벡터 스토어 초기화 중...")
    try:
        vector_store = VectorStore(db_path=db_dir)
        rag_engine = RAGEngine(vector_store=vector_store)
    except Exception as e:
        print(f"[ERROR] 시스템 초기화 실패: {e}")
        sys.exit(1)
        
    # 4. Check if we need to load documents
    doc_count = vector_store.get_collection_count()
    print(f"[INFO] 현재 DB에 등록된 문서 청크 수: {doc_count}개")
    
    if doc_count == 0:
        print(f"\n[!] '{data_dir}' 폴더에 분석할 문서(PDF, TXT, Excel, PPT, 소스 코드 등)를 넣어주세요.")
        print("현재 데이터베이스(DB)가 비어 있어 색인 작업이 필요합니다. 엔터를 누르시면 색인을 시작합니다...")
        input()
        
        # We also put a default quick-start readme file if data folder is empty
        readme_path = os.path.join(data_dir, "quickstart_readme.txt")
        if not os.listdir(data_dir):
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("""Gemini RAG 프로젝트에 오신 것을 환영합니다!
이 파일은 프로젝트의 빠른 시작을 위해 자동으로 생성된 안내 파일입니다.
여기에 관심 있는 어떤 텍스트 문서든 추가하여 질문해 보세요.
예를 들어, 회사 규정집, 개발 문서, 뉴스 기사, 강의 노트 등을 TXT 또는 PDF 파일로 복사해 두면
Gemini API가 해당 문서를 분석하여 정확하고 친절하게 답변해 드립니다.""")
                print(f"[INFO] 기본 시작 파일 '{readme_path}'이 생성되었습니다.")
        
        # Load and index
        print("[INFO] 문서를 불러와 색인(Embedding)을 진행합니다...")
        docs = load_and_chunk_documents(data_dir)
        if docs:
            vector_store.add_documents(docs)
            print(f"[SUCCESS] {len(docs)}개 문서 청크가 색인되었습니다.")
        else:
            print("[WARNING] 색인할 문서가 없습니다.")
            
    # 5. Interactive query loop
    while True:
        print_header("RAG 질의응답 시스템")
        print(" 1. 질문하기 (Ask Question)")
        print(" 2. 문서 폴더 다시 색인하기 (Re-index documents)")
        print(" 3. 종료 (Exit)")
        print("="*60)
        
        choice = input("선택 (1/2/3): ").strip()
        
        if choice == "1":
            query_text = input("\n질문을 입력하세요: ").strip()
            if not query_text:
                continue
                
            print("\n[RAG] 관련 정보 검색 및 답변 생성 중...")
            try:
                result = rag_engine.query(query_text)
                
                print("\n" + "-"*60)
                print("■ 답변 (Answer):")
                print("-"*60)
                print(result["answer"])
                print("-"*60)
                
                print("\n■ 참조 출처 (Sources):")
                sources = result["sources"]
                if not sources:
                    print("  참조된 문서가 없습니다.")
                for idx, src in enumerate(sources):
                    doc_name = src["metadata"].get("source", "Unknown")
                    chunk_idx = src["metadata"].get("chunk_index", 0)
                    print(f"  [{idx+1}] {doc_name} (Chunk #{chunk_idx}) - 유사도 거리: {src['distance']:.4f}")
                    # Print snippet of chunk
                    snippet = src["content"].replace('\n', ' ')
                    if len(snippet) > 80:
                        snippet = snippet[:80] + "..."
                    print(f"      요약: {snippet}")
                print("-"*60)
                
            except Exception as e:
                print(f"[ERROR] 질의 처리 중 오류 발생: {e}")
                
            input("\n계속하려면 엔터를 누르세요...")
            
        elif choice == "2":
            print("\n[INFO] 'data/' 디렉터리에서 문서를 다시 불러와 색인 작업을 진행합니다...")
            try:
                docs = load_and_chunk_documents(data_dir)
                if docs:
                    vector_store.add_documents(docs)
                    print(f"[SUCCESS] 총 {vector_store.get_collection_count()}개 청크 색인 완료.")
                else:
                    print("[WARNING] 'data/' 폴더에 분석 가능한 문서 파일이 없습니다.")
            except Exception as e:
                print(f"[ERROR] 색인 중 오류 발생: {e}")
            input("\n계속하려면 엔터를 누르세요...")
            
        elif choice == "3":
            print("\n시스템을 종료합니다. 감사합니다!")
            break
        else:
            print("\n[!] 잘못된 선택입니다. 1, 2, 3 중 하나를 선택해 주세요.")
            input("\n계속하려면 엔터를 누르세요...")

if __name__ == "__main__":
    main()
