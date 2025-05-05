import os
import json
from mistralai import Mistral, AssistantMessage, ToolMessage, UserMessage, SystemMessage
from mistralai.models.function import Function
import re
from java_code_parser import java_parser
import javalang

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


prompt = """
    You're a Java code parsing and profiling assistant. Your task is to analyze and profile Java code provided by users.

    You run in a loop of Thought, Action, PAUSE, Observation.
    At the end of the loop you output an Answer
    
    Use Thought to describe why you’re doing what you’re doing.
    Use Action to invoke one of your tools, then return PAUSE.
    Observation will be filled in with the result of that action.
    
    Your available tools are: 
    • java_code_parser: - Input: a Java code snippet (method or class) - Behavior: parses 
    the Java code and produces an abstract syntax tree (AST) - Example: Action: java_code_parser: public class 
    Operations{public int fib(int n) { return n < 2 ? n : fib(n-1)+fib(n-2); }}
    
    • java_profiler: - Input: a complete Java class with a main method - Behavior: compiles and executes the Java 
    code with JFR enabled, and returns profiling metrics - Parameters: class_name, duration_seconds (optional) - 
    Example: Action: java_profiler: public class HelloWorld { public static void main(String[] args) { 
    System.out.println("Hello World!"); } } | HelloWorld | 5

When given Java code:
1. First, check if the code appears to be valid Java syntax (proper brackets, semicolons, etc.)
2. Assess if the code is a complete method, class, or if it needs to be wrapped
3. Use the java_code_parser tool to try parsing the code
4. If the code contains a main method and the user wants to profile it, use the java_profiler tool
5. Analyze the results and provide insights on performance metrics
6. Summarize your findings in the final Answer

Example session:

Question: Parse this Java code:
public int calculate(int x, int y) {
    return x + y;
}

Thought: I need to analyze this Java method that calculates the sum of two integers. I'll use the java_code_parser 
tool to get the AST.

Action: java_code_parser: public int calculate(int x, int y) { return x + y; }

PAUSE

Observation: {"methodName": "calculate", "returnType": "int", "parameters": [{"type": "int", "name": "x"}, 
{"type": "int", "name": "y"}], "body": {"type": "ReturnStatement", "expression": {"type": "BinaryOperation", 
"operator": "+", "leftOperand": "x", "rightOperand": "y"}}}

Thought: Now I can analyze the AST. This is a simple method that takes two integer parameters and returns their sum.

Answer: The code defines a method named 'calculate' that:
- Takes two integer parameters: x and y
- Returns an integer value
- Has a simple implementation that adds x and y and returns the result
- Has a time complexity of O(1) and space complexity of O(1)

Question: Profile this Java code:
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello World!");
    }
}

Thought: I need to profile this Java class that has a main method. I'll use the java_profiler tool to get performance metrics.

Action: profile_java_code: public class HelloWorld { public static void main(String[] args) { System.out.println("Hello World!"); } } | HelloWorld | 5

PAUSE

Observation: {
  "success": true,
  "jfr_file": "jfr_profiles/HelloWorld_1714898724.jfr",
  "stdout": "Hello World!",
  "metrics": {
    "summary": "Recording: recording-1, duration: 5s",
    "cpu": "CPU load: 2.3% (user: 1.8%, system: 0.5%)",
    "memory": "Heap used: 15.2 MB (12.3% of total heap)"
  }
}

Thought: Now I can analyze the profiling results. This is a simple program with minimal CPU and memory usage.

Answer: The code was successfully profiled. The results show:
- CPU usage was very low (2.3%), as expected for a simple Hello World program
- Memory usage was minimal (15.2 MB)
- The program executed successfully with the output "Hello World!"
- No performance issues were detected in this simple program
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

    # Return a simplified version of the results as JSON
    simplified_results = {
        "success": results["success"]
    }

    if results["success"]:
        simplified_results.update({
            "jfr_file": results["jfr_file"],
            "stdout": results["stdout"],
            "metrics": {
                "summary": results["metrics"]["summary"][:100] if "summary" in results["metrics"] else "Not available",
                "cpu": results["metrics"]["cpu"][:100] if "cpu" in results["metrics"] else "Not available",
                "memory": results["metrics"]["memory"][:100] if "memory" in results["metrics"] else "Not available"
            }
        })
    else:
        simplified_results.update({
            "stage": results.get("stage", "unknown"),
            "error": results.get("error", "Unknown error")
        })

    return json.dumps(simplified_results, indent=2)


# Add the java_profiler to known actions
known_actions = {
    "java_code_parser": java_code_parser,
    "profile_java_code": profile_java_code,
}

# Creating a loop for tool calling agent
action_re = re.compile(r'^\s*Action:\s*(\w+)\s*:\s*(.*)$')  # python regular expression to selection action


def query(code, max_turns=5):
    i = 0  # counter to keep track of iterations
    bot = Agent(prompt)  # initialize agent with default system prompt
    next_prompt = f"Parse and analyze this Java code:\n{code}\n"

    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)

        # actions = [
        #     action_re.match(a)
        #     for a in result.split("\n")  # parse the content of the result
        #     if action_re.match(a)
        # ]
        actions = [
            action_re.match(line.strip())
            for line in result.splitlines()
            if action_re.match(line.strip())
        ]

        if actions:
            # there is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print("-- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return


# Calling an agent

if __name__ == "__main__":
    # Example usage for profiling
    profiling_code = """
    public class BubbleSort {
        public static void main(String[] args) {
            int[] arr = {64, 34, 25, 12, 22, 11, 90};

            System.out.println("Array before sorting:");
            printArray(arr);

            bubbleSort(arr);

            System.out.println("Array after sorting:");
            printArray(arr);
        }

        static void bubbleSort(int[] arr) {
            int n = arr.length;
            for (int i = 0; i < n - 1; i++) {
                for (int j = 0; j < n - i - 1; j++) {
                    if (arr[j] > arr[j + 1]) {
                        // swap arr[j+1] and arr[j]
                        int temp = arr[j];
                        arr[j] = arr[j + 1];
                        arr[j + 1] = temp;
                    }
                }
            }
        }

        static void printArray(int[] arr) {
            for (int i = 0; i < arr.length; i++) {
                System.out.print(arr[i] + " ");
            }
            System.out.println();
        }
    }
    """

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--profile":
        # Run in profiling mode
        query(profiling_code)
    else:
        # Run in parsing mode (your original example)
        sample_code = """
        public int setSecurityMode ( int level, String authToken ) throws RemoteException {
        if ( !this.authToken.equals( authToken )){
            throw new RemoteException( "Invalid Login Token" );
        }
        ServerSettingBean.setSecureMode( "" + level );
        serverSettingBean.updateSettings();
        securityMode = level;
        return securityMode;
    }
        """
        query(sample_code)
