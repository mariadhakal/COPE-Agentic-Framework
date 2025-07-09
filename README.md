# COPE-Agentic-Framework

**Code Performance Evaluation Agentic Framework** - An intelligent, multi-agent system for automated Java performance analysis and optimization recommendations.

##  Overview

COPE is a sophisticated agentic framework that combines AI-powered code analysis with production-grade profiling tools to automatically identify performance bottlenecks in Java applications. It leverages multiple AI models, architecture-specific analyzers, and real-time profiling to provide actionable optimization recommendations.

###  Key Features

- ** Intelligent Agent System**: ReAct-pattern agent with multi-turn reasoning capabilities
- ** Production Profiling**: Java Flight Recorder (JFR) integration for accurate metrics
- ** Architecture-Aware Analysis**: Specialized analyzers for x86_64, ARM64, and CUDA architectures
- ** Automated Tool Orchestration**: Seamless integration of parsing, profiling, and AI analysis
- ** REST API**: FastAPI-based web service with dependency injection
- ** Real-time Metrics**: CPU, memory, and hot method detection

##  Architecture

### System Components

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   AI Agent Layer   │    │   Service Layer     │    │   Core Tools Layer  │
│                     │    │                     │    │                     │
│ • Mistral Codestral │    │ • Parser Service    │    │ • Java Profiler     │
│ • Anthropic Claude  │    │ • Profiler Service  │    │ • Code Parser       │
│ • ReAct Pattern     │    │ • FastAPI Endpoints │    │ • JFR Integration   │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      │
            ┌─────────────────────────▼─────────────────────────┐
            │           Architecture Analysis Layer             │
            │                                                   │
            │ • x86_64 Analyzer  • ARM64 Analyzer  • CUDA GPU  │
            │ • Cache Analysis   • SIMD Optimization           │
            │ • Branch Prediction • Memory Patterns           │
            └───────────────────────────────────────────────────┘
```

### Design Patterns

- ** Layered Architecture**: Clean separation between presentation, service, and core layers
- ** Dependency Injection**: Abstract interfaces with concrete implementations
- ** Agent Pattern**: Intelligent reasoning with tool-calling capabilities
- ** Strategy Pattern**: Pluggable architecture-specific analyzers
- ** Facade Pattern**: Simplified interface for complex tool orchestration


## Installation & Setup

### Prerequisites
- **Python 3.10+**
- **JDK 11+** with JFR tools in PATH
- **Git** for repository access

### 1. Clone Repository
```bash
git clone https://github.com/your-org/COPE-Agentic-Framework.git
cd COPE-Agentic-Framework
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
# or using pyproject.toml
pip install -e .
```

### 3. Environment Configuration

#### GitHub Token Setup (for Mistral Codestral)
1. Create a GitHub developer token: https://github.com/settings/tokens
2. Set environment variable:

**Bash/Linux:**
```bash
export GITHUB_TOKEN="<your-github-token-goes-here>"
```

**PowerShell:**
```powershell
$Env:GITHUB_TOKEN="<your-github-token-goes-here>"
```

**Command Prompt:**
```cmd
set GITHUB_TOKEN=<your-github-token-goes-here>
```

### 4. Verify Installation
```bash
python -c "import src.agent.main_agent.agent as agent; print('COPE installed successfully!')"
```

## Quick Start

### Command Line Interface

#### Single Code Analysis
```bash
# Analyze code from string
python src/agent/main_agent/agent.py --code "public class Example { 
    public static void main(String[] args) { 
        for(int i=0; i<1000; i++) { 
            System.out.println(i); 
        } 
    } 
}"

# Analyze code from file
python src/agent/main_agent/agent.py --file path/to/YourClass.java

# Custom analysis duration
python src/agent/main_agent/agent.py --file Example.java --max-turns 15
```

#### Web API Service
```bash
# Start FastAPI server
cd src/agent
uvicorn main:app --reload --port 8000

# API endpoints will be available at:
# POST http://localhost:8000/api/v1/parse
# POST http://localhost:8000/api/v1/profile
```

### Python API Usage

```python
from src.agent.main_agent.agent import query

# Analyze Java code
java_code = """
public class PerformanceExample {
    public static void main(String[] args) {
        // Inefficient string concatenation
        String result = "";
        for (int i = 0; i < 10000; i++) {
            result += "a";
        }
        
        // Linear search in array
        int[] numbers = new int[100000];
        for (int i = 0; i < numbers.length; i++) {
            if (numbers[i] == 99999) break;
        }
    }
}
"""

# Run analysis
analysis_result = query(java_code, max_turns=10)
print(analysis_result)
```

## Features Deep Dive

### Intelligent Agent System

The core agent uses a **ReAct (Reasoning + Acting)** pattern:

1. **Thought**: Analyzes the code structure and identifies potential issues
2. **Action**: Executes tools (parser, profiler) to gather data
3. **Observation**: Processes tool outputs and metrics
4. **Reasoning**: Synthesizes findings into actionable recommendations

**Available Tools:**
- `java_code_parser`: AST generation and structural analysis
- `java_profiler`: JFR-based runtime profiling with hot method detection

### Performance Profiling

**Java Flight Recorder Integration:**
- Low-overhead production profiling
- CPU utilization tracking
- Memory allocation patterns
- Garbage collection analysis
- Hot method identification

**Metrics Collected:**
```json
{
  "cpu": "CPU load and thread utilization",
  "memory": "Allocation rates and GC events", 
  "hot_methods": ["Method1", "Method2", "Method3"],
  "summary": "Overall execution statistics",
  "file_size_bytes": 1024000
}
```

### Architecture-Specific Analysis

#### x86_64 Analyzer
- **Cache Hierarchy**: L1 (32KB, 4 cycles), L2 (256KB, 12 cycles), L3 (16MB, 40 cycles)
- **SIMD Extensions**: SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, AVX, AVX2
- **Branch Prediction**: 15-20 cycle misprediction penalty

#### ARM64 Analyzer
- **Cache Levels**: L1 (64KB, 4 cycles), L2 (512KB, 11 cycles), L3 (4MB, 30 cycles)
- **SIMD**: NEON, SVE, SVE2 optimizations
- **Lower Branch Penalty**: 10-15 cycles

#### CUDA Analyzer (Experimental)
- GPU-specific optimization patterns
- Memory coalescing analysis
- Kernel launch optimization

## Analysis Output

### Performance Report Structure

```json
{
  "bottlenecks_identified": [
    {
      "type": "String Concatenation in Loop",
      "severity": "HIGH",
      "location": "Line 45-52",
      "impact": "O(n²) complexity causing excessive memory allocation"
    }
  ],
  "optimization_recommendations": [
    {
      "issue": "StringBuilder Usage",
      "solution": "Replace String += with StringBuilder.append()",
      "expected_improvement": "90% performance gain",
      "code_example": "StringBuilder sb = new StringBuilder();"
    }
  ],
  "architecture_analysis": {
    "cache_behavior": "Poor locality due to scattered memory access",
    "simd_opportunities": "Array operations could benefit from vectorization",
    "branch_prediction": "Predictable patterns, minimal impact"
  },
  "metrics": {
    "execution_time": "1250ms",
    "memory_usage": "450MB peak",
    "hot_methods": ["stringConcatenation", "linearSearch"]
  }
}
```

## Advanced Usage

### Custom Architecture Analyzers

```python
from src.architectures.architecture_registry import ArchitectureRegistry

class CustomArchAnalyzer:
    ARCHITECTURE_NAME = "custom_arch"
    
    @staticmethod
    def analyze_performance(code, ast, call_graph=None, dataflow=None):
        # Custom analysis logic
        return {"custom_metrics": "..."}

# Register automatically via auto-discovery
ArchitectureRegistry.auto_discover()
```

### Extending Tool Capabilities

```python
# Add new tools to the agent
def custom_analysis_tool(input_data):
    # Custom analysis logic
    return analysis_results

# Register in known_actions
known_actions["custom_tool"] = custom_analysis_tool
```

### Batch Processing

```python
import csv
from src.agent.main_agent.agent import query

# Process multiple files
with open('java_samples.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(f"Analyzing {row['name']}...")
        result = query(row['code'])
        # Save results
```

## Dataset Sources

### Primary Dataset
- **University of Texas CS307**: [Java Coding Samples](https://www.cs.utexas.edu/~scottm/cs307/codingSamples.htm)
- **Collection Script**: `get_data.py` automatically downloads and processes samples

### Dataset Format
```csv
name,url,code
"ArrayExample.java","https://...","public class ArrayExample { ... }"
"LoopOptimization.java","https://...","public class LoopOptimization { ... }"
```

### Custom Dataset Integration
```python
# Use your own dataset
python src/agent/main_agent/agent.py --file your_dataset.csv
```

## Troubleshooting

### Common Issues

#### JFR Not Found
```bash
# Ensure JDK 11+ is installed and JFR tools are in PATH
java -XX:+FlightRecorder -version
jfr --help
```

#### GitHub Token Issues
```bash
# Verify token is set
echo $GITHUB_TOKEN  # Linux/Mac
echo $Env:GITHUB_TOKEN  # PowerShell
```

#### Import Errors
```bash
# Ensure project is installed in development mode
pip install -e .
# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/COPE-Agentic-Framework"
```

#### Memory Issues with Large Code
- Reduce analysis duration: `--max-turns 5`
- Use smaller code samples for testing
- Increase JVM heap size: `-Xmx4g`

### Debug Mode
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

from src.agent.main_agent.agent import query
result = query(code, max_turns=5)
```

## Contributing

### Development Setup
```bash
git clone https://github.com/your-org/COPE-Agentic-Framework.git
cd COPE-Agentic-Framework
pip install -e ".[dev]"
pre-commit install
```

### Adding New Architecture Analyzers
1. Create new file in `src/architectures/`
2. Implement `ARCHITECTURE_NAME` class attribute
3. Add `analyze_performance` static method
4. Auto-discovery will register automatically

### Extending Agent Capabilities
1. Add new tools in `agent.py`
2. Update `known_actions` dictionary
3. Enhance prompts for new capabilities
4. Add comprehensive testing

### Code Standards
- **Type Hints**: Use throughout codebase
- **Docstrings**: Google style documentation
- **Testing**: pytest with >80% coverage
- **Linting**: black, flake8, mypy

## Research & References

### Academic Background
- **Performance Analysis**: Static and dynamic analysis techniques
- **Agent-Based Systems**: ReAct pattern and tool-calling architectures
- **Architecture Optimization**: Platform-specific performance characteristics

### Related Projects
- **Java Performance**: JProfiler, VisualVM, Java Mission Control
- **Code Analysis**: SpotBugs, PMD, SonarQube
- **AI Agents**: LangChain, AutoGPT, CrewAI

### Publications
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Java Flight Recorder: An In-Depth Guide](https://docs.oracle.com/javacomponents/jmc-5-4/jfr-runtime-guide/about.htm)

## Acknowledgments

- **Oracle**: Java Flight Recorder technology
- **Mistral AI**: Codestral language model
- **Anthropic**: Claude for architecture analysis
- **University of Texas**: CS307 dataset
- **javalang**: Python Java parsing library

