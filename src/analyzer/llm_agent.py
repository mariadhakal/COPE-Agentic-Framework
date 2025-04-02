from src.utils.parsers import parse_code_with_javaparser
from src.analyzer.external_tools import run_profiler
from src.architectures.architecture_registry import get_architectures
from src.analyzer.state import AnalysisState


class JavaCodeAnalyzerAgent:
    def __init__(self, llm):
        """
        :param llm: An instance of your open-source LLM that provides a .run(prompt) method.
        """
        self.llm = llm

    def analyze_code(self, java_file_path: str) -> AnalysisState:
        # Initialize analysis state
        state = AnalysisState()

        # Step 1: Read and parse the Java code using the JavaParser wrapper.
        state.code_structure = parse_code_with_javaparser(java_file_path)

        # Step 2: Gather dynamic performance metrics across architectures.
        performance_data = {}
        for arch_module in get_architectures():
            performance_data[arch_module.name] = arch_module.evaluate(state)
        state.performance = performance_data

        # Step 3: Build the prompt for the LLM-based agent.
        combined_input = {
            "code_structure": state.code_structure,
            "performance_data": state.performance
        }
        prompt = self._build_prompt(combined_input)

        # Step 4: Use the LLM to identify bottlenecks.
        bottleneck_analysis = self.llm.run(prompt)
        state.bottlenecks = bottleneck_analysis
        return state

    def _build_prompt(self, combined_input: dict) -> str:
        prompt = (
            "You are given the following Java code information:\n\n"
            f"Callgraph/Structure: {combined_input['code_structure']}\n\n"
            f"Performance Metrics: {combined_input['performance_data']}\n\n"
            "Identify the potential bottlenecks in the code and suggest improvements."
        )
        return prompt
