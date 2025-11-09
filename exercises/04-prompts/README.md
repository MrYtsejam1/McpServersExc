# Exercise 4: Prompts

## Objective

Learn how to create reusable prompt templates that help users accomplish specific tasks efficiently with your MCP server.

## What You'll Learn

- Prompt definition and registration
- Prompt arguments and templates
- Use cases for prompts
- Combining prompts with tools and resources
- Best practices for prompt design

## Background

Prompts in MCP are pre-written templates that help users accomplish specific tasks. They're like shortcuts or macros that provide structured guidance to the LLM. Prompts can include:

- Instructions for the LLM
- Context from resources
- Suggested tool usage patterns
- Domain-specific workflows

Common use cases:
- Code review templates
- Bug report formats
- Data analysis workflows
- Documentation generation
- Testing procedures

## Setup

```bash
cd exercises/04-prompts

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv add "mcp[cli]"
```

## Task

Create a code review assistant server that provides prompts for common code review tasks:

1. `review_pull_request` - Template for reviewing a pull request
2. `suggest_improvements` - Template for suggesting code improvements
3. `write_tests` - Template for writing tests for code
4. `document_code` - Template for documenting code

## Implementation Guide

### Step 1: Set up the server

Create `code_review_server.py`:

```python
from mcp.server.fastmcp import FastMCP
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("code-review-assistant")
```

### Step 2: Implement basic prompts

Use the `@mcp.prompt()` decorator to register prompts:

```python
@mcp.prompt()
async def review_pull_request() -> str:
    """Comprehensive pull request review template."""
    return """Please review this pull request with the following checklist:

## Code Quality
- [ ] Code follows project style guidelines
- [ ] Variable and function names are clear and descriptive
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Complex logic is well-commented
- [ ] No unnecessary code or commented-out blocks

## Functionality
- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No obvious bugs or logic errors

## Testing
- [ ] Tests are included for new functionality
- [ ] Tests cover edge cases
- [ ] All tests pass
- [ ] Test names are descriptive

## Security
- [ ] No sensitive data is exposed
- [ ] Input validation is present
- [ ] No SQL injection or XSS vulnerabilities
- [ ] Authentication/authorization is correct

## Performance
- [ ] No obvious performance issues
- [ ] Database queries are optimized
- [ ] No unnecessary API calls
- [ ] Appropriate caching is used

## Documentation
- [ ] Public APIs are documented
- [ ] README is updated if needed
- [ ] Breaking changes are noted

Please provide specific feedback on each section with examples from the code.
"""
```

### Step 3: Implement prompts with arguments

Prompts can accept arguments to customize the template:

```python
@mcp.prompt()
async def suggest_improvements(language: str, focus_area: str = "general") -> str:
    """Suggest code improvements for a specific language and focus area.
    
    Args:
        language: Programming language (e.g., "Python", "JavaScript")
        focus_area: Area to focus on (e.g., "performance", "readability", "security")
    """
    return f"""Please analyze this {language} code and suggest improvements focusing on {focus_area}.

## Analysis Framework

1. **Current State**: Describe what the code currently does
2. **Issues Identified**: List specific problems or concerns
3. **Suggested Improvements**: Provide concrete recommendations
4. **Example Refactoring**: Show improved code examples
5. **Trade-offs**: Discuss any trade-offs in your suggestions

## Focus: {focus_area.title()}

{"Focus on performance optimizations, algorithmic efficiency, and resource usage." if focus_area == "performance" else ""}
{"Focus on code clarity, naming conventions, and maintainability." if focus_area == "readability" else ""}
{"Focus on security vulnerabilities, input validation, and safe practices." if focus_area == "security" else ""}

Please provide specific, actionable feedback with code examples.
"""
```

### Step 4: Create prompts that reference tools

Prompts can guide users to use specific tools:

```python
@mcp.prompt()
async def write_tests(test_framework: str = "pytest") -> str:
    """Template for writing comprehensive tests.
    
    Args:
        test_framework: Testing framework to use (e.g., "pytest", "unittest", "jest")
    """
    framework_examples = {
        "pytest": """
```python
import pytest

def test_example():
    # Arrange
    expected = 42
    
    # Act
    result = my_function()
    
    # Assert
    assert result == expected

def test_edge_case():
    with pytest.raises(ValueError):
        my_function(invalid_input)
```
""",
        "unittest": """
```python
import unittest

class TestExample(unittest.TestCase):
    def test_example(self):
        # Arrange
        expected = 42
        
        # Act
        result = my_function()
        
        # Assert
        self.assertEqual(result, expected)
    
    def test_edge_case(self):
        with self.assertRaises(ValueError):
            my_function(invalid_input)
```
""",
        "jest": """
```javascript
describe('Example', () => {
  test('should return expected value', () => {
    // Arrange
    const expected = 42;
    
    // Act
    const result = myFunction();
    
    // Assert
    expect(result).toBe(expected);
  });
  
  test('should handle edge case', () => {
    expect(() => myFunction(invalidInput)).toThrow();
  });
});
```
"""
    }
    
    example = framework_examples.get(test_framework, framework_examples["pytest"])
    
    return f"""Please write comprehensive tests using {test_framework}.

## Test Structure

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **Edge Cases**: Test boundary conditions and error cases
4. **Happy Path**: Test normal, expected usage

## Test Template

{example}

## Coverage Goals

- Aim for 80%+ code coverage
- Test all public APIs
- Test error conditions
- Test edge cases and boundary values

## Best Practices

- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Keep tests independent
- Use fixtures/mocks appropriately
- Test one thing per test

Please generate tests following this structure.
"""
```

### Step 5: Add a tool to list prompts

```python
@mcp.tool()
async def list_prompts() -> str:
    """List all available code review prompts."""
    prompts = [
        "review_pull_request - Comprehensive PR review checklist",
        "suggest_improvements(language, focus_area) - Code improvement suggestions",
        "write_tests(test_framework) - Test writing template",
        "document_code - Code documentation template",
    ]
    return "\n".join(prompts)
```

### Step 6: Implement the document_code prompt

```python
@mcp.prompt()
async def document_code(style: str = "google") -> str:
    """Template for documenting code.
    
    Args:
        style: Documentation style (e.g., "google", "numpy", "sphinx")
    """
    return f"""Please add comprehensive documentation to this code using {style} style.

## Documentation Requirements

### Functions/Methods
- Brief description of what it does
- Parameters with types and descriptions
- Return value with type and description
- Exceptions that may be raised
- Usage examples

### Classes
- Class purpose and responsibility
- Attributes with types and descriptions
- Method documentation
- Usage examples

### Modules
- Module purpose
- Key components
- Usage examples

## {style.title()} Style Example

```python
def example_function(param1: str, param2: int) -> bool:
    \"\"\"Brief description of what the function does.
    
    Longer description if needed, explaining the function's
    behavior in more detail.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
        TypeError: When param1 is not a string
    
    Example:
        >>> example_function("test", 42)
        True
    \"\"\"
    pass
```

Please document all public functions, classes, and modules.
"""
```

### Step 7: Add the main function

```python
def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
```

## Testing

### Using MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory /absolute/path/to/04-prompts run code_review_server.py
```

In the inspector:
1. Click on "Prompts" tab
2. You should see your prompts listed
3. Click on a prompt to use it
4. Fill in any required arguments

### Using Claude for Desktop

Add to your Claude config:

```json
{
  "mcpServers": {
    "code-review": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/exercises/04-prompts",
        "run",
        "code_review_server.py"
      ]
    }
  }
}
```

Test by asking Claude to use the prompts:
- "Use the review_pull_request prompt to review this code"
- "Use suggest_improvements for Python code focusing on performance"
- "Help me write tests using the write_tests prompt with pytest"

## Best Practices

1. **Clear Instructions**: Make prompts specific and actionable
2. **Structured Output**: Use checklists and sections
3. **Examples**: Include examples in prompts
4. **Flexibility**: Use arguments for customization
5. **Context**: Provide relevant context and background
6. **Actionable**: Focus on what the user should do

## Verification Checklist

- [ ] All four prompts are implemented
- [ ] Prompts with arguments work correctly
- [ ] Prompts provide clear, structured guidance
- [ ] Examples are included where helpful
- [ ] No `print()` statements
- [ ] Prompts appear in MCP Inspector
- [ ] Prompts can be used in Claude

## Common Pitfalls

1. **Too vague**: Prompts should be specific
2. **Too rigid**: Allow for customization with arguments
3. **No examples**: Users need concrete examples
4. **Too long**: Keep prompts focused and concise
5. **No structure**: Use sections and checklists

## Challenge Extensions

Try these additional features:

1. Add a prompt for security audits
2. Create a prompt for API design review
3. Add a prompt for database schema review
4. Create language-specific code review prompts
5. Add a prompt for accessibility review

## Solution

Check `solution.py` for a complete implementation.

## Next Steps

Move on to Exercise 5 to build a complete server combining all concepts:

```bash
cd ../05-complete-server
cat README.md
```
