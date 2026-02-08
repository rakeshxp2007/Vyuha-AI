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

The UPSC Civil Services Mains examination is not just about knowledge; it is about **presentation** and **structure**. Aspirants face specific challenges that generic LLMs fail to address:
* **Strict Word Limits:** Answers must be strictly 150 or 250 words.
* **Contextual Linkage:** Static syllabus topics (History/Geography) must be linked to dynamic Current Affairs.
* **Value Addition:** High-scoring answers require specific elements like "Value Addition Boxes," diagrams, or relevant case studies.

## 💡 The Solution

**Vyuha-AI** leverages a specialized Multi-Agent architecture to simulate the thought process of a UPSC Topper.

### Key Features
* **📝 Structured Drafting:** Automatically formats answers into the mandatory *Introduction → Body → Conclusion* flow.
* **💎 Value Addition Box:** A dedicated agent injects a "Value Addition" section (Facts, Articles, Supreme Court Judgments) to boost score potential.
* **⏱️ Word Limit Enforcement:** Strict token constraints ensure answers fit within the 150/250 word mandate.
* **🔗 Dynamic Context:** RAG pipelines retrieve relevant context from standard textbooks and recent editorials.
* **🔍 Observability:** Full transparency into agent reasoning and latency via **Opik**.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **LLM** | **Google Gemini** | `gemini-1.5-pro` & `gemini-1.5-flash` for reasoning and drafting. |
| **Frontend** | **Streamlit** | Interactive chat interface for aspirants. |
| **Observability** | **Opik (by Comet)** | Tracing, evaluation, and latency monitoring. |
| **Orchestration** | **LangChain / Custom** | Managing agent workflows and RAG retrieval. |
| **Deployment** | **Docker** | Containerized application for easy deployment. |

---

## 📊 Opik Integration (Hackathon Track)

Vyuha-AI is built with **Opik** at its core to ensure reliability in a hallucination-prone domain like education.

### How we use Opik:
1.  **Traceability:** We trace the full lifecycle of a user query—from the RAG retriever fetching documents to the Drafting Agent generating the final response.
2.  **Evaluation:** We track "hallucination rates" by logging retrieved context against generated answers.
3.  **Cost & Latency:** Monitoring the trade-off between the faster `gemini-flash` (for retrieval) and `gemini-pro` (for drafting).

*(Place a screenshot of your Opik Dashboard Traces here)*

---

## 📂 Project Flow Diagram

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
🗺️ Roadmap
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
