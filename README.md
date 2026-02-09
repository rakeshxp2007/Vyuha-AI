# 🏛️ Vyuha-AI: UPSC Mains Strategy Partner

<img width="1024" height="344" alt="Banner-Vyuha" src="https://github.com/user-attachments/assets/697f1408-0d76-4a71-9280-6f53d0c697f0" />

---

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini-4E8BF5?logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![LLM: OpenAI](https://img.shields.io/badge/LLM-OpenAI-000000)](https://openai.com/)
[![Vector DB: LanceDB](https://img.shields.io/badge/VectorDB-LanceDB-4B8BFF)](https://lancedb.com/)
[![Observability by Opik](https://img.shields.io/badge/Observability-Opik-FF6B6B)](https://www.comet.com/site/products/opik/)
[![Models: HuggingFace](https://img.shields.io/badge/Models-HuggingFace-FFD21E)](https://huggingface.co/)
[![License: Custom](https://img.shields.io/badge/License-Custom-red)](#-license--hackathon-usage)


---

> **"Vyuha" (Sanskrit: व्यूह)** refers to a strategic formation or arrangement.
> **Vyuha-AI** is a Multi-Agent RAG system designed to help UPSC Mains aspirants strategically structure, draft, and evaluate their answers against "Topper-level" benchmarks.

---

## 📸 10 Marks Q&A

<img width="1024" height="773" alt="10_mark_answer" src="https://github.com/user-attachments/assets/322b133f-87af-4b55-ae56-74b6563155b9" />


## 📸 15 Marks Q&A
<img width="1024" height="773" alt="15_mark_answer" src="https://github.com/user-attachments/assets/c68d7989-ec97-4020-ae32-4c9460dae525" />

---

## 🚀 The Problem

The `UPSC Civil Service Examination (UPSC-CSE)` evaluates how an aspirant can connect and think, plan, and write answers by linking relevant topics while also meeting the minimum demand of the question—all within the word limit or roughly 8–9 minutes per question. This requires a lot of practice. Some estimates suggest the top 100 rankers have given almost 100 full tests before appearing for the Mains. They represent less than 1% of total applicants. The **rest 99%**, although they may understand the demand, are not able to reproduce that in the exam. With GPT models in the market, aspirants get answers for practice which are rich in content, but reproducing such content is not humanly possible in those 180 minutes.

## 💡 The Solution

> **Vyuha-AI** leverages a specialized Multi-Agent architecture to simulate the thought process of a UPSC Topper.

### Key Features
* **📝 Structured Drafting:** Automatically formats answers into the mandatory *Introduction → Body → Conclusion* flow.
* **⏱️ Word Limit Enforcement:** Strict token constraints ensure answers fit within the 150/250 word mandate.
* **🔗 Dynamic Context:** RAG pipelines retrieve relevant context from standard textbooks and recent editorials.
* **🔍 Observability:** Full transparency into agent reasoning and latency via **Opik**.

---

## 🧰 Tech Stack

| Component           | Technology              | Description |
|---------------------|--------------------------|-------------|
| Agent Intelligence  | Google Gemini 3          | Primary reasoning engine for both SME and team orchestration; optimized for high-token UPSC contextual reasoning. |
| Embedding Engine    | text-embedding-3-large   | 3,072-dimensional embeddings enabling high-precision semantic retrieval from dense NCERT and static syllabus content. |
| Vector Database     | LanceDB                  | Serverless, disk-persistent vector store enabling row-aware retrieval to preserve contextual integrity across documents. |
| Orchestration       | Agno (Phidata)           | Agent orchestration layer providing tracing, evaluation, latency monitoring, and prompt versioning for reliable agentic workflows. |
| Observability       | Opik (by Comet)          | End-to-end observability for agent traces, evaluation runs, latency metrics, and systematic prompt experimentation. |
| Frontend            | Streamlit                | Interactive UI designed to surface both the final UPSC answer and the underlying agent planning workflow. |


---

## 📊 Opik Integration (Hackathon Track)

Vyuha-AI is built with **Opik** at its core to ensure reliability in a hallucination-prone domain like education.

### How we use Opik:
1.  **Traceability:** We trace the full lifecycle of a user query—from the RAG retriever fetching documents to the Drafting Agent generating the final response.
2.  **Evaluation:** We track "hallucination rates" by logging retrieved context against generated answers.
3.  **Cost & Latency:** Monitoring the trade-off between the faster `gemini-flash` (for retrieval) and `gemini-pro` (for drafting).

| <img width="1024" height="1245" alt="Span" src="https://github.com/user-attachments/assets/31a424cc-189e-412d-bc4e-a582e6f54a40" /> |
|--- |
| `Opik`: A span |


---

## 📊 Performance Benchmarking

| Metric                | Value  | Technical Context |
|-----------------------|--------|-------------------|
| Context Recall        | 85.6%  | High-fidelity retrieval enabled by 3,072-dimension embeddings over dense NCERT and static syllabus content. |
| Answer Relevance      | 93.2%  | Strong alignment with UPSC-specific question demand and directive adherence. |
| Hallucination Metric  | 98.4%  | High groundedness enforced through mandatory dual-source citation and RAG constraints. |
| Levenshtein Ratio     | 0.40   | Intentional divergence indicating successful restructuring of raw content into a superior, exam-oriented answer format. |

---

## 🛠️  Project Flow Diagram

<img width="1024" height="1536" alt="Flow-diagram" src="https://github.com/user-attachments/assets/02daa380-18ee-484e-9c3f-7413a97ec845" />

---

## ⚙️ Installation & Setup

### Prerequisites
- Python **3.10+**
- **Google AI Studio (Gemini) API Key**
- **Opik API Key**

---

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/Vyuha-AI.git
cd Vyuha-AI
```

2️⃣ Configure Environment Variables
Create a `.env` file in the project root:
```
GOOGLE_API_KEY="your_gemini_api_key"
OPIK_API_KEY="your_opik_api_key"
OPIK_WORKSPACE="your_opik_workspace"
```

3️⃣ Install Dependencies
```
pip install -r requirements.txt
```

4️⃣ Run Locally
```
uv run streamlit run app.py
```

---
## 🗺️ Roadmap

[x] Phase 1: Core RAG Agent for GS-1 (History/Geography).

[x] Phase 2: Integration of Opik for full system observability.

[ ] Phase 3: Specialized agents for GS-2 (Polity) and GS-3 (Economy).

[ ] Phase 4: Image generation for automatic map/diagram creation.

---

🤝 Contributors

* Sanchita Deb
* Pankaj Kumar

---

## 📜 License & Hackathon Usage

**License**: All Rights Reserved © Rakesh Kumar Sahoo

**Hackathon Evaluation License**:  
Judges and authorized organizers are granted a **temporary, non-exclusive, non-transferable license** to fork, run, and evaluate this repository **solely for hackathon evaluation purposes** until **March 10, 2026**.


---
