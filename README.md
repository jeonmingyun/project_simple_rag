# Gemini API & ChromaDB RAG System

Google Gemini API와 로컬 벡터 데이터베이스인 ChromaDB를 연동한 문서 기반 질의응답(RAG) 파이썬 토이 프로젝트입니다.

텍스트 문서와 PDF뿐만 아니라 Excel, PPTX 및 각종 소스 코드 파일(Java, Python 등)을 지원하며, 텍스트가 없는 이미지 기반의 스캔 PDF나 이미지 파일도 Gemini의 멀티모달 능력을 활용한 OCR 기능으로 자동 텍스트를 추출하여 데이터베이스에 색인(Index)하고 검색할 수 있도록 구현되었습니다.

### 🛠️ 주요 기술 스택 (Tech Stack)
* **Language**: Python 3.11
* **LLM & Embedding**: Google GenAI SDK
* **Vector Database**: ChromaDB
* **Document Parsing**:
  * PDF: `pypdf`
  * Excel: `pandas`, `openpyxl`
  * PowerPoint: `python-pptx`
* **Configuration**: `python-dotenv`

---

## 🌟 핵심 기능

1. **다양한 파일 포맷 분석 지원**
   - 일반 문서 및 소스 코드: `.txt`, `.md`, `.java`, `.py`, `.js`, `.html`, `.css`, `.c`, `.cpp`, `.h`, `.json`, `.xml`, `.csv` 등
   - PDF 문서: `.pdf` (일반 PDF 텍스트 추출)
   - 스프레드시트(Excel): `.xlsx`, `.xls` (각 시트를 읽어 Markdown/CSV 형태로 전처리)
   - 파워포인트(PPT): `.pptx` (슬라이드별 텍스트 박스 단위 추출)

2. **스캔 이미지 PDF 및 일반 이미지 OCR 지원**
   - 일반 텍스트 레이어가 없어 텍스트 추출이 불가능한 PDF 파일이나 일반 이미지 파일(`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`)이 입력될 경우, Gemini API의 파일 업로드 기능 및 멀티모달 기능을 사용하여 이미지 속의 한국어 텍스트를 고성능으로 읽어내 색인합니다.
   * *구글 최신 `google-genai` SDK 적용으로 발생하는 한글 파일명 헤더 전송 오류를 우회하기 위한 임시 파일명 우회 로직이 내장되어 있습니다.*

3. **로컬 벡터 데이터베이스 (ChromaDB)**
   - Gemini의 `models/gemini-embedding-001` 임베딩 모델을 활용하여 문서 청크의 임베딩 값을 추출하고 로컬 디렉터리에 영구 저장하여 보관합니다.

4. **대화형 CLI 인터페이스**
   - CLI 환경에서 문서 추가 후 갱신(색인 생성), 질문하기, 매칭된 문서 출처 및 유사도 점수 시각화 등의 기능을 제공합니다.

---

## 📁 폴더 및 파일 구조

```text
simple-rag/
│
├── data/                 # 분석할 원본 문서 파일을 넣는 폴더 (PDF, Excel, PPTX, TXT 등)
├── chroma_db/            # ChromaDB 데이터베이스가 로컬에 생성되는 폴더 (자동 생성)
│
├── main.py               # 대화형 CLI 실행 진입점
├── document_loader.py    # 문서 로드, 파싱, 텍스트 청킹 및 이미지 OCR 처리 로직
├── vector_store.py       # ChromaDB 인스턴스 연동 및 임베딩 추출 로직
├── rag_engine.py         # 검색된 컨텍스트 조립 및 Gemini LLM 연동 답변 생성 로직
│
├── requirements.txt      # 프로젝트 필수 의존성 패키지 목록
└── .env                  # API Key 등 환경 변수 설정 파일 (템플릿 제공)
```

---

## 🚀 시작하기

### 1. 사전 준비
컴퓨터에 **Python 3.11** 이상이 설치되어 있어야 합니다.

### 2. 가상환경 세팅 및 라이브러리 설치

**가상환경(venv) 생성:**
```bash
python -m venv venv
```

**가상환경 활성화:**
- **PowerShell (Windows)**:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process # 실행 제한 오류 해결용
  C:\[YOUR_PROJECT_PATH]\venv\Scripts\Activate.ps1
  ```
- **명령 프롬프트(CMD) (Windows)**:
  ```cmd
  C:\[YOUR_PROJECT_PATH]\venv\Scripts\activate.bat
  ```

**필수 라이브러리 설치:**
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 (`.env`) 설정
개인용 Gemini API Key를 설정하기 위해 프로젝트 루트 폴더에 `.env` 파일을 생성하고 키를 입력합니다.
*(주의: 보안상 API 키 누출을 방지하기 위해 `.env` 파일과 벡터 DB 폴더 `chroma_db/`, 문서 `data/` 내부 파일은 `.gitignore`에 등록되어 깃허브 업로드 대상에서 자동으로 제외됩니다.)*

프로젝트 루트 경로에 `.env` 파일을 만들고 아래 내용을 입력합니다:
```env
GEMINI_API_KEY=AIzaSy...(여기에 발급받은 실제 API 키 입력)
```
> **Tip:** API 키는 [Google AI Studio](https://aistudio.google.com/)에서 구글 계정으로 로그인하여 무료로 쉽게 발급받으실 수 있습니다. (신형 키 포맷인 `AQ.Ab...`로 시작하는 키도 원활하게 지원합니다.)

---

## 💡 사용 방법

### 1. 프로그램 구동
터미널(PowerShell 또는 CMD)에서 아래 명령어를 실행하여 구동합니다:
```bash
# 가상환경 활성화가 번거로운 경우 직접 실행법 (CMD / PowerShell 공통)
"C:\[YOUR_PROJECT_PATH]\venv\Scripts\python.exe" "C:\[YOUR_PROJECT_PATH]\main.py"
```

### 2. 문서 업로드 및 색인
1. `data/` 폴더에 질문하고 싶은 문서나 소스 코드 파일(PDF, Excel, PPTX, TXT, Java 등)을 넣어둡니다.
2. 프로그램 실행 후 메뉴에서 **`2` (문서 폴더 다시 색인하기)**를 선택하여 데이터베이스에 분석 내용을 등록합니다.
   - *팁: 색인이 완료되면 `data/` 폴더 내의 원본 파일은 지우거나 다른 곳으로 백업해 두어도 데이터베이스(`chroma_db/`)에 기록되어 있어 질문이 가능합니다.*

### 3. 질문 및 답변 확인
1. 메뉴에서 **`1` (질문하기)**을 선택합니다.
2. 질문을 입력하면 데이터베이스에서 가장 유사한 상위 컨텍스트를 찾아 화면에 보여주고, Gemini AI가 이를 분석하여 친절한 한글 답변을 제공합니다.
3. 답변 아래에서 질문과 연관성이 높았던 문서명과 유사도 점수를 함께 확인할 수 있습니다.
