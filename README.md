# COPE-Agentic-Framework
Code Performance Evaluation agentic framework, a framework to analyze the bottleneck for code optimization

This tool provides automated performance bottleneck diagnosis for Java code. It analyzes Java source code, identifies performance issues, and suggests optimizations.

## Components
The system consists of three main components:

### 1. Agent (agent.py)
The core bottleneck diagnosis agent that uses Mistral AI to analyze Java code.
### 2. Java Profiler (java_profiler.py)
A tool that compiles, runs, and profiles Java code using JFR.
### 3. Batch Analyzer (batch_analyzer.py) 
A script to analyze multiple code samples from a CSV file.

## Usage
### Single Code Analysis
To analyze a single Java code sample:
> python agent.py --code "public class MyClass { ... }"

Or from a file:
> python agent.py --file path/to/MyClass.java
 
## Batch Analysis
To analyze multiple code samples from a CSV file:
> python batch_analyzer.py samples.csv --output-dir results
 
The CSV file format:
> id,class_name,description,code
sample1,MyClass1,"Description","public class MyClass1 { ... }"
sample2,MyClass2,"Description","public class MyClass2 { ... }"

## Profiling Tools for Java and Python
java_profiler.py -> JFR \
This script will:
- Take Java code as input
- Save it to a file
- Compile it
- Run it with JFR enabled
- Generate a basic analysis of the JFR recording

To use the script independently:
* Method 1: Provide code directly:
> python java_profiler.py --code "public class HelloWorld { public static void main(String[] args) { System.out.println(\"Hello World!\"); } }" --class-name HelloWorld --duration 5
* Method 2: From a Java file:
> python java_profiler.py --file HelloWorld.java --class-name HelloWorld --duration 5
* Method 3: With automatic JMC opening:
> python java_profiler.py --file HelloWorld.java --class-name HelloWorld --open-jmc

### Note:
The script requires Python 3.6+ and a JDK 11+ installation with JFR tools in your PATH \
For complex Java applications, you might need to adjust the classpath and JVM arguments \
The basic metrics extraction provides a simple overview - for detailed analysis, use the JMC GUI that can be launched with the --open-jmc flag


https://www.ej-technologies.com/jprofiler

## Parser

We use javalang to parse java code. It is a python based java parser which makes it easier to use.

       pip install javalang
https://www.baeldung.com/javaparser
https://javaparser.org/

Python http://github.com/dabeaz/ply

Python: ast tree library: https://docs.python.org/3/library/ast.html

## LLM Agent
We are using codestral as our llm agent, from github models
1. Create a gthub developer token: https://github.com/settings/tokens
2. If you are using bash: 

    export GITHUB_TOKEN="<your-github-token-goes-here>"
    
    If you're in powershell:

    $Env:GITHUB_TOKEN="<your-github-token-goes-here>"
    If you're using Windows command prompt:
    
    set GITHUB_TOKEN=<your-github-token-goes-here>

3. Install dependencies

   Install Mistral SDK using pip (Requires: Python >=3.9):

       pip install mistralai>=1.0.0