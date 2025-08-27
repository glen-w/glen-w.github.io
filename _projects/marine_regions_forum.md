---
layout: page
title: Marine Regions Forum
description: All-in-one audio transcription & analysis
img: /assets/img/projects/thumbs/marine_regions_forum_logo.png
importance: 2
category: past work
---


<div align="center">
  <img src="/assets/img/projects/thumbs/marine_regions_forum_logo.png" alt="TranscriptX Logo" width="200"/>
</div>

## Overview

TranscriptX is a comprehensive, modular toolkit for analyzing transcripts with advanced NLP capabilities including sentiment analysis, emotion detection, named entity recognition, and more. Built with a web-native architecture for modern deployment and accessibility.

## Features

- 🎯 **Modular Architecture**: Plug-and-play analysis components
- 🧠 **Advanced NLP**: Sentiment analysis, emotion detection, NER
- 🔍 **Semantic Similarity**: Dual-method repetition detection (simple keyword-based and advanced analysis-integrated)
- 📊 **Visual Analytics**: Interactive charts and word clouds (matplotlib + upcoming Plotly integration)
- 🌍 **Geographic Analysis**: Location-based insights
- 🎙️ **Speaker Identification**: Multi-speaker transcript support with cross-session tracking
- 📈 **Statistical Analysis**: Comprehensive metrics and reporting
- 🌐 **Web-Native Interface**: Modern web viewer for results
- 🖥️ **CLI Interface**: Interactive command-line tool for batch processing (with colored output powered by [rich](https://github.com/Textualize/rich))
- 📦 **Zip Export**: Automatic creation of zip files containing all analysis results
- 🛡️ **Robust Error Handling**: Graceful degradation and comprehensive error reporting
- 🗄️ **Database Backend**: Persistent speaker profiles and cross-session analysis
- 🐳 **Docker Support**: Complete containerized environment for dependency-free deployment

## Quick Start

### 🐳 Docker (Recommended - Solves All Dependency Issues)

#### Quick Start with Docker
```bash
# Complete Docker setup (recommended)
./scripts/docker-setup.sh
./scripts/docker-data-setup.sh

# Start full environment (all services)
./scripts/docker-full.sh

# Or start individual services
./scripts/docker-dev.sh    # Development environment
./scripts/docker-web.sh    # Web viewer
./scripts/docker-docs.sh   # Documentation server
./scripts/docker-test.sh   # Run tests
```

#### Docker Services Available
- **Development Environment** (port 8000): Full development container with interactive shell
- **Web Viewer** (port 8001): Results viewing interface
- **Documentation Server** (port 8003): Sphinx documentation with API docs
- **Test Environment**: Automated testing with coverage
- **Production Environment** (port 8002): Optimized deployment

**📖 [Complete Docker Documentation](docs/DOCKER_README.md)**

### For Users (Local Installation)
```bash
# Interactive setup with virtual environment
./scripts/setup_env.sh

# Quick activation (after setup)
./activate_env.sh

# One-command setup and run
./transcriptx.sh
```

### For Developers (Local Installation)
```bash
# Development setup with virtual environment
./scripts/setup_env.sh  # Choose option 4 for development
# OR
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
pytest  # Run tests
```

### Basic Usage

```bash
# Start the interactive CLI
./transcriptx.sh

# Or use direct commands
./transcriptx.sh analyze transcript.json --modules sentiment,emotion

# Run semantic similarity analysis (simple method)
./transcriptx.sh analyze transcript.json --modules semantic_similarity

# Run advanced semantic similarity with analysis integration
./transcriptx.sh analyze transcript.json --modules semantic_similarity_advanced

# Create a zip file of all outputs
./transcriptx.sh create-zip transcript.json

# Start the web viewer (separate lightweight installation)
python src/transcriptx/web_viewer.py --dir /path/to/transcripts

# Get help
./transcriptx.sh --help
```

## Project Structure

```
transcriptx/
├── README.md                    # Main project documentation
├── src/transcriptx/             # Core package (91 Python files)
│   ├── cli/                    # Command-line interface
│   ├── core/                   # Core analysis modules
│   ├── database/               # Database operations and speaker profiling
│   ├── web_viewer/             # Web interface
│   └── utils/                  # Utility functions
├── frontend/                   # React frontend
├── tests/                      # Comprehensive test suite (56 test files)
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
└── assets/                     # Project assets
```

## Documentation

### 📚 Main Documentation
- **[README.md](README.md)** - This file - Primary project overview
- **[docs/](docs/)** - Sphinx-generated documentation with API reference

### 🔧 Development Documentation
- **[Project Organization](docs/development/README_ORGANIZED.md)** - Detailed project structure and cleanup
- **[Developer Guide](docs/development/DEVELOPER_GUIDE.md)** - Development setup and guidelines
- **[Consistency Standards](docs/development/CONSISTENCY_STANDARDS_SUMMARY.md)** - Code quality standards
- **[Output Standards](docs/development/OUTPUT_STANDARDS_SUMMARY.md)** - Analysis output formats
- **[Error Handling](docs/development/ERROR_HANDLING_STANDARDS.md)** - Error handling and reliability
- **[Database Backend](docs/development/DATABASE_BACKEND_README.md)** - Database architecture
- **[Topic Modeling](docs/development/TOPIC_MODELING_ANALYSIS.md)** - Topic modeling implementation
- **[Batch Analysis](docs/development/BATCH_ANALYSIS_GUIDE.md)** - Batch processing guide

## Testing & Coverage

TranscriptX includes a comprehensive test suite covering:
- **Error Logging**: All error/exception cases are logged and asserted in tests
- **Input Validation**: Extensive tests for invalid, edge, and boundary inputs
- **Graceful Exit**: All CLI and process entry points are tested for KeyboardInterrupt and clean exit
- **Progress Feedback**: Long-running processes are tested for regular user feedback and percent complete
- **Robustness**: Negative tests for corrupt/missing files, bad configs, and user-facing error messages

### Running Tests

```bash
# Run all tests (recommended - uses virtual environment)
./scripts/run_tests.sh

# Run with coverage
./scripts/run_tests.sh --cov=src --cov-report=term-missing

# Run specific test file
./scripts/run_tests.sh tests/unit/test_config.py

# Alternative: Run tests directly (requires virtual environment to be activated)
source .transcriptx/bin/activate
pytest
```

All tests are located in `tests/` and its subdirectories.

**Note:** The `run_tests.sh` script automatically activates the virtual environment to ensure consistent dependency versions. This prevents issues with missing or mismatched packages.

## Error Handling & Reliability

TranscriptX implements comprehensive error handling standards to ensure robust operation across diverse environments and input conditions. **All error handling, input validation, and robustness features are fully covered by automated tests.**

### 🛡️ Error Handling Standards

#### **Centralized Logging System**
- **Standardized Error Logging**: All errors are logged through `transcriptx.core.logger.log_error()`
- **Module Context**: Errors include module name and operation context
- **Exception Tracking**: Full stack traces preserved for debugging
- **Structured Format**: `[MODULE] Error message | Context: additional_info`

#### **Input Validation & Sanitization**
- **Comprehensive Validation**: All inputs validated before processing
- **Graceful Degradation**: Invalid inputs handled without crashing
- **User-Friendly Messages**: Clear error messages for common issues
- **File Format Support**: Robust handling of various transcript formats

#### **DAG Pipeline Resilience**
- **Module Isolation**: Individual module failures don't affect others
- **Timeout Protection**: Long-running operations have configurable timeouts
- **Resource Management**: Proper cleanup of system resources
- **Error Aggregation**: Comprehensive error reporting across modules

### 🔧 Error Recovery Mechanisms

#### **Automatic Retry Logic**
```python
# Example: File operations with retry
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    log_error("IO", f"Failed to load {file_path}: {e}")
    # Fallback to default data or skip operation
```

#### **Graceful Degradation**
- **Missing Dependencies**: Modules continue with reduced functionality
- **Large Files**: Memory-efficient processing for large transcripts
- **Network Issues**: Offline operation when external services unavailable
- **Resource Limits**: Automatic resource management and cleanup

### 🚀 Best Practices for Users

#### **Handling Common Errors**

**File Not Found**
```bash
# Check file path and permissions
ls -la transcript.json
# Ensure file is in correct format
file transcript.json
```

**Memory Issues**
```bash
# Use smaller batch sizes
transcriptx analyze transcript.json --modules sentiment --batch-size 100
# Process in chunks for large files
transcriptx analyze transcript.json --modules emotion --chunk-size 50
```

**Missing Dependencies**
```bash
# Install required packages
pip install -r requirements.txt
# For specific modules
pip install nltk textblob transformers
```

**Timeout Issues**
```bash
# Increase timeout for complex analysis
transcriptx analyze transcript.json --timeout 600
# Use DAG pipeline for optimal results
```

## Semantic Similarity Analysis

TranscriptX offers two semantic similarity analysis methods:

**Simple Method (`semantic_similarity`)**: 
- Fast keyword-based analysis
- Suitable for quick repetition detection
- Lower computational requirements

**Advanced Method (`semantic_similarity_advanced`)**:
- Integrates with existing analysis modules (sentiment, emotion, acts, etc.)
- Quality-based segment filtering
- Configurable profiles for different conversation types
- Enhanced repetition detection with context awareness

Configure the method and profiles through the interactive CLI or config file:

```bash
# Configure semantic similarity settings
transcriptx config --show

# Run with specific method
transcriptx analyze transcript.json --modules semantic_similarity_advanced
```

## Database Backend & Speaker Profiling

TranscriptX includes a comprehensive database backend for persistent speaker profiling and cross-session analysis:

### Features
- **Persistent Speaker Profiles**: Speaker data persists across sessions
- **Cross-Session Tracking**: Link speakers across different conversations
- **Behavioral Fingerprinting**: Unique behavioral patterns for speaker identification
- **Profile Evolution**: Automatic profile updates with new data
- **Confidence Scoring**: Measure reliability of behavioral analysis

### Usage
```bash
# Initialize database
transcriptx db init

# View speaker profiles
transcriptx profiles list

# Compare speakers
transcriptx profiles compare speaker1 speaker2

# Export profile data
transcriptx profiles export --format json
```

## Output Management

TranscriptX automatically creates zip files when all requested modules complete successfully:

```bash
# Analyze with automatic zip creation
transcriptx analyze transcript.json --modules sentiment,emotion,ner

# Manual zip creation from existing outputs
transcriptx create-zip transcript.json

# Force zip creation even if some modules failed
transcriptx create-zip transcript.json --force

# Create zip from output directory
transcriptx create-zip /path/to/outputs/
```

Zip files include:
- All analysis outputs organized by module
- Validation report for missing modules
- README with usage instructions
- Comprehensive summary files

## Web Viewer (Lightweight)

For just the web viewer without heavy ML dependencies:

```bash
# Install lightweight requirements
pip install -r requirements-web.txt

# Start web viewer
python src/transcriptx/web_viewer.py --dir /Users/89298/Desktop/meetings
```

## Transcript Simplification

TranscriptX now supports transcript simplification for TTS and summary purposes. This feature removes tics, hesitations, repetitions, and agreement phrases, focusing on substantive content and decision points while maintaining conversational flow.

### Usage

```bash
python -m transcriptx.cli.main simplify-transcript INPUT.json OUTPUT.json
```

- `INPUT.json`: Path to the input transcript (list of dicts with 'speaker' and 'text')
- `OUTPUT.json`: Path to write the simplified transcript
- Optional: `--tics-file` and `--agreements-file` to provide custom lists (JSON arrays)

### Example

Input:
```json
[
  {"speaker": "Alice", "text": "Um, I think we should start."},
  {"speaker": "Bob", "text": "Yeah, I agree."},
  {"speaker": "Alice", "text": "Let's review the agenda."},
  {"speaker": "Bob", "text": "Let's review the agenda."},
  {"speaker": "Alice", "text": "You know, the main point is the launch."}
]
```

Output:
```json
[
  {"speaker": "Alice", "text": "I think we should start."},
  {"speaker": "Alice", "text": "Let's review the agenda."},
  {"speaker": "Alice", "text": "the main point is the launch."}
]
```

## Known Issues

### Matplotlib Transform Corruption in Chart Generation

**Issue**: Some analysis modules (particularly topic modeling) may fail to generate charts due to a matplotlib transform corruption error:

```
TypeError: can't multiply sequence by non-int of type 'numpy.float64'
```

**Root Cause**: This is a known matplotlib bug where the figure's DPI scale transform matrix (`self._mtx[0, 0]`) becomes corrupted and contains a sequence instead of a numeric value. This corruption occurs in matplotlib's internal transform system during the `fig.savefig()` call.

**Affected Modules**: 
- Topic modeling (LDA/NMF heatmaps and speaker charts)
- Potentially other modules that generate matplotlib charts

**Current Workaround**: 
- Chart generation is gracefully skipped with informative logging
- All analysis data (JSON files, topic distributions, etc.) is still saved successfully
- The analysis completes without interruption

**Status**: 
- ✅ **Analysis functionality**: Fully working
- ✅ **Data output**: All JSON and analysis results saved
- ⚠️ **Chart generation**: Skipped due to matplotlib corruption
- 🔧 **Investigation ongoing**: Exploring alternative charting libraries and matplotlib workarounds

### NumPy Version Conflicts

**Issue**: Some ML dependencies have NumPy version conflicts that can cause import errors.

**Solution**: Use Docker environment which pins NumPy to <2.0, or manually install compatible versions.

**Status**:
- ✅ **Docker environment**: Fully resolved with pinned dependencies
- ⚠️ **Local environment**: May require manual dependency management

## Roadmap Highlights

### Current Version (v0.2.0)
- **Database Backend**: Complete speaker profiling and cross-session tracking
- **Docker Support**: Full containerization with dependency resolution
- **Enhanced Error Handling**: Comprehensive error handling and recovery
- **Cross-Session Analysis**: Advanced speaker tracking across multiple conversations

### Upcoming Features (v0.3.0)
- **Plotly Chart Integration**: Interactive charts alongside matplotlib (3-4 hours development)
- **Enhanced Web Interface**: Improved user experience and interactivity
- **Additional Output Formats**: CSV, JSONL, DOCX support
- **Advanced Speaker Analytics**: Machine learning-based speaker analysis

### Web-Native Focus
TranscriptX is designed as a web-native application, prioritizing:
- **Cross-platform accessibility** through web browsers
- **Modern deployment** via containers and cloud platforms
- **Scalable architecture** for enterprise integration
- **Interactive visualizations** with Plotly and modern web technologies

## Contributing

We welcome contributions! Please see our [Developer Guide](docs/development/DEVELOPER_GUIDE.md) for setup instructions and contribution guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://transcriptx.readthedocs.io)
- 🐛 [Issues](https://github.com/yourusername/transcriptx/issues)
- 💬 [Discussions](https://github.com/yourusername/transcriptx/discussions)

---

<div align="center">
  <em>Built with ❤️ by the TranscriptX Team</em>
</div>
