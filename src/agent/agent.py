import os
import json
from mistralai import Mistral, AssistantMessage, ToolMessage, UserMessage, SystemMessage
from mistralai.models.function import Function
import re
from java_code_parser import java_parser
from java_profiler import JavaProfiler

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "Codestral-2501"

# Initialize model
client = Mistral(api_key=token, server_url=endpoint)


class Agent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
        # Initialize the Java profiler
        self.profiler = JavaProfiler()

    # What we want agent to do?
    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        response = client.chat.complete(
            messages=self.messages,
            model=model_name,
        )
        return response.choices[0].message.content


# Updated prompt for bottleneck diagnosis
prompt = """
    You're a Java Performance Expert and Bottleneck Diagnoser. Your task is to analyze Java code, profile its execution, 
    identify performance bottlenecks, and provide specific optimization recommendations.

    You run in a loop of Thought, Action, PAUSE, Observation.
    At the end of the loop you output an Answer.

    Use Thought to describe your reasoning process.
    Use Action to invoke one of your tools, then return PAUSE.
    Observation will be filled in with the result of that action.

    Your available tools are: 
    • java_code_parser: Parses Java code and produces an abstract syntax tree (AST)
      - Input: a Java code snippet (method or class)
      - Example: Action: java_code_parser: public class Operations{public int fib(int n) { return n < 2 ? n : fib(n-1)+fib(n-2); }}

    • java_profiler: Compiles and executes Java code with JFR enabled, returning profiling metrics
      - Input: a complete Java class with a main method, class name, and optional duration
      - Format: java_profiler: <java_code> | <class_name> | <duration_seconds>
      - Example: Action: java_profiler: public class HelloWorld { public static void main(String[] args) { System.out.println("Hello World!"); } } | HelloWorld | 5

    When analyzing code for performance bottlenecks:
    1. First parse the code to understand its structure using java_code_parser
    2. Identify potential algorithmic inefficiencies (e.g., nested loops, inefficient data structures)
    3. Use java_profiler to gather execution metrics if a main method is present
    4. Analyze the profiling results to identify:
       • Hot methods that consume most CPU time (check the hot_methods field in metrics)
       • Memory allocation issues from the memory metrics
       • CPU utilization patterns from the cpu metrics
       • Overall execution performance from the summary
    5. For each bottleneck identified, provide:
       • Detailed explanation of why it's a performance issue
       • Specific code modifications to improve performance
       • Expected performance gains from the optimization
    6. Prioritize recommendations based on potential impact

    Common performance bottlenecks to look for:
    • O(n²) or worse algorithmic complexity
    • Excessive object creation and garbage collection
    • Inefficient data structures for the workload
    • Redundant computations that could be cached
    • Excessive synchronization
    • Unoptimized database queries or I/O operations
    • String concatenation in loops (especially important to check!)
    • Boxed primitives in performance-critical code
    • Using ArrayList where LinkedList would be better (or vice versa)
    • Inefficient collection operations (like contains() on LinkedList)

    Your final Answer should include:
    1. A summary of identified bottlenecks
    2. Optimization recommendations with code examples
    3. Expected performance improvements
    4. Additional monitoring suggestions

    Pay special attention to the hot_methods list in the profiler output, as these are the methods consuming the most CPU time during execution. Always look carefully at these methods first, as they represent the biggest opportunities for optimization.

    Remember to be specific, actionable, and to prioritize recommendations based on impact.
""".strip()


def java_code_parser(snippet):
    """
    Wrapper function that calls the parse_java_code function from the imported module.
    This function will attempt to parse the Java code and return the AST.
    If parsing fails, it returns an error message.
    """
    is_full_cu = (
            snippet.lstrip().startswith(("package", "public class", "class"))
            or "interface" in snippet
            or "enum" in snippet
    )
    code = snippet if is_full_cu else f"class _Wrapper {{ {snippet} }}"
    try:
        # Call the parse_java_code function from your module
        return java_parser(code)
    except Exception as e:
        return f"Error parsing code: {str(e)}"


def profile_java_code(input_string):
    """
    Profiles Java code using JFR and returns the metrics.
    Expected format: <java_code> | <class_name> | <duration_seconds>
    """
    parts = input_string.split('|')

    if len(parts) < 2:
        return "Error: Input must contain Java code and class name separated by '|'"

    java_code = parts[0].strip()
    class_name = parts[1].strip()

    # Default duration is 5 seconds if not specified
    duration_seconds = 5
    if len(parts) > 2:
        try:
            duration_seconds = int(parts[2].strip())
        except ValueError:
            return "Error: Duration must be an integer"

    profiler = JavaProfiler()

    # Run the profiling
    results = profiler.profile_code(
        java_code=java_code,
        class_name=class_name,
        duration_seconds=duration_seconds
    )

    # Return a detailed version of the results for bottleneck analysis
    detailed_results = {
        "success": results["success"]
    }

    if results["success"]:
        detailed_results.update({
            "jfr_file": results["jfr_file"],
            "stdout": results["stdout"],
            "stderr": results.get("stderr", ""),
            "metrics": {
                "summary": results["metrics"].get("summary", "Not available"),
                "metadata": results["metrics"].get("metadata", "Not available"),
                "cpu": results["metrics"].get("cpu", "Not available"),
                "memory": results["metrics"].get("memory", "Not available"),
                "file_size_bytes": results["metrics"].get("file_size_bytes", 0),
                "hot_methods": results["metrics"].get("hot_methods", [])
            }
        })
    else:
        detailed_results.update({
            "stage": results.get("stage", "unknown"),
            "error": results.get("error", "Unknown error")
        })

    return json.dumps(detailed_results, indent=2)


# Fix mapping to use correct function name
known_actions = {
    "java_code_parser": java_code_parser,
    "java_profiler": profile_java_code,
}

# Regular expression to identify actions in the agent's response
action_re = re.compile(r'^\s*Action:\s*(\w+)\s*:\s*(.*)', re.MULTILINE)


def query(code, max_turns=10):
    """
    Run the agent with the given code and maximum number of turns.
    Increased max_turns to allow for more thorough analysis.
    """
    i = 0  # counter to keep track of iterations
    bot = Agent(prompt)  # initialize agent with updated system prompt
    next_prompt = f"Analyze this Java code for performance bottlenecks:\n{code}\n"

    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(f"Turn {i}:\n{result}\n")

        # Find actions in the response
        actions = [
            action_re.match(line.strip())
            for line in result.splitlines()
            if action_re.match(line.strip())
        ]

        if actions:
            # Run the first action found
            action, action_input = actions[0].groups()
            if action not in known_actions:
                print(f"Unknown action: {action}: {action_input}")
                return result

            print(f"Running: {action} with input: {action_input[:100]}...")
            observation = known_actions[action](action_input)
            print(f"Observation: {observation[:200]}...")
            next_prompt = f"Observation: {observation}"
        else:
            # No more actions, we're done
            print("Analysis complete.")
            return result


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Analyze Java code for performance bottlenecks')
    parser.add_argument('--file', type=str, help='Path to Java file to analyze')
    parser.add_argument('--code', type=str, help='Java code snippet to analyze')
    parser.add_argument('--max-turns', type=int, default=10, help='Maximum number of turns for the agent')

    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r') as f:
            code = f.read()
        query(code, args.max_turns)
    elif args.code:
        query(args.code, args.max_turns)
    else:
        # Example usage with a sample that has performance issues
        sample_code = """
        public class SlowCollection {
            public static void main(String[] args) {
                long startTime = System.currentTimeMillis();

                // Create a large collection
                String[] strings = new String[100000];
                for (int i = 0; i < strings.length; i++) {
                    strings[i] = "Item " + i;
                }

                // Inefficient search
                String searchItem = "Item 99999";
                for (int i = 0; i < strings.length; i++) {
                    if (strings[i].equals(searchItem)) {
                        System.out.println("Found at index: " + i);
                        break;
                    }
                }

                // String concatenation in a loop
                String result = "";
                for (int i = 0; i < 10000; i++) {
                    result += "a";
                }

                // Inefficient memory usage
                Integer[] boxedInts = new Integer[100000];
                for (int i = 0; i < boxedInts.length; i++) {
                    boxedInts[i] = Integer.valueOf(i);
                }

                long endTime = System.currentTimeMillis();
                System.out.println("Execution time: " + (endTime - startTime) + " ms");
            }
        }
        """
        query(sample_code, args.max_turns)