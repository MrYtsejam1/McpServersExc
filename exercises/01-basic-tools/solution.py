from mcp.server.fastmcp import FastMCP
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("calculator")


@mcp.tool()
async def add(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    logger.info(f"Adding {a} + {b}")
    return a + b


@mcp.tool()
async def subtract(a: float, b: float) -> float:
    """Subtract second number from first number.
    
    Args:
        a: First number (minuend)
        b: Second number (subtrahend)
    """
    logger.info(f"Subtracting {b} from {a}")
    return a - b


@mcp.tool()
async def multiply(a: float, b: float) -> float:
    """Multiply two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    logger.info(f"Multiplying {a} * {b}")
    return a * b


@mcp.tool()
async def divide(a: float, b: float) -> str:
    """Divide first number by second number.
    
    Args:
        a: Dividend (number to be divided)
        b: Divisor (number to divide by)
    """
    logger.info(f"Dividing {a} by {b}")
    
    if b == 0:
        return "Error: Cannot divide by zero"
    
    result = a / b
    return f"{result}"


def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
