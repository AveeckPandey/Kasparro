# Kasparro Candidate Screening & Ranking System

An automated, explainable, production-minded candidate screening and ranking pipeline designed for an **SDE Internship requiring strong Python fundamentals and practical exposure to AI/agentic systems**.

This system ingests candidate resumes (PDF, DOCX, TXT), enforces strict rule-based eligibility filters, enriches candidate profiles with public GitHub activity metrics and developer cohorts, evaluates candidates using a 100-point explainability rubric with penalties for shallow wrappers, generates 50–100 word narrative justifications, and surfaces results via both a Rich CLI and an interactive web dashboard.

---

## Architecture Overview

```mermaid
flowchart TD
    User["Recruiter / Hiring Team"] --> InterfaceChoice{"Choose Interface"}
    
    InterfaceChoice -->|CLI Execution| CLI["Rich CLI Engine<br/>python main.py --input ./resumes"]
    InterfaceChoice -->|Web Dashboard| WebUI["FastAPI + Interactive UI<br/>http://localhost:8000"]
    
    subgraph Ingestion["1. Multi-Format Ingestion Engine"]
        DocParse["PDF (PyMuPDF & pypdf)<br/>DOCX (python-docx) | TXT"]
        LinkExtract["Extract Clickable PDF Links<br/>(GitHub, LinkedIn, Email)"]
        EntityExtract["Regex & Entity Normalizer<br/>(CGPA, Experience, Skills)"]
        DocParse --> LinkExtract --> EntityExtract
    end
    
    subgraph Filtering["2. Eligibility & Dynamic Filtering"]
        HardFilter{"Hard Eligibility Filter<br/>Python + AI/Agentic?"}
        DynamicDial["Dynamic Dials<br/>• Min CGPA Dial (0-10)<br/>• Related Experience<br/>• GitHub Link Required"]
        EntityExtract --> HardFilter
        HardFilter -->|Pass| DynamicDial
        HardFilter -->|Fail| Disqualified["Mark Ineligible<br/>Explicit Reasons"]
    end
    
    subgraph Enrichment["3. GitHub Deep Profiling"]
        GHApi["GitHub Public API<br/>(/users/{u}, /events/public, /repos)"]
        GHMetrics["Extract Metrics:<br/>• Account Age (Years)<br/>• Public Repositories<br/>• Recent Commits & Pulse<br/>• Relevant Python/AI Repos"]
        GHCohort["Cohort Classification:<br/>Veteran / Active / Emerging / Dormant"]
        GHCache[("Local Disk & Memory Cache")]
        DynamicDial -->|Eligible| GHApi
        GHApi <--> GHCache
        GHApi --> GHMetrics --> GHCohort
    end
    
    subgraph Scoring["4. 100-Point Explainable Scorer"]
        AIScore["AI / Agentic Depth (40 pts)<br/>Penalties: -5 to -15 Shallow Wrapper"]
        PyScore["Python & Backend (30 pts)<br/>FastAPI, Async, Postgres, Redis"]
        CloudScore["Cloud & Full Stack (15 pts)<br/>Docker, GCP, AWS, Next.js"]
        GHScore["GitHub Activity (10 pts)"]
        EngScore["Engineering Depth (5 pts)<br/>Testing, Queues, Observability"]
    end
    
    subgraph Reasoning["5. Narrative Reasoning Engine"]
        LLMAdapter["Provider Adapter<br/>(OpenAI / Gemini / Heuristic Fallback)"]
        Justification["Generate Guaranteed 50–100 Word<br/>Evidence-Backed Justification"]
        LLMAdapter --> Justification
    end
    
    GHCohort --> Scoring
    Scoring --> AIScore & PyScore & CloudScore & GHScore & EngScore
    AIScore & PyScore & CloudScore & GHScore & EngScore --> Reasoning
    Disqualified --> Reasoning
    
    Reasoning --> Outputs["Final Deliverables:<br/>• output/results.json<br/>• output/results.csv<br/>• Real-time UI Cards"]
```

---

## Key Features

1. **Multi-Format Ingestion & Hyperlink Extraction**:
   - Parses `.pdf` (via `PyMuPDF` with `pypdf` fallback), `.docx`, and `.txt`.
   - **Clickable PDF URI Extraction**: Extracts embedded PDF hyperlink annotations (e.g., clickable GitHub or LinkedIn icons that do not expose raw text).
   - Fault-tolerant: Corrupted or unreadable files are recorded with descriptive errors without crashing the batch.

2. **Hard Rule-Based Eligibility Filter**:
   - **Python Stack Evidence**: Requires genuine Python development (FastAPI, Django, Flask, SQLAlchemy, etc.). Rejects pure JavaScript/Java/MERN candidates.
   - **AI / Agentic Exposure**: Requires demonstrable exposure to LangGraph, LangChain, ADK, LlamaIndex, RAG pipelines, embeddings, tool-calling agents, or vector databases.
   - Produces explicit rejection reasons for every disqualified candidate.

3. **Interactive Filter Dials (User Requirements)**:
   - **CGPA Dial / Slider**: Normalizes 10-point scales, 4.0 GPA, and percentages to a standardized 10.0 scale. Allows setting a minimum CGPA threshold.
   - **Related Experience Toggle**: Flags candidates with verified software engineering or AI internships.
   - **GitHub Profile Required Toggle**: Filters for candidates providing a public GitHub profile.

4. **GitHub Deep Profiling & Cohort Segmentation**:
   - **`account_age_years`**: Exact account age calculated from `created_at`.
   - **`public_repos`**: Total public repositories and count of relevant Python/AI repositories.
   - **`recent_commits`**: Commits extracted from public push events.
   - **Developer Cohorts**: Classifies candidates into *Veteran Builder* (3+ years, 10+ repos, active commits), *Active Builder*, *Emerging Developer*, *Dormant*, or *Unlinked*.
   - **Rate-Limit Resilience & Caching**: Supports optional `GITHUB_TOKEN`, handles HTTP 403 gracefully without failing the candidate, and caches profiles locally in `.github_cache.json`.

5. **100-Point Explainable Scoring Model**:
   - **AI / Agentic / RAG Project Depth (40 pts)**: Rewards multi-agent graphs, hybrid search RAG, tool calling, and evaluation pipelines.
     - **Penalties**: Deducts 5–15 points for shallow LLM API wrappers (e.g., single prompt-in/prompt-out with no retrieval, state, or tools) and tutorial-style projects without ownership.
   - **Python & Backend Engineering (30 pts)**: Rewards async FastAPI, PostgreSQL/SQLAlchemy, and Redis caching. Keyword-only mentions receive capped credit.
   - **Cloud / Deployment / Full Stack (15 pts)**: Docker, GCP/AWS, and supporting React/Next.js frontend.
   - **GitHub Activity (10 pts)**: 0–5 pts recent activity + 0–5 pts maintained/relevant repos.
   - **Engineering Depth Signals (5 pts)**: Unit testing (pytest), queues (Celery/Kafka), and observability.

6. **50–100 Word Narrative Justification Engine**:
   - Produces an explainable narrative between 50 and 100 words for every candidate (both ranked and disqualified) citing specific technical evidence.

7. **Dual Interface: Rich CLI + Interactive Web Dashboard**:
   - **CLI**: Headless execution with rich colored summary tables, cohort distributions, and export to JSON/CSV.
   - **Web UI**: Modern single-page application served via FastAPI (`http://localhost:8000`) supporting folder upload (up to 100 resumes), live dials, search, score breakdown bars, and downloadable exports.

---

## Quick Start

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone <repo-url>
cd Kasparro
pip install -r requirements.txt
```

### 2. Configuration (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key variables:
- `GITHUB_TOKEN`: (Optional) GitHub Personal Access Token to increase public API rate limits from 60 req/hr to 5,000 req/hr.
- `OPENAI_API_KEY` or `GEMINI_API_KEY`: (Optional) To use live LLM completions. If left unset, the system uses the built-in deterministic heuristic engine.

---

## Running the Application

### Option A: Command Line Interface (CLI)
Screen the provided 50 resumes and export the results to JSON and CSV:
```bash
python main.py --input ./resumes --output ./output/results.json
```

**Additional CLI Options**:
```bash
# Filter by minimum CGPA (e.g. 7.5/10)
python main.py --input ./resumes --min-cgpa 7.5

# Require related internship experience and a public GitHub link
python main.py --input ./resumes --require-experience --require-github

# Adjust concurrency (default: 5 worker threads)
python main.py --input ./resumes --concurrency 8
```

### Option B: Interactive Web Dashboard & FastAPI
Launch the web server:
```bash
python main.py --serve
# Or directly via uvicorn:
# uvicorn src.api:app --reload --port 8000
```
Open **`http://localhost:8000`** in your browser. From the dashboard, you can:
1. Click **"Screen 50 Sample Resumes"** to run batch screening with one click.
2. Upload a custom folder or files (up to 100 resumes).
3. Adjust the **Minimum CGPA Dial** (0.0 to 10.0).
4. Toggle **AI Background**, **Experience**, and **GitHub Link** filters.
5. Inspect real-time candidate cards with 50–100 word justifications, score meters, and GitHub metrics.
6. Download the filtered output as `results.json` or `results.csv`.

---

## API Endpoints

- `GET /`: Interactive web dashboard.
- `GET /health`: Health status check.
- `POST /screen`: Screen a directory on the filesystem.
  ```json
  {
    "input_dir": "./resumes",
    "min_cgpa": 7.0,
    "require_ai": true,
    "require_experience": false,
    "require_github_link": false
  }
  ```
- `POST /upload_and_screen`: Multipart file upload (up to 100 resumes) with form parameters.
- `GET /results`: Fetch the latest screening report.
- `GET /download_csv`: Download results as a CSV file.

---

## Output Format (`output/results.json`)

The generated JSON matches the required schema with full evidence, score breakdown, and batch statistics:

```json
{
  "batch_summary": {
    "total_resumes": 50,
    "successfully_parsed": 50,
    "eligible": 32,
    "rejected": 18,
    "failed_unreadable": 0,
    "github_cohorts": {
      "Veteran Builder": 9,
      "Active Builder": 1,
      "Emerging Developer": 2,
      "Dormant / Minimal": 0,
      "Unlinked / Missing": 20,
      "Active Developer": 9,
      "Unverified (Rate Limited)": 9
    },
    "average_score_eligible": 63.0
  },
  "ranked_candidates": [
    {
      "rank": 1,
      "candidate_name": "V Sree Raghu Vardhan",
      "file_name": "candidate_30.pdf",
      "eligible": true,
      "total_score": 94.5,
      "score_breakdown": {
        "ai_project_depth": 37.0,
        "python_backend": 30.0,
        "cloud_fullstack": 14.0,
        "github": 10.0,
        "engineering_depth": 3.5
      },
      "matched_skills": ["Python", "FastAPI", "LangGraph", "ChromaDB", "Docker", "GCP"],
      "project_summary": "Built systems utilizing Stateful multi-agent orchestration (LangGraph), Vector database retrieval...",
      "github_summary": "Veteran Builder (4.2 yrs on GitHub, 35 repos, 0 recent commits). 3 relevant Python/AI repositories identified.",
      "strengths": [
        "Stateful multi-agent orchestration (LangGraph/CrewAI/AutoGen)",
        "Async FastAPI backend architecture",
        "Docker containerization & deployment"
      ],
      "concerns": ["No significant technical weaknesses observed"],
      "rejection_reasons": [],
      "reason_50_to_100_words": "V Sree Raghu Vardhan qualifies as an eligible candidate with a total score of 94.5/100. The candidate demonstrates practical engineering capability highlighted by stateful multi-agent orchestration (langgraph/crewai/autogen), vector database retrieval (chromadb/faiss/pinecone/qdrant), supported by core stack competencies in Python, FastAPI, Django, PostgreSQL, Redis. GitHub enrichment indicates: Veteran Builder (4.2 yrs on GitHub, 35 repos). Primary area for review: No significant technical weaknesses observed. Overall, this profile exhibits solid engineering depth and the requisite hands-on exposure to modern agentic systems to succeed in the SDE AI internship.",
      "github_metrics": {
        "username": "vardhanvsr",
        "account_age_years": 4.2,
        "public_repos": 35,
        "recent_commits": 0,
        "relevant_ai_python_repos": 3,
        "cohort": "Veteran Builder",
        "status": "enriched"
      },
      "cgpa": 8.5,
      "has_related_experience": true
    }
  ],
  "rejected_candidates": [
    {
      "rank": null,
      "candidate_name": "Kartikay Sinha",
      "file_name": "candidate_01.pdf",
      "eligible": false,
      "total_score": 0.0,
      "rejection_reasons": [
        "No evidence of Python stack",
        "No AI/agentic project evidence"
      ],
      "matched_skills": ["React", "Next.js", "Javascript", "Typescript", "Node.Js"],
      "reason_50_to_100_words": "Kartikay Sinha was marked ineligible during screening due to no evidence of python stack, no ai/agentic project evidence. While the candidate presents background in React, Next.js, Javascript, Typescript, the profile lacks practical evidence of Python backend development and demonstrable exposure to agentic, RAG, or LLM-based workflows. For this SDE internship, candidates must demonstrate functional experience building with Python services alongside agent orchestration, tool calling, or vector retrieval pipelines. Consequently, this profile does not meet the mandatory baseline criteria for further scoring consideration."
    }
  ]
}
```

---

## Design Decisions

### 1. Ingestion & Embedded Link Extraction
Resumes submitted as PDFs often store GitHub and LinkedIn profiles as **clickable link annotations** attached to SVG icons rather than raw textual URLs. Relying solely on regular expressions on raw text would fail to extract GitHub profiles for over 30% of modern resumes. We implemented a hybrid strategy: `PyMuPDF` extracts all URI link annotations (`page.get_links()`), with regex fallback on text.

### 2. Hard Eligibility Filtering Strategy
Eligibility is kept intentionally rule-based and deterministic before any scoring occurs. We reject candidates who lack genuine Python evidence or meaningful AI/agentic project exposure. Candidates with complementary skills (e.g., React, TypeScript, Java) are **not** rejected as long as Python and AI exposure are present. This prevents well-formatted frontend resumes from scoring high.

### 3. Anti-Shallow Wrapper Scoring & Quality Penalties
To fulfill the requirement that candidates with superficial AI projects do not rank near the top, the scoring engine enforces quality penalties:
- **Shallow API Wrapper Penalty (-12 pts)**: If a resume lists OpenAI or Gemini completions without retrieval, state management, vector databases, or backend logic.
- **Tutorial Project Penalty (-8 pts)**: If projects follow common tutorial templates (e.g., basic To-Do apps, generic Titanic ML) without evidence of system ownership.
- **Skills-Only Cap**: Keyword mentions in the skills section receive minimal credit unless substantiated in project or experience sections.

### 4. LLM Usage & Fallback Design
The system uses an **Adapter Pattern** (`BaseLLMAdapter`). If an API key (`OPENAI_API_KEY` or `GEMINI_API_KEY`) is present, it uses structured LLM prompts to generate evaluations. If no API key is provided, or if the API times out/fails, it automatically falls back to our deterministic `HeuristicAdapter`. This ensures 100% offline testability, zero flaky test dependencies, and zero cost out of the box.

### 5. GitHub Deep Profiling & Resilience
GitHub contributes up to 10 points as an **enrichment booster**. A candidate with no GitHub or a private profile is never disqualified. Rate-limiting is handled by inspecting response status codes (HTTP 403/429) and continuing gracefully with 0 GitHub points while caching results in `.github_cache.json` to prevent redundant network requests.

---

## If I Had More Time

If given additional time to extend the system, the next 4 improvements would be:

1. **Static AST Analysis of GitHub Repositories**:
   Instead of relying on GitHub API metadata alone, clone/inspect top public repositories to perform AST analysis on Python code (e.g., checking for type hints, pytest test coverage, async concurrency, and LangGraph state graph definitions).
2. **LangSmith / Ragas Evaluation Benchmark**:
   Implement an automated evaluation pipeline measuring the consistency and alignment of LLM resume rankings against human recruiter shortlists.
3. **Multi-Page OCR for Scanned Image Resumes**:
   Integrate Tesseract OCR or PaddleOCR for resumes submitted as non-searchable flattened images or scanned printouts.
4. **Interactive Weight Customizer in the Web Dashboard**:
   Allow hiring managers to adjust rubric category weights (e.g., increasing Cloud weight from 15% to 25% for infrastructure-heavy cohorts) directly from the UI dials with real-time re-ranking.

---

## Test Suite

Run the comprehensive pytest suite:
```bash
python -m pytest -v
```

**Test Coverage Highlights**:
- `test_filters.py`: Validates rejection of pure JS/React and Java/Spring profiles, acceptance of Python + AI, and dynamic CGPA dial filtering.
- `test_scoring.py`: Validates 100-pt rubric breakdown and verifies deduction of points for thin wrappers.
- `test_github.py`: Validates GitHub caching, rate-limit resilience, and unlinked profiles.
- `test_parsers.py`: Tests PDF/DOCX parsing, entity extraction, CGPA normalization, and corrupted file tolerance.
- `test_narrative.py`: Enforces 50–100 word count constraints on generated justifications.
- `test_api.py`: Tests `/health`, `/results`, `/download_csv`, and dashboard rendering.

All 24 test cases pass with 100% success.
