# This file implements a simple execution graph. The graph runs the first node (which requires a file path) and then passes the updated state to subsequent nodes.

# src/analyzer/graph.py

from src.analyzer.state import AnalysisState

class AnalysisGraph:
    """
    Represents an execution graph where each node processes the AnalysisState.
    """
    def __init__(self, nodes):
        self.nodes = nodes  # List of node instances to execute sequentially

    def execute(self, file_path: str, initial_state: AnalysisState = None) -> AnalysisState:
        # Initialize state if not provided.
        state = initial_state if initial_state else AnalysisState()
        # Assume the first node requires the file path.
        if self.nodes:
            state = self.nodes[0].run(file_path, state)
        # Run the remaining nodes which operate solely on the state.
        for node in self.nodes[1:]:
            state = node.run(state)
        return state

# Example usage:
# from src.analyzer.nodes import CodeReaderNode, StaticAnalyzerNode, PerformanceEvaluatorNode, BottleneckIdentifierNode
# nodes = [CodeReaderNode(), StaticAnalyzerNode(), PerformanceEvaluatorNode(), BottleneckIdentifierNode()]
# graph = AnalysisGraph(nodes)
# final_state = graph.execute("path/to/YourJavaFile.java")
# print(final_state)
