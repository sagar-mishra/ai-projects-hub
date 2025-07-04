from fastmcp import FastMCP

mcp = FastMCP("MathServer")

@mcp.tool()
def add(a: float, b: float) -> float:
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    if b == 0:
        return "Error: division by zero"
    return a / b

if __name__ == "__main__":
    mcp.run(transport="stdio", debug=True)
