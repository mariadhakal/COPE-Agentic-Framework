from typing import Dict, Any, List
import anthropic
from ..analyzer.external_tools import ExternalToolExecutor


class ARM64Analyzer:
    """Analyzer for ARM64 architecture performance characteristics."""

    ARCHITECTURE_NAME = "ARM64"

    # Architecture-specific characteristics
    CACHE_LEVELS = {
        "L1": {"size": "64KB", "latency_cycles": 4},
        "L2": {"size": "512KB", "latency_cycles": 11},
        "L3": {"size": "4MB", "latency_cycles": 30}
    }

    SIMD_EXTENSIONS = ["NEON", "SVE", "SVE2"]

    BRANCH_PREDICTION = {
        "misprediction_penalty": "10-15 cycles",
        "prediction_accuracy": "90-95%"
    }

    @staticmethod
    def analyze_performance(code: str, ast: Dict, call_graph: Dict = None, dataflow: Dict = None) -> Dict:
        """
        Analyze code performance for ARM64 architecture.

        Args:
            code: Source code to analyze
            ast: Abstract Syntax Tree of the code
            call_graph: Call graph of the code (optional)
            dataflow: Data flow analysis results (optional)

        Returns:
            Dictionary with architecture-specific performance metrics
        """
        client = anthropic.Anthropic()

        # Prepare context information about the architecture
        arch_info = {
            "name": ARM64Analyzer.ARCHITECTURE_NAME,
            "cache_levels": ARM64Analyzer.CACHE_LEVELS,
            "simd_extensions": ARM64Analyzer.SIMD_EXTENSIONS,
            "branch_prediction": ARM64Analyzer.BRANCH_PREDICTION
        }

        # Determine language from code (simplified version)
        language = "python"  # Default assumption
        if "int main" in code or "{" in code:
            language = "c" if code.count(";") > code.count("=>") else "cpp"

        # Extract key patterns for ARM64 analysis
        patterns = ARM64Analyzer._extract_patterns(code, language)

        # Prepare prompt with architecture-specific information
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze the performance characteristics of this code specifically on ARM64 architecture:

                    ```
                    {code}
                    ```

                    Architecture information:
                    - Cache hierarchy: L1 (64KB, 4 cycles), L2 (512KB, 11 cycles), L3 (4MB, 30 cycles)
                    - SIMD extensions: NEON, SVE, SVE2
                    - Branch misprediction penalty: 10-15 cycles
                    - Power efficiency focus: ARM cores typically prioritize energy efficiency

                    Patterns detected in code:
                    {patterns}

                    Provide detailed performance metrics including:
                    1. Time complexity
                    2. Space complexity
                    3. Cache behavior (locality, misses)
                    4. Branch prediction impact
                    5. NEON/SVE optimization opportunities
                    6. ARM64-specific bottlenecks

                    Format your response as JSON with these keys:
                    - time_complexity
                    - space_complexity
                    - cache_behavior
                    - branch_prediction_effects
                    - simd_opportunities
                    - architecture_bottlenecks (array)
                    - optimization_suggestions (array)
                    """
                }
            ]
        )

        # Parse and return the analysis
        import json
        import re

        # Find JSON in the response
        json_match = re.search(r'```json\n(.*?)\n```', response.content[0].text, re.DOTALL)
        if json_match:
            try:
                metrics = json.loads(json_match.group(1))
                return metrics
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "error": "Failed to parse metrics",
                    "raw_text": response.content[0].text
                }
        else:
            # Try to find JSON without code blocks
            try:
                metrics = json.loads(response.content[0].text)
                return metrics
            except json.JSONDecodeError:
                return {
                    "error": "No metrics found",
                    "raw_text": response.content[0].text
                }

    @staticmethod
    def _extract_patterns(code: str, language: str) -> str:
        """Extract patterns that are important for ARM64 performance analysis."""
        patterns = []

        # Look for nested loops (potential cache issues)
        if "for" in code and code.count("for") > 1:
            patterns.append("Nested loops detected (potential cache locality issues)")

        # Look for conditional branches (potential branch prediction issues)
        if code.count("if") > 3:
            patterns.append("Multiple conditional branches detected (potential branch prediction challenges)")

        # Look for potential NEON/SVE patterns
        if "array" in code or "[]" in code:
            patterns.append("Array operations detected (potential NEON/SVE optimization opportunity)")

        # Look for pointer operations in C/C++
        if language in ["c", "cpp"] and "*" in code:
            patterns.append("Pointer operations detected (memory access patterns important)")

        # Look for memory allocation
        if "malloc" in code or "new" in code:
            patterns.append("Dynamic memory allocation detected (potential cache alignment issues)")

        # Look for power-intensive operations
        if "while" in code and ("True" in code or "1" in code):
            patterns.append("Infinite or long-running loop detected (power consumption concern for ARM)")

        return "\n".join(patterns)