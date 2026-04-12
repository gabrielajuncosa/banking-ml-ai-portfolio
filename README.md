# Banking AI & Data Science — Teaching Portfolio

A portfolio of hands-on, well-commented notebooks developed for applied teaching
and data science, with a focus on banking and financial services use cases.

Each notebook is self-contained, runs on Google Colab, and is written to serve
two purposes simultaneously: as a working technical example and as a teaching
blueprint that can be adapted for learners at different levels.

---

## Repository Structure

```
├── 01_classical_ml/
│   └── 01_classical_ml_credit_risk.ipynb
│
├── 02_nlp/
│   ├── 02_hugging_face_intro_banking.ipynb
│   └── 03_nlp_text_classification_banking.ipynb
│
├── 03_llm_and_genai/
│   ├── 05_llm_prompting_techniques.ipynb
│   ├── 06_rag_pipeline_banking.ipynb
│   └── 07_agent_architectures_banking.ipynb
│
├── 04_teaching_blueprints/
│   ├── LAB1/
│   ├── LAB3/
│   └── LAB7/
│
├── 05_research_methods/
│   ├── Collaborative-Notes-main/
│   └── YouTube-comments-main/
│
└── README.md
```

---

## Notebooks at a Glance

| # | Notebook | Topic | Key Libraries | Runs Free? |
|---|---|---|---|---|
| 01 | Classical ML — Credit Risk | End-to-end ML pipeline for credit default prediction | pandas, scikit-learn, matplotlib | ✅ Yes |
| 02 | Hugging Face Introduction | Sentiment, NER, summarisation, zero-shot classification | transformers, torch | ✅ Yes |
| 03 | NLP Text Classification | Classifying customer emails with TF-IDF and transformers | scikit-learn, Hugging Face | ✅ Yes |
| 05 | LLM Prompting Techniques | Zero-shot, few-shot, chain-of-thought, structured output | openai | 🔑 API key |
| 06 | RAG Pipeline | Retrieval-augmented generation on a loan policy document | langchain, faiss-cpu, openai | 🔑 API key |
| 07 | Agent Architectures | LangChain agent with tools, memory, banking use case | langchain, openai | 🔑 API key |

---

## Teaching Blueprints (04_teaching_blueprints)

Lab materials developed and delivered to undergraduate and graduate students
across statistics, econometrics, and operations research courses. Each lab
includes exercises, worked examples, and coding components designed around
real-world datasets and problems brought by students from their own workplaces.

| Lab | Topic |
|---|---|
| LAB1 | Introduction to statistical analysis with real data |
| LAB3 | Regression modelling and interpretation |
| LAB7 | Operations research — optimisation problems |

---

## Research Methods (05_research_methods)

Original research projects demonstrating end-to-end data pipeline design,
large-scale data collection, and computational analysis.

| Project | Description |
|---|---|
| **YouTube-comments-main** | End-to-end pipeline for collecting and analysing a 40-million comment dataset to study how toxicity propagates through political conversation flows. Includes API-based data collection, network analysis, and NLP-based toxicity classification. |
| **Collaborative-Notes-main** | Experimental research on collaborative online environments and willingness to express opinions. Includes randomised controlled trial design, oTree experiment infrastructure, and statistical analysis. |

---

## How to Run

### Option A — Google Colab (recommended)
1. Click the notebook you want to open
2. Click the **Open in Colab** badge at the top of the notebook
3. For notebooks marked 🔑, add your `OPENAI_API_KEY` to Colab Secrets:
   - Click the key icon in the left sidebar
   - Add a secret named `OPENAI_API_KEY`
   - Paste your key
4. Run all cells from top to bottom

### Option B — Local (Jupyter)
```bash
git clone https://github.com/gabrielajuncosa/banking-ml-ai-portfolio
cd banking-ml-ai-portfolio
pip install -r requirements.txt
jupyter notebook
```

---

## Requirements

```
# Core data science
pandas
numpy
matplotlib
seaborn
scikit-learn

# NLP and Hugging Face
transformers
torch
huggingface_hub

# LLM and GenAI
openai
langchain
langchain-community
langchain-openai
faiss-cpu

# Utilities
jupyter
```

---

## Notebook Descriptions

### 01 — Classical ML: Credit Risk Prediction
A complete, production-style machine learning pipeline for predicting loan default.
Covers synthetic data generation, exploratory analysis, preprocessing with sklearn
Pipeline (preventing data leakage), training and cross-validating three models
(logistic regression, random forest, gradient boosting), evaluation with ROC-AUC
and confusion matrices, feature importance for interpretability, and threshold
selection as a business decision rather than a statistical one.

**Teaching focus:** Why ROC-AUC matters more than accuracy for imbalanced datasets.
Why data leakage is catastrophic. Why interpretability is a regulatory requirement.

---

### 02 — Hugging Face Introduction
Practical introduction to the Hugging Face ecosystem for banking NLP tasks.
Covers the pipeline API for sentiment analysis, zero-shot classification, named
entity recognition, and summarisation. Also shows the manual tokenizer-model-logits
path so learners understand what the pipeline abstracts. Ends with FinBERT — a
BERT model fine-tuned on financial text — and a comparison with a general model.

**Teaching focus:** The difference between general and domain-specific models.
What a tokenizer does. How to find the right model on the Hub.

---

### 03 — NLP Text Classification
Classical NLP pipeline for classifying customer emails into routing categories.
Covers text preprocessing, TF-IDF vectorisation with n-grams, logistic regression
and random forest classifiers, evaluation with confusion matrices, testing on
unseen inputs, and a direct comparison with a Hugging Face zero-shot classifier.

**Teaching focus:** When to use classical NLP vs transformers. How TF-IDF finds
signal in text. How to build a classifier with no deep learning.

---

### 05 — LLM Prompting Techniques
Systematic demonstration of seven prompting strategies using banking use cases.
Zero-shot, few-shot, chain-of-thought, system prompt design, structured JSON output,
prompt chaining, and prompt comparison. Each technique is demonstrated with a
concrete banking example (complaint classification, loan eligibility, email parsing).

**Teaching focus:** How prompt design controls output quality and consistency.
Why structured output matters for integration. How to evaluate prompt variants.

---

### 06 — RAG Pipeline
End-to-end retrieval-augmented generation pipeline built on a synthetic loan
policy document. Covers document loading and chunking, embedding with OpenAI
and FAISS, retriever configuration, prompt design to prevent hallucination, and
inspection of retrieved chunks for debugging. Includes guidance on what changes
for production deployment.

**Teaching focus:** Why RAG solves the context window limitation. What chunking
strategy does. Why prompts must prevent hallucination in banking contexts.

---

### 07 — Agent Architectures
LangChain agent with three banking tools: a loan repayment calculator, a customer
database lookup, and a policy eligibility checker. Demonstrates the ReAct reasoning
loop with verbose mode so learners can follow every thought-action-observation step.
Adds conversation memory in the second half for multi-turn interactions.

**Teaching focus:** The difference between a chain and an agent. How tool docstrings
guide the agent's decisions. Why audit logging matters for agentic systems in banking.

---

## About

These notebooks were developed as part of a portfolio for applied AI and data science
teaching in the banking sector. Each notebook prioritises clarity, reproducibility,
and direct connection to real banking use cases over technical complexity.

Gabriela Juncosa, PhD
[gabrielajuncosa.github.io](https://gabrielajuncosa.github.io) |
[github.com/gabrielajuncosa](https://github.com/gabrielajuncosa)
