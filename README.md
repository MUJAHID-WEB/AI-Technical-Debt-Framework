# 🤖 AI Technical Debt Management Framework

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)
[![Research](https://img.shields.io/badge/Research-AI%20Technical%20Debt-purple)]()

A comprehensive framework for detecting, measuring, and visualizing hidden architectural problems in AI-enabled microservice systems. This research project introduces the **Model Entanglement Score (MES)** - a novel metric to quantify how tightly AI services are coupled to core business logic.

## 📋 Table of Contents
- [Overview](#-overview)
- [The Core Problem](#-the-core-problem)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [The 6-Tier Framework](#-the-6-tier-framework)
- [Model Entanglement Score (MES)](#-model-entanglement-score-mes)
- [API Reference](#-api-reference)
- [Research Validation](#-research-validation)
- [Contributing](#-contributing)
- [License](#-license)
- [Citation](#-citation)

## 🎯 Overview

When we integrate AI components into microservice systems, they introduce a new, sticky kind of technical debt. Unlike traditional code debt, AI debt includes:

- **Hidden feedback loops** where models influence their own training data
- **Explosive glue code** connecting components
- **Undeclared consumers** silently depending on models
- **Data dependencies** that can break systems without any code changes

Traditional architectural metrics like coupling and cohesion completely fail to capture this "entanglement" caused by AI models. This framework provides a systematic way to detect, measure, and visualize these hidden problems.

## 🔍 The Core Problem

Traditional technical debt metrics measure code relationships, but not:
- Data dependencies between services and models
- Model versioning and update cascades
- Feedback loops where model outputs influence training data
- Implicit coupling through shared feature pipelines

**Our research hypothesis**: AI-enabled systems degrade in maintainability **3 times faster** than traditional systems, unless specific isolation layer patterns are applied.

## ✨ Key Features

- **Universal Project Support**: Works with any project type (microservices, web apps, ML projects, data pipelines)
- **Multi-Language Detection**: Supports 20+ programming languages and frameworks
- **6-Tier Analysis Pipeline**: Comprehensive analysis from data collection to hypothesis validation
- **Model Entanglement Score (MES)**: Novel metric (0-10) quantifying AI architecture debt
- **Real-time Analysis**: Watch each tier process your project with live updates
- **Multiple Collection Methods**:
  - Local ZIP/TAR.GZ upload
  - GitHub repository cloning
  - MLOps platform integration (Kubeflow, MLflow, BentoML, Seldon Core)
- **Professional PDF Reports**: Generate comprehensive architectural analysis reports
- **Research Validation Tools**: Statistical validation of the 3x degradation hypothesis

## 🏗 Architecture

```bash
ai-debt-framework/
├── app.py # Main Flask application
├── requirements.txt # Dependencies
├── static/
│ ├── css/
│ │ └── style.css # Styles
│ └── js/
│ ├── main.js # Core functionality
│ └── charts.js # Visualization
├── templates/
│ ├── base.html # Base template
│ ├── index.html # Upload page
│ └── analysis.html # Results page
├── collectors/
│ ├── github_collector.py # GitHub integration
│ ├── local_scanner.py # Local/ZIP scanning
│ └── mlops_collector.py # MLOps platforms
├── analyzers/
│ ├── tier1_collector.py # Universal data collection
│ ├── tier2_analyzer.py # System analysis
│ ├── tier3_smell_detector.py # AI smell detection
│ ├── tier4_metrics.py # MES computation
│ ├── tier5_maintainability.py # Maintainability analysis
│ └── tier6_validator.py # Hypothesis validation
├── detectors/
│ ├── language_detector.py # Language detection
│ ├── framework_detector.py # Framework detection
│ └── model_detector.py # Model detection
├── utils/
│ ├── git_utils.py # Git analysis
│ ├── file_utils.py # File operations
│ └── report_generator.py # PDF generation
└── uploads/ # Temporary storage

```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- git (optional, for GitHub integration)

### Option 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-debt-framework.git
cd ai-debt-framework

# Run the installation script
# On Linux/Mac:
chmod +x install.sh
./install.sh

# On Windows:
install.bat

```

### Option 2: Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```
### Option 3: Docker Installation

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build standalone image
docker build -t aidebt-framework .
docker run -p 5000:5000 aidebt-framework

# Create necessary directories
mkdir -p uploads results reports

```

### 🚀 Quick Start
## 1. Start the application:

```bash
python app.py

```
## 2. Open your browser:

```bash
http://localhost:5000
```

## 3. Upload a project:

### Choose from three methods:

- Local Upload: Drag & drop a ZIP file

- GitHub: Enter a repository URL

- MLOps: Connect to Kubeflow, MLflow, etc.

## 4. Watch the analysis:

- Real-time progress bar shows each tier

- Live output displays findings

- Tier status indicators show progress

## 5. View results:

- Model Entanglement Score (0-10)

- Detailed tier-by-tier analysis

- Actionable recommendations

- Download PDF report
