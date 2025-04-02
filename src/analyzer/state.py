# src/analyzer/state.py

class AnalysisState:
    def __init__(self):
        self.ast = None                 # Abstract Syntax Tree from parsing
        self.code_structure = None      # Callgraph and structural information
        self.metrics = {}               # Static analysis metrics (e.g., complexity)
        self.performance = {}           # Dynamic performance metrics per architecture
        self.bottlenecks = []           # Identified performance bottlenecks

    def __str__(self):
        return (
            f"AST: {self.ast}\n"
            f"Code Structure: {self.code_structure}\n"
            f"Metrics: {self.metrics}\n"
            f"Performance: {self.performance}\n"
            f"Bottlenecks: {self.bottlenecks}"
        )
