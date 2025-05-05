import javalang
import json

def ast_node_to_dict(node):
    """Recursively convert a javalang AST node to a dict."""
    if isinstance(node, javalang.ast.Node):
        d = { 'node_type': type(node).__name__ }
        for attr in node.attrs:
            value = getattr(node, attr)
            # Handle any sequence type (list, set, tuple)
            if isinstance(value, (list, set, tuple)):
                lst = []
                for x in value:
                    if isinstance(x, javalang.ast.Node):
                        lst.append(ast_node_to_dict(x))
                    else:
                        lst.append(x)
                d[attr] = lst
            # Recurse into sub-nodes
            elif isinstance(value, javalang.ast.Node):
                d[attr] = ast_node_to_dict(value)
            # Primitives (str, int, etc.)
            else:
                d[attr] = value
        return d
    else:
        return str(node)

def java_parser(snippet: str) -> str:
    # 1) Wrap in a dummy class so javalang can parse
    wrapped = f"{snippet}"

    try:
        tree = javalang.parse.parse(wrapped)
        ast_dict = ast_node_to_dict(tree)
        return json.dumps(ast_dict, indent=2)
    except javalang.parser.JavaSyntaxError as e:
        return f"Parse error: {e}"

print(java_parser("""
    public class HelloWorld{
        public static void main(String[] args) {
            System.out.println("Hello World!");
        }
    }
    """))