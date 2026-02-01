# Insurance Claim Processing Pipeline

An automated insurance claim processing system that analyzes claim submissions with supporting documents and makes intelligent coverage decisions using AI-powered document analysis, fraud detection and policy reasoning.

## Overview

This system processes insurance claims by:
- Accepting claim descriptions with supporting documents (images, medical certificates, receipts, etc.)
- Extracting and analyzing text from documents using OCR and LLMs
- Detecting potential fraud indicators
- Evaluating claims against policy terms and coverage rules
- Making automated decisions: **APPROVED**, **DENIED**, or **UNCERTAIN**
- Providing detailed reasoning for each decision


## Features

- **RESTful API** built with FastAPI
- **Multi-format document support**: Images (.png, .jpg, .jpeg, .webp), text files (.txt, .md)
- **OCR capabilities** using PaddleOCR for text extraction from images
- **AI-powered analysis** using local LLM models via Ollama
- **In-memory storage** for claim records and documents (should be replaced with database storage in production)
- **Evaluation** scripts for benchmarking

## Architecture

The system uses a pipeline with specialized AI-powered steps:
1. **Policy Section Identifier**: Identifies relevant policy sections ans rules out out-of-scope claims
2. **Document Processor**: Extracts text from images and documents using OCR
3. **Document Analyzer**: Analyzes extracted text for key information
4. **Fraud Detector**: Checks for suspicious patterns
5. **Policy Reasoner**: Evaluates claims against policy terms

Each step processes the output from a previous step, building up context until a final decision is made.

Please check [SOLUTION.md](SOLUTION.md) for a full solution description and reasoning behind architectural decisions.

## Prerequisites

Before setting up the project, ensure you have the following installed:

### Required Software

1. **Python 3.11 or 3.12**
   ```bash
   python3 --version  # Should show 3.11.x or 3.12.x
   ```

2. **PDM (Python Dependency Manager)**
   ```bash
   # Install via pip
   pip install pdm
   
   # Or via Homebrew (macOS)
   brew install pdm
   ```

3. **Ollama** (for running local LLM models)
   ```bash
   # macOS
   brew install ollama
   
   # Or download from https://ollama.ai
   ```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd automated-claims-processing
```

### 2. Install Dependencies

```bash
pdm install
```
**Note**: The first time you run the application, PaddleOCR will download its models automatically. This may take a few minutes.

### 3. Set Up Ollama Models

Start the Ollama service and pull the required models:

```bash
# Start Ollama (if not already running)
ollama serve

# In a new terminal, pull the required models
ollama pull qwen3:8b
ollama pull qwen2.5vl:7b-q4_K_M
```

**Note**: The download may take some time depending on your internet connection.

### 4. Configure Environment Variables

Copy the example environment file and customize if needed:

```bash
cp .env.example .env
```

Default configuration:
```
API_HOST=localhost
API_PORT=8000
LOG_LEVEL=INFO
```

### 5. Start the Application

```bash
pdm run app
```

The API will be available at `http://localhost:8000`

**Note**: The first startup may take 1-2 minutes as PaddleOCR loads its models into memory.

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs

### Endpoints

#### 1. Submit a Claim

**POST** `/claims/`

Submit a new insurance claim with supporting documents.

**Request**:
- `description` (form field, required): Text description of the incident
- `metadata` (form field, optional): Additional metadata (dates, names, etc.)
- `files` (file upload, optional): Supporting documents

**Supported file types**: `.md`, `.txt`, `.png`, `.jpg`, `.jpeg`, `.webp`

**Example using curl**:
```bash
curl -X POST "http://localhost:8000/claims/" \
  -F "description=I had a medical emergency during my trip to Spain" \
  -F "metadata=Date: 2024-01-15, Location: Madrid" \
  -F "files=@medical_certificate.jpg" \
  -F "files=@receipt.png"
```

**Response**:
```json
{
  "claim_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processed",
  "message": "Claim processed successfully",
  "decision": "APPROVED",
  "explanation": "The claim meets all policy requirements..."
}
```

#### 2. Get Claim Details

**GET** `/claims/{claim_id}`

Retrieve details of a specific claim.

**Example**:
```bash
curl "http://localhost:8000/claims/550e8400-e29b-41d4-a716-446655440000"
```

**Response**:
```json
{
  "claim_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processed",
  "created_at": "2024-01-31T10:30:00",
  "description": "Medical emergency in Spain",
  "metadata": "Date: 2024-01-15",
  "documents": ["path/to/doc1.jpg", "path/to/doc2.png"],
  "decision": "APPROVED",
  "explanation": "Detailed reasoning..."
}
```

#### 3. List All Claims

**GET** `/claims/`

Retrieve a list of all processed claims.

**Example**:
```bash
curl "http://localhost:8000/claims/"
```

**Response**: Array of claim objects

## Running Evaluations

The project includes evaluation tools to test the pipeline against benchmark datasets:

```bash
# Run full evaluation on all test claims
pdm run evaluation

# Generate summary statistics (requires evaluation to run first)
pdm run summarize-results

# Generate detailed evaluation report (requires evaluation to run first)
pdm run evaluation-report
```

Results are saved in the `results/` directory.

For a detailed analysis of the pipeline's performance and evaluation results, see [RESULTS.md](RESULTS.md).

## Project Structure

```
automated-claims-processing/
├── src/claim_processing_pipeline/
│   ├── api/              # API endpoints and models
│   ├── experts/          # Specialized steps
│   ├── pipeline.py       # Main processing pipeline
│   ├── prompts.py        # LLM prompts
|   ├── schemas.py        # Pydantic models
|   ├── constants.py      
|   ├── utils.py          
|   ├── config.py         # Application settings
│   └── main.py           # Application entry point
├── data/
│   ├── claims/           # Test claim data
│   └── policy.md         # Insurance policy document
├── evaluation/           # Evaluation scripts
├── results/              # Evaluation results
└── in-memory-storage/    # Processed claims storage  (created when API is used)
```

## Troubleshooting

### Ollama Connection Issues
If you see connection errors to Ollama:
```bash
# Ensure Ollama is running
ollama serve

# Verify models are installed
ollama list
```

### PaddleOCR Model Loading
The first run downloads OCR models automatically. If you experience issues:
- Ensure you have a stable internet connection
- Check available disk space (models require ~500MB)
- The models are cached in `~/.paddleocr/`
