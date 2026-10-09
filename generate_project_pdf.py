"""Script to generate a comprehensive, publication-quality PDF documentation for Kasparro."""

import os
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
    HRFlowable,
    Preformatted,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page numbers and running headers/footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running header on pages 2+
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "Kasparro Candidate Screening & Ranking System - Project Documentation")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.6)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Running footer on all pages
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.6)
        self.line(54, 46, 8.5 * 72 - 54, 46)

        self.drawString(54, 32, "GitHub: https://github.com/AveeckPandey/Kasparro")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 32, page_str)
        self.restoreState()


def make_code_box(text: str, style: ParagraphStyle, width: float, bg_color: str = "#f8fafc", border_color: str = "#cbd5e1"):
    """Helper to wrap preformatted code into a cleanly styled, high-contrast box."""
    p = Preformatted(text.strip(), style)
    t = Table([[p]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(border_color)),
        ('PADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return t


def build_pdf(filename: str = "Kasparro_Project_Documentation.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14,
    )

    h1_style = ParagraphStyle(
        "DocH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "DocH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "DocBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3,
    )

    code_style = ParagraphStyle(
        "DocCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0f172a"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
    )

    table_cell_code = ParagraphStyle(
        "TableCellCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
    )

    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # ---------------------------------------------------------
    # HEADER / COVER SECTION
    # ---------------------------------------------------------
    story.append(Paragraph("Kasparro Candidate Screening & Ranking System", title_style))
    story.append(Paragraph("Production-Grade Automated Screening, GitHub Deep Profiling & Explainable 100-Point Scoring for SDE AI Roles", subtitle_style))

    # GitHub Repository Highlight Box
    github_url = "https://github.com/AveeckPandey/Kasparro"
    github_callout_data = [
        [
            Paragraph(
                f"<b>Official GitHub Repository:</b> <font color='#2563eb'><u><a href='{github_url}'>{github_url}</a></u></font><br/>"
                f"<b>Project Author:</b> Aveeck Pandey &nbsp;|&nbsp; <b>Tech Stack:</b> Python 3.10+, FastAPI, PyMuPDF, Pydantic v2, ReportLab, Rich CLI<br/>"
                f"<b>Documentation Generated:</b> {datetime.now().strftime('%B %Y')} &nbsp;|&nbsp; <b>License:</b> Open Source / Educational",
                callout_style
            )
        ]
    ]
    github_table = Table(github_callout_data, colWidths=[doc.width])
    github_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(github_table)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 1: WHAT DOES THIS PROJECT DO?
    # ---------------------------------------------------------
    story.append(Paragraph("1. Executive Summary: What Does This Project Do?", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "The <b>Kasparro Candidate Screening & Ranking System</b> is an automated, explainable, production-ready "
        "recruitment pipeline specifically engineered to evaluate candidates for an <b>SDE Internship requiring strong Python "
        "backend fundamentals and practical exposure to Agentic AI and Retrieval-Augmented Generation (RAG)</b>.",
        body_style
    ))
    story.append(Paragraph(
        "Traditional Applicant Tracking Systems (ATS) rely on shallow keyword searches that can easily be manipulated by candidates "
        "copy-pasting buzzwords into their resumes. Kasparro replaces naive keyword scanning with an evidence-based multi-stage evaluation engine "
        "that deeply inspects document semantics, verifies code via public GitHub APIs, applies a 100-point rubric with penalties for shallow API wrappers, "
        "and synthesizes concise 50-100 word hiring justifications.",
        body_style
    ))

    story.append(Paragraph("Key Core Capabilities:", h2_style))
    story.append(Paragraph("&bull; <b>Multi-Format Ingestion & Hyperlink Extraction:</b> Ingests PDF, DOCX, and TXT resumes. Uniquely extracts embedded PDF URI hyperlinks (such as clickable GitHub or LinkedIn icons) that do not expose raw URL text.", bullet_style))
    story.append(Paragraph("&bull; <b>Hard Rule-Based Eligibility Gatekeeper:</b> Enforces non-negotiable baselines: requires verifiable Python backend experience (FastAPI, Flask, Django) and demonstrable AI/Agentic tooling (LangChain, LangGraph, ADK, RAG, vector search). Rejects pure JavaScript/Java candidates with explicit disqualification notes.", bullet_style))
    story.append(Paragraph("&bull; <b>Deep GitHub Profiling & Developer Cohorts:</b> Queries GitHub's public API to calculate exact account age, count public and original repositories, measure recent commit velocity, and categorize developers into distinct cohorts (Veteran Builder, Active Builder, Emerging Developer, Dormant).", bullet_style))
    story.append(Paragraph("&bull; <b>100-Point Explainable Scoring Rubric:</b> Evaluates candidates across 5 weighted dimensions (AI Depth: 40 pts, Python Backend: 30 pts, Cloud/Full Stack: 15 pts, GitHub: 10 pts, Engineering Signals: 5 pts) with automated penalties (-5 to -15 pts) for shallow LLM prompt-in/prompt-out wrappers.", bullet_style))
    story.append(Paragraph("&bull; <b>Guaranteed 50-100 Word Narrative Justifications:</b> Employs an LLM Reasoning Engine (or deterministic heuristic fallback) to generate individualized, evidence-backed hiring justifications citing specific repositories and strengths.", bullet_style))
    story.append(Paragraph("&bull; <b>Multi-Format Export Engine:</b> Automatically produces comprehensive exports in JSON, CSV, Microsoft Excel (.xlsx), and Microsoft Word (.docx).", bullet_style))
    story.append(Paragraph("&bull; <b>Dual User Interfaces:</b> Operates both as a terminal CLI with rich styled tables and as an interactive, single-page web dashboard served by FastAPI.", bullet_style))
    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # SECTION 2: PROJECT ARCHITECTURE & STRUCTURE
    # ---------------------------------------------------------
    story.append(Paragraph("2. Project Architecture & Directory Structure", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The project follows a clean, modular, service-oriented architecture designed for maintainability, fault-tolerance, and high throughput. "
        "The repository tree and component responsibilities are outlined below:",
        body_style
    ))

    tree_text = (
        "Kasparro/\n"
        "|-- main.py                     # Root CLI & FastAPI server entrypoint\n"
        "|-- requirements.txt            # Production Python package dependencies\n"
        "|-- .env.example                # Environment variables template & API keys\n"
        "|-- .env                        # Local runtime configuration\n"
        "|-- README.md                   # Project documentation & usage instructions\n"
        "|-- static/\n"
        "|   \\-- index.html              # Single-page web dashboard (Monochrome dark UI)\n"
        "|-- src/\n"
        "|   |-- api.py                  # FastAPI server, screening routes & upload handlers\n"
        "|   |-- cli.py                  # Rich terminal CLI engine with progress bars & tables\n"
        "|   |-- config.py               # Pydantic Settings management & environment bindings\n"
        "|   |-- models.py               # Strict Pydantic v2 data models, schemas & validation\n"
        "|   |-- pipeline.py             # End-to-end multithreaded screening pipeline orchestrator\n"
        "|   |-- parsers/\n"
        "|   |   |-- resume_parser.py    # Multi-format doc parser (PyMuPDF, pypdf, docx) & link extractor\n"
        "|   |   \\-- entity_extractor.py # Regex & heuristic entity extractor (CGPA, skills, contact)\n"
        "|   |-- filters/\n"
        "|   |   \\-- eligibility.py      # Hard rule-based eligibility gatekeeper\n"
        "|   |-- enrichment/\n"
        "|   |   \\-- github_client.py    # GitHub REST client, rate-limit resilience, cache & cohorts\n"
        "|   |-- scoring/\n"
        "|   |   \\-- scorer.py           # 100-point explainability scorer & shallow wrapper penalty\n"
        "|   \\-- llm/\n"
        "|       \\-- adapter.py          # Multi-provider LLM adapter (Groq, OpenAI, Gemini, Claude, Fallback)\n"
        "|-- resumes/                    # Corpus of 50 sample candidate resumes (PDF, DOCX, TXT)\n"
        "|-- output/                     # Generated results (results.json, .csv, .xlsx, .docx, cache)\n"
        "\\-- tests/                      # Automated test suite (Pytest fixtures & unit tests)"
    )

    story.append(make_code_box(tree_text, code_style, doc.width, bg_color="#f8fafc", border_color="#cbd5e1"))
    story.append(Spacer(1, 10))

    # Module breakdown table
    module_data = [
        [Paragraph("Module / File", table_header_style), Paragraph("Core Responsibility & Technical Implementation", table_header_style)],
        [
            Paragraph("<b>src/parsers/resume_parser.py</b>", table_cell_code),
            Paragraph("Extracts text and embedded hyperlink annotations across PDF (PyMuPDF + pypdf fallback), DOCX (python-docx), and TXT formats. Never crashes on corrupted files.", table_cell_style)
        ],
        [
            Paragraph("<b>src/parsers/entity_extractor.py</b>", table_cell_code),
            Paragraph("Normalizes candidate names, emails, phones, LinkedIn links, and CGPA (standardizes 10.0, 4.0 GPA, percentages to a uniform 10.0 scale). Categorizes skill tags across 6 technical domains.", table_cell_style)
        ],
        [
            Paragraph("<b>src/filters/eligibility.py</b>", table_cell_code),
            Paragraph("Binary gatekeeper enforcing mandatory Python backend depth (FastAPI/Django) and demonstrable AI/Agentic project exposure. Produces explicit disqualified reasons.", table_cell_style)
        ],
        [
            Paragraph("<b>src/enrichment/github_client.py</b>", table_cell_code),
            Paragraph("Queries public GitHub API to extract account age in years, public repositories, and commit velocity. Classifies candidates into developer cohorts with local caching to prevent rate limiting.", table_cell_style)
        ],
        [
            Paragraph("<b>src/scoring/scorer.py</b>", table_cell_code),
            Paragraph("Implements the 100-point rubric. Rewards multi-agent graphs and hybrid RAG; deducts -5 to -15 pts for shallow wrappers and -8 pts for tutorial-style code.", table_cell_style)
        ],
        [
            Paragraph("<b>src/llm/adapter.py</b>", table_cell_code),
            Paragraph("Provides unified adapter interface for Groq, OpenAI, Google Gemini, Anthropic Claude, and deterministic heuristic fallback. Enforces strict 50-100 word justification bounds.", table_cell_style)
        ],
        [
            Paragraph("<b>src/pipeline.py</b>", table_cell_code),
            Paragraph("Orchestrates parallel candidate processing with ThreadPoolExecutor, aggregates batch metrics, and handles exports to JSON, CSV, Excel, and Word DOCX.", table_cell_style)
        ],
        [
            Paragraph("<b>src/api.py & static/index.html</b>", table_cell_code),
            Paragraph("FastAPI service offering REST endpoints and serving the responsive single-page web UI with folder upload, PDF preview modal, live dials, and export toolbars.", table_cell_style)
        ],
        [
            Paragraph("<b>src/cli.py & main.py</b>", table_cell_code),
            Paragraph("Command-line interface with rich ASCII banners, colored progress bars, summary metric tables, and server launch flags.", table_cell_style)
        ],
    ]

    mod_table = Table(module_data, colWidths=[doc.width * 0.35, doc.width * 0.65])
    mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(mod_table)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 3: WHICH LLMS ARE BEING USED?
    # ---------------------------------------------------------
    story.append(Paragraph("3. LLM Architecture: Which LLMs & Models Are Being Used?", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Kasparro features a <b>pluggable, multi-provider LLM reasoning architecture</b> implemented via the "
        "<code>BaseLLMAdapter</code> pattern. It allows recruiters to switch between state-of-the-art hosted LLM providers "
        "or operate completely offline with zero external dependencies.",
        body_style
    ))

    llm_data = [
        [Paragraph("Provider", table_header_style), Paragraph("Default Model ID", table_header_style), Paragraph("API Protocol", table_header_style), Paragraph("Characteristics & Usage", table_header_style)],
        [
            Paragraph("<b>Groq Cloud</b>", table_cell_style),
            Paragraph("<code>qwen/qwen3.8-27b</code><br/>(or Llama 3.3 70B)", table_cell_style),
            Paragraph("OpenAI-compatible HTTP (/v1/chat/completions)", table_cell_style),
            Paragraph("Ultra-low latency inference (~250 tokens/sec). Ideal for processing high-volume batches (e.g. 50-100 resumes) in seconds at near-zero cost.", table_cell_style)
        ],
        [
            Paragraph("<b>OpenAI</b>", table_cell_style),
            Paragraph("<code>gpt-4o-mini</code><br/>(or <code>gpt-4o</code>)", table_cell_style),
            Paragraph("OpenAI Chat Completions REST API", table_cell_style),
            Paragraph("High reasoning precision and reliable instruction following. Used for nuanced evaluation justifications and technical stack verification.", table_cell_style)
        ],
        [
            Paragraph("<b>Google Gemini</b>", table_cell_style),
            Paragraph("<code>gemini-1.5-flash</code>", table_cell_style),
            Paragraph("Google Generative Language API (v1beta)", table_cell_style),
            Paragraph("Fast multi-modal speed with long context capability and strong structural reasoning.", table_cell_style)
        ],
        [
            Paragraph("<b>Anthropic Claude</b>", table_cell_style),
            Paragraph("<code>claude-3-5-haiku-latest</code>", table_cell_style),
            Paragraph("Anthropic Messages REST API (/v1/messages)", table_cell_style),
            Paragraph("High analytical fidelity and nuanced narrative generation. Excels at identifying shallow buzzwords vs genuine depth.", table_cell_style)
        ],
        [
            Paragraph("<b>Heuristic Engine</b><br/>(Built-in Fallback)", table_cell_style),
            Paragraph("Deterministic rule engine<br/>(MD5 Seed Rotation)", table_cell_style),
            Paragraph("Local in-process Python execution (Zero network calls)", table_cell_style),
            Paragraph("100% offline fallback. Employs MD5 candidate hashing to vary sentence structures and synthesize candidate-specific evidence. Zero latency, guaranteed 50-100 words.", table_cell_style)
        ],
    ]

    llm_table = Table(llm_data, colWidths=[doc.width * 0.20, doc.width * 0.25, doc.width * 0.25, doc.width * 0.30])
    llm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(llm_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Dynamic Provider Selection & Resilience Architecture:", h2_style))
    story.append(Paragraph("&bull; <b>Automatic Provider Discovery (<code>LLM_PROVIDER=auto</code>):</b> When set to auto, the factory inspects available environment variables in priority order (<code>OPENAI_API_KEY</code> -&gt; <code>GEMINI_API_KEY</code> -&gt; <code>ANTHROPIC_API_KEY</code> -&gt; <code>GROQ_API_KEY</code> -&gt; <code>HeuristicAdapter</code>).", bullet_style))
    story.append(Paragraph("&bull; <b>Strict Anti-Template Negative Constraints:</b> Prompts explicitly prohibit generic openings (such as <i>'Candidate qualifies as an eligible candidate...'</i>) and enforce direct technical evidence citing specific repositories, score numbers, and technical gaps.", bullet_style))
    story.append(Paragraph("&bull; <b>Guaranteed Word Count Enforcer:</b> The engine runs a programmatic <code>_ensure_word_count()</code> post-processor ensuring all narratives remain strictly within the 50 to 100 word constraint required by recruitment standards.", bullet_style))
    story.append(Paragraph("&bull; <b>Graceful API Degradation:</b> If any LLM API call times out, encounters HTTP 429 rate limits, or returns non-conforming responses, it transparently falls back to the deterministic heuristic engine without aborting the batch run.", bullet_style))
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 4: 100-POINT SCORING RUBRIC & PENALTIES
    # ---------------------------------------------------------
    story.append(Paragraph("4. Explainable 100-Point Scoring Model & Penalties", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Kasparro implements an objective, mathematically transparent 100-point rubric tailored for an SDE AI intern role. "
        "The score is decomposed into 5 distinct categories, complemented by deduction logic for low-effort submissions:",
        body_style
    ))

    score_data = [
        [Paragraph("Category", table_header_style), Paragraph("Weight", table_header_style), Paragraph("Evaluation Criteria & Evidence Signals", table_header_style)],
        [
            Paragraph("<b>AI / Agentic / RAG Depth</b>", table_cell_style),
            Paragraph("<b>40 pts</b>", table_cell_style),
            Paragraph("LangGraph/LangChain multi-agent graphs, stateful agent loops, hybrid search RAG, vector databases (Chroma, Qdrant, Pinecone), embeddings, tool calling, and evaluation pipelines.", table_cell_style)
        ],
        [
            Paragraph("<b>Python & Backend Engineering</b>", table_cell_style),
            Paragraph("<b>30 pts</b>", table_cell_style),
            Paragraph("Modern async FastAPI/Django services, SQLAlchemy ORM, PostgreSQL database schemas, Redis caching, and async worker patterns. Mentions without depth receive capped credit.", table_cell_style)
        ],
        [
            Paragraph("<b>Cloud, DevOps & Full Stack</b>", table_cell_style),
            Paragraph("<b>15 pts</b>", table_cell_style),
            Paragraph("Containerization (Docker, Docker Compose), cloud deployment (AWS, GCP), CI/CD pipelines, and supporting modern web frontends (Next.js, React).", table_cell_style)
        ],
        [
            Paragraph("<b>GitHub Activity & Proven Code</b>", table_cell_style),
            Paragraph("<b>10 pts</b>", table_cell_style),
            Paragraph("Scored from verified public activity: account longevity (0-2 pts), public repository depth (0-3 pts), and recent commit velocity/pulse (0-5 pts).", table_cell_style)
        ],
        [
            Paragraph("<b>Engineering Depth Signals</b>", table_cell_style),
            Paragraph("<b>5 pts</b>", table_cell_style),
            Paragraph("Unit and integration testing (pytest, unittest), message queues (Celery, Kafka, RabbitMQ), logging, telemetry, and observability.", table_cell_style)
        ],
    ]

    score_table = Table(score_data, colWidths=[doc.width * 0.30, doc.width * 0.15, doc.width * 0.55])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Automated Penalty Architecture:", h2_style))
    story.append(Paragraph("&bull; <b>Shallow LLM Wrapper Penalty (-5 to -15 pts):</b> Penalizes resumes that claim 'AI development' but only implement single-prompt OpenAI API completions without state management, tool calling, vector search, or evaluation.", bullet_style))
    story.append(Paragraph("&bull; <b>Tutorial / Forked Clone Penalty (-8 pts):</b> Penalizes obvious tutorial clones (e.g. basic to-do apps with a chatbot) that demonstrate zero independent architecture or engineering ownership.", bullet_style))
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 5: HOW TO RUN THIS PROJECT
    # ---------------------------------------------------------
    story.append(Paragraph("5. Step-by-Step Guide: How to Run This Project", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("Step 1: Clone the Repository", h2_style))
    step1_code = "git clone https://github.com/AveeckPandey/Kasparro.git\ncd Kasparro"
    story.append(make_code_box(step1_code, code_style, doc.width))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 2: Create a Virtual Environment & Install Dependencies", h2_style))
    step2_code = "# Create virtual environment\npython -m venv venv\n\n# Activate environment\n# Windows (PowerShell):\n.\\venv\\Scripts\\activate\n# macOS / Linux:\nsource venv/bin/activate\n\n# Install required dependencies\npip install -r requirements.txt"
    story.append(make_code_box(step2_code, code_style, doc.width))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 3: Configure Environment Variables (Optional)", h2_style))
    story.append(Paragraph("Copy the provided template to configure API keys for GitHub or LLM providers:", body_style))
    step3_code = "cp .env.example .env\n\n# Optional variables in .env:\n# GITHUB_TOKEN=ghp_your_token_here       # Increases GitHub API rate limit from 60 to 5,000 req/hr\n# LLM_PROVIDER=auto                      # auto, groq, openai, gemini, anthropic, or heuristic\n# GROQ_API_KEY=gsk_your_groq_key_here    # Free ultra-fast Qwen/Llama inference\n# OPENAI_API_KEY=sk-your_openai_key_here # Optional OpenAI API key"
    story.append(make_code_box(step3_code, code_style, doc.width))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 4: Launch the Web Dashboard (Interactive Interface)", h2_style))
    story.append(Paragraph("Launch the FastAPI web server to access the sleek monochrome recruiter dashboard:", body_style))
    step4_code = "python main.py --serve --port 8000\n\n# Open your web browser at:\n# http://localhost:8000"
    story.append(make_code_box(step4_code, code_style, doc.width))
    story.append(Paragraph(
        "<b>Web UI Capabilities:</b> Drag-and-drop batch resume upload (up to 100 files), 1-click sample screening of the 50 bundled resumes, "
        "interactive min passing score dialer, Top 5/10/20 quick filter pills, real-time candidate search, PDF resume viewer modal, "
        "and one-click downloads for Excel, Word, CSV, and JSON.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 5: Run Batch Screening via Command-Line Interface (CLI)", h2_style))
    story.append(Paragraph("For CI/CD pipelines or headless server workflows, execute screening directly via the CLI:", body_style))
    step5_code = "# Standard batch screening on sample resumes\npython main.py --input ./resumes --output ./output/results.json\n\n# Filter with a minimum CGPA threshold (e.g. 7.5 on 10.0 scale)\npython main.py --input ./resumes --min-cgpa 7.5\n\n# Require verified industry experience and a public GitHub profile link\npython main.py --input ./resumes --require-experience --require-github\n\n# Specify multi-threaded concurrency (default: 5 worker threads)\npython main.py --input ./resumes --concurrency 8 --format json,csv"
    story.append(make_code_box(step5_code, code_style, doc.width))
    story.append(Spacer(1, 6))

    story.append(Paragraph("CLI Arguments Reference:", h2_style))
    cli_args = [
        [Paragraph("Flag", table_header_style), Paragraph("Type", table_header_style), Paragraph("Default", table_header_style), Paragraph("Description", table_header_style)],
        [Paragraph("<code>--input, -i</code>", table_cell_code), Paragraph("string", table_cell_style), Paragraph("<code>./resumes</code>", table_cell_code), Paragraph("Path to directory containing resumes (PDF, DOCX, TXT).", table_cell_style)],
        [Paragraph("<code>--output, -o</code>", table_cell_code), Paragraph("string", table_cell_style), Paragraph("<code>./output/results.json</code>", table_cell_code), Paragraph("Destination path for structured output JSON.", table_cell_style)],
        [Paragraph("<code>--format, -f</code>", table_cell_code), Paragraph("string", table_cell_style), Paragraph("<code>json,csv</code>", table_cell_code), Paragraph("Comma-separated export formats (json, csv).", table_cell_style)],
        [Paragraph("<code>--min-cgpa</code>", table_cell_code), Paragraph("float", table_cell_style), Paragraph("<code>None</code>", table_cell_code), Paragraph("Filter candidates below this CGPA (on 10.0 scale).", table_cell_style)],
        [Paragraph("<code>--require-experience</code>", table_cell_code), Paragraph("flag", table_cell_style), Paragraph("<code>False</code>", table_cell_code), Paragraph("Filter strictly for candidates with related work experience.", table_cell_style)],
        [Paragraph("<code>--require-github</code>", table_cell_code), Paragraph("flag", table_cell_style), Paragraph("<code>False</code>", table_cell_code), Paragraph("Require presence of a public GitHub profile link.", table_cell_style)],
        [Paragraph("<code>--concurrency</code>", table_cell_code), Paragraph("int", table_cell_style), Paragraph("<code>5</code>", table_cell_code), Paragraph("Number of parallel worker threads.", table_cell_style)],
        [Paragraph("<code>--serve</code>", table_cell_code), Paragraph("flag", table_cell_style), Paragraph("<code>False</code>", table_cell_code), Paragraph("Launch FastAPI web server instead of headless CLI.", table_cell_style)],
        [Paragraph("<code>--port</code>", table_cell_code), Paragraph("int", table_cell_style), Paragraph("<code>8000</code>", table_cell_code), Paragraph("HTTP port for web dashboard.", table_cell_style)],
    ]
    cli_table = Table(cli_args, colWidths=[doc.width * 0.28, doc.width * 0.12, doc.width * 0.22, doc.width * 0.38])
    cli_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(cli_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Step 6: Running Automated Tests", h2_style))
    step6_code = "# Run full test suite\npytest -v\n\n# Run tests with output logging\npytest -v -s"
    story.append(make_code_box(step6_code, code_style, doc.width))
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 6: REST API ENDPOINTS
    # ---------------------------------------------------------
    story.append(Paragraph("6. REST API Endpoints Reference", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=8))

    api_endpoints = [
        [Paragraph("Endpoint", table_header_style), Paragraph("Method", table_header_style), Paragraph("Payload / Params", table_header_style), Paragraph("Response & Function", table_header_style)],
        [
            Paragraph("<code>/</code>", table_cell_code),
            Paragraph("GET", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("Serves the single-page web dashboard HTML.", table_cell_style)
        ],
        [
            Paragraph("<code>/health</code>", table_cell_code),
            Paragraph("GET", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("Health check returning service status (healthy).", table_cell_style)
        ],
        [
            Paragraph("<code>/screen</code>", table_cell_code),
            Paragraph("POST", table_cell_style),
            Paragraph("JSON: <code>{input_dir, min_cgpa, require_ai...}</code>", table_cell_code),
            Paragraph("Executes screening on a specified server directory and returns the full screening report.", table_cell_style)
        ],
        [
            Paragraph("<code>/upload_and_screen</code>", table_cell_code),
            Paragraph("POST", table_cell_style),
            Paragraph("Multipart Form: files (up to 100) + filters", table_cell_style),
            Paragraph("Uploads files, runs screening immediately, and saves originals for recruiter preview.", table_cell_style)
        ],
        [
            Paragraph("<code>/results</code>", table_cell_code),
            Paragraph("GET", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("Retrieves the cached screening report from the most recent run.", table_cell_style)
        ],
        [
            Paragraph("<code>/resumes/{file_name}</code>", table_cell_code),
            Paragraph("GET", table_cell_style),
            Paragraph("Path param: resume filename", table_cell_style),
            Paragraph("Direct file access for the built-in PDF iframe modal viewer.", table_cell_style)
        ],
        [
            Paragraph("<code>/export_filtered_excel</code>", table_cell_code),
            Paragraph("POST", table_cell_style),
            Paragraph("JSON: <code>{candidates, filter_label}</code>", table_cell_code),
            Paragraph("Dynamically generates and downloads an Excel spreadsheet for the active shortlist view.", table_cell_style)
        ],
        [
            Paragraph("<code>/export_filtered_docx</code>", table_cell_code),
            Paragraph("POST", table_cell_style),
            Paragraph("JSON: <code>{candidates, filter_label}</code>", table_cell_code),
            Paragraph("Dynamically generates and downloads an executive Word DOCX report for the current view.", table_cell_style)
        ],
    ]

    api_table = Table(api_endpoints, colWidths=[doc.width * 0.25, doc.width * 0.10, doc.width * 0.32, doc.width * 0.33])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('PADDING', (0, 0), (-1, -1), 4.5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 7: DELIVERABLES & EXPORT FORMATS
    # ---------------------------------------------------------
    story.append(Paragraph("7. Structured Deliverables & Export Formats", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Kasparro ensures end-to-end recruiter interoperability by exporting structured screening reports across 4 distinct formats:",
        body_style
    ))

    story.append(Paragraph("&bull; <b>JSON Report (<code>output/results.json</code>):</b> Comprehensive schema containing batch summary statistics, ranked candidates with nested score breakdowns and GitHub metrics, and rejected candidates with explicit disqualification reasons.", bullet_style))
    story.append(Paragraph("&bull; <b>CSV Export (<code>output/results.csv</code>):</b> Flat tabular export containing all candidate fields, contact details, individual rubric sub-scores, and 50-100 word justifications for easy integration into spreadsheets or ATS databases.", bullet_style))
    story.append(Paragraph("&bull; <b>Microsoft Excel (<code>output/results.xlsx</code>):</b> Styled multi-sheet workbook with custom color headers, auto-fit column widths, frozen header panes, and formatted numbers.", bullet_style))
    story.append(Paragraph("&bull; <b>Microsoft Word (<code>output/results.docx</code>):</b> Clean, professionally formatted executive summary document suitable for forwarding directly to hiring engineering managers.", bullet_style))
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # CONCLUSION & REPOSITORY BANNER
    # ---------------------------------------------------------
    story.append(Paragraph("8. Summary & Project Links", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=8))

    conclusion_text = (
        f"The <b>Kasparro Candidate Screening & Ranking System</b> bridges the gap between high-volume hiring and rigorous "
        f"technical evaluation. By combining strict rule-based eligibility checks, automated GitHub code verification, "
        f"a 100-point explainable scoring rubric, and high-speed LLM reasoning, it empowers recruitment teams to shortlist top-tier "
        f"SDE AI talent with speed, consistency, and complete transparency.<br/><br/>"
        f"<b>Source Code & Contributions:</b><br/>"
        f"Explore the source code, open issues, and star the project on GitHub:<br/>"
        f"<font color='#2563eb'><u><a href='{github_url}'>{github_url}</a></u></font>"
    )
    story.append(Paragraph(conclusion_text, body_style))
    story.append(Spacer(1, 10))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")


if __name__ == "__main__":
    build_pdf("Kasparro_Project_Documentation.pdf")
