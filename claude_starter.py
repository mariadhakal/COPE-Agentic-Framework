import anthropic
from typing import TypedDict, List, Dict, Any, Callable
from langgraph.graph import StateGraph, END


# Define your state
class ProgramAnalyzerState(TypedDict):
    code: str
    ast: Dict
    performance_metrics: Dict
    bottlenecks: List[Dict]
    architectures: List[str]
    recommendations: List[Dict]
    current_architecture: str
    analysis_complete: bool


# Code parsing node
def parse_code(state: ProgramAnalyzerState) -> ProgramAnalyzerState:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"Parse this code and provide the AST representation as a JSON structure:\n\n{state['code']}"
            }
        ]
    )

    # Extract JSON from the response
    import json
    import re

    # Find JSON-like content in the response
    json_match = re.search(r'```json\n(.*?)\n```', response.content[0].text, re.DOTALL)
    if json_match:
        try:
            state["ast"] = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            state["ast"] = {"error": "Failed to parse AST", "raw_text": response.content[0].text}
    else:
        state["ast"] = {"error": "No AST found", "raw_text": response.content[0].text}

    return state


# Architecture selector node
def select_next_architecture(state: ProgramAnalyzerState) -> ProgramAnalyzerState:
    # Get the next architecture to analyze
    analyzed_archs = set(state["performance_metrics"].keys())
    remaining_archs = [arch for arch in state["architectures"] if arch not in analyzed_archs]

    if remaining_archs:
        state["current_architecture"] = remaining_archs[0]
    else:
        state["analysis_complete"] = True

    return state


# Analysis per architecture node
def analyze_performance(state: ProgramAnalyzerState) -> ProgramAnalyzerState:
    client = anthropic.Anthropic()
    arch = state["current_architecture"]

    code_snippet = state["code"][:1000] if len(state["code"]) > 1000 else state["code"]

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""Analyze the performance characteristics of this code on {arch} architecture:

                ```
                {code_snippet}
                ```

                Provide detailed performance metrics including:
                1. Time complexity
                2. Space complexity
                3. Expected bottlenecks
                4. Architecture-specific issues

                Format your response as JSON with these keys:
                - time_complexity
                - space_complexity
                - bottlenecks (array)
                - arch_specific_issues (array)
                """
            }
        ]
    )

    # Extract JSON from the response
    import json
    import re

    # Find JSON-like content in the response
    json_match = re.search(r'```json\n(.*?)\n```', response.content[0].text, re.DOTALL)
    if json_match:
        try:
            metrics = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            metrics = {
                "error": "Failed to parse metrics",
                "raw_text": response.content[0].text
            }
    else:
        # Try to find JSON without code blocks
        try:
            metrics = json.loads(response.content[0].text)
        except json.JSONDecodeError:
            metrics = {
                "error": "No metrics found",
                "raw_text": response.content[0].text
            }

    # Add metrics for current architecture
    if "performance_metrics" not in state:
        state["performance_metrics"] = {}

    state["performance_metrics"][arch] = metrics
    return state


# Bottleneck identification node
def identify_bottlenecks(state: ProgramAnalyzerState) -> ProgramAnalyzerState:
    client = anthropic.Anthropic()

    # Prepare performance data for prompt
    import json
    performance_data = json.dumps(state["performance_metrics"], indent=2)

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""Given the performance analysis across different architectures, identify the common and architecture-specific bottlenecks:

                Performance Data: {performance_data}

                For each bottleneck, provide:
                1. Description
                2. Severity (High/Medium/Low)
                3. Affected architectures
                4. Root cause
                5. Potential solutions

                Format your response as a JSON array of bottleneck objects.
                """
            }
        ]
    )

    # Extract JSON from the response
    import json
    import re

    # Find JSON-like content in the response
    json_match = re.search(r'```json\n(.*?)\n```', response.content[0].text, re.DOTALL)
    if json_match:
        try:
            state["bottlenecks"] = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            state["bottlenecks"] = [{"error": "Failed to parse bottlenecks", "raw_text": response.content[0].text}]
    else:
        # Try to find JSON without code blocks
        try:
            state["bottlenecks"] = json.loads(response.content[0].text)
        except json.JSONDecodeError:
            state["bottlenecks"] = [{"error": "No bottlenecks found", "raw_text": response.content[0].text}]

    return state


# Recommendation generation node
def generate_recommendations(state: ProgramAnalyzerState) -> ProgramAnalyzerState:
    client = anthropic.Anthropic()

    # Prepare bottlenecks data for prompt
    import json
    bottlenecks_data = json.dumps(state["bottlenecks"], indent=2)

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""Based on the identified bottlenecks, generate specific recommendations to improve the code's performance:

                Bottlenecks: {bottlenecks_data}

                For each recommendation, provide:
                1. Detailed description
                2. Expected performance improvement
                3. Implementation complexity (High/Medium/Low)
                4. Code example showing the recommendation

                Format your response as a JSON array of recommendation objects with these fields.
                """
            }
        ]
    )

    # Extract JSON from the response
    import json
    import re

    # Find JSON-like content in the response
    json_match = re.search(r'```json\n(.*?)\n```', response.content[0].text, re.DOTALL)
    if json_match:
        try:
            state["recommendations"] = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            state["recommendations"] = [
                {"error": "Failed to parse recommendations", "raw_text": response.content[0].text}]
    else:
        # Try to find JSON without code blocks
        try:
            state["recommendations"] = json.loads(response.content[0].text)
        except json.JSONDecodeError:
            state["recommendations"] = [{"error": "No recommendations found", "raw_text": response.content[0].text}]

    return state


# LangGraph state router
def router(state: ProgramAnalyzerState) -> str:
    if state.get("analysis_complete", False):
        return "identify_bottlenecks"
    else:
        return "analyze_performance"


# Create the workflow
def create_program_analyzer() -> Callable:
    # Create the graph
    workflow = StateGraph(ProgramAnalyzerState)

    # Add nodes
    workflow.add_node("parse_code", parse_code)
    workflow.add_node("select_architecture", select_next_architecture)
    workflow.add_node("analyze_performance", analyze_performance)
    workflow.add_node("identify_bottlenecks", identify_bottlenecks)
    workflow.add_node("generate_recommendations", generate_recommendations)

    # Add edges
    workflow.add_edge("parse_code", "select_architecture")
    workflow.add_edge("select_architecture", router)
    workflow.add_edge("analyze_performance", "select_architecture")
    workflow.add_edge("identify_bottlenecks", "generate_recommendations")
    workflow.add_edge("generate_recommendations", END)

    # Compile the graph
    app = workflow.compile()

    # Create a function to run the analyzer
    def run_analyzer(code: str, architectures: List[str] = None):
        if architectures is None:
            architectures = ["x86_64", "ARM64", "CUDA", "AVX512"]

        # Initialize state
        state = {
            "code": code,
            "ast": {},
            "performance_metrics": {},
            "bottlenecks": [],
            "architectures": architectures,
            "recommendations": [],
            "current_architecture": "",
            "analysis_complete": False
        }

        # Run the graph
        result = app.invoke(state, {"stream": False})
        return result

    return run_analyzer


# Example usage
if __name__ == "__main__":
    analyzer = create_program_analyzer()

    # Example code to analyze
    sample_code = """
    def matrix_multiply(A, B):
        m, n = len(A), len(A[0])
        p = len(B[0])

        C = [[0 for _ in range(p)] for _ in range(m)]

        for i in range(m):
            for j in range(p):
                for k in range(n):
                    C[i][j] += A[i][k] * B[k][j]

        return C
    """

    # Run the analyzer
    result = analyzer(sample_code, ["x86_64", "ARM64", "CUDA"])

    # Print results
    import json

    print(json.dumps(result, indent=2))