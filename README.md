# COPE-Agentic-Framework
Code Performance Evaluation agentic framework, a framework to analyze the bottleneck for code optimization


# Profiling Tools for Java and Python

https://www.ej-technologies.com/jprofiler

# Parser
https://www.baeldung.com/javaparser
https://javaparser.org/

Python http://github.com/dabeaz/ply

Python: ast tree library: https://docs.python.org/3/library/ast.html

# LLM Agent
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