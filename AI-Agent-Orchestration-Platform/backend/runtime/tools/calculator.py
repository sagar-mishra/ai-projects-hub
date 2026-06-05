import numexpr

def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely (e.g., '2 * (3 + 4)') and return the result as a string."""
    try:
        # Sanitize expression
        expression = expression.strip().replace("^", "**")
        
        # We can use numexpr to evaluate
        # numexpr supports variables, but we evaluate simple arithmetic
        result = numexpr.evaluate(expression).item()
        return str(result)
    except Exception as e:
        return f"Error evaluating math expression: {str(e)}"
