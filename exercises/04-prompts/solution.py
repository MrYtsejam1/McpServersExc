from mcp.server.fastmcp import FastMCP
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("code-review-assistant")


@mcp.prompt()
async def review_pull_request() -> str:
    """Comprehensive pull request review template."""
    return """Please review this pull request with the following checklist:

- [ ] Code follows project style guidelines
- [ ] Variable and function names are clear and descriptive
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Complex logic is well-commented
- [ ] No unnecessary code or commented-out blocks

- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No obvious bugs or logic errors

- [ ] Tests are included for new functionality
- [ ] Tests cover edge cases
- [ ] All tests pass
- [ ] Test names are descriptive

- [ ] No sensitive data is exposed
- [ ] Input validation is present
- [ ] No SQL injection or XSS vulnerabilities
- [ ] Authentication/authorization is correct

- [ ] No obvious performance issues
- [ ] Database queries are optimized
- [ ] No unnecessary API calls
- [ ] Appropriate caching is used

- [ ] Public APIs are documented
- [ ] README is updated if needed
- [ ] Breaking changes are noted

Please provide specific feedback on each section with examples from the code.
"""


@mcp.prompt()
async def suggest_improvements(language: str, focus_area: str = "general") -> str:
    """Suggest code improvements for a specific language and focus area.
    
    Args:
        language: Programming language (e.g., "Python", "JavaScript")
        focus_area: Area to focus on (e.g., "performance", "readability", "security")
    """
    focus_guidance = {
        "performance": "Focus on performance optimizations, algorithmic efficiency, and resource usage.",
        "readability": "Focus on code clarity, naming conventions, and maintainability.",
        "security": "Focus on security vulnerabilities, input validation, and safe practices.",
        "general": "Provide general improvements across all areas."
    }
    
    guidance = focus_guidance.get(focus_area, focus_guidance["general"])
    
    return f"""Please analyze this {language} code and suggest improvements focusing on {focus_area}.


1. **Current State**: Describe what the code currently does
2. **Issues Identified**: List specific problems or concerns
3. **Suggested Improvements**: Provide concrete recommendations
4. **Example Refactoring**: Show improved code examples
5. **Trade-offs**: Discuss any trade-offs in your suggestions


{guidance}

Please provide specific, actionable feedback with code examples.
"""


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
    expected = 42
    
    result = my_function()
    
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
        expected = 42
        
        result = my_function()
        
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


1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **Edge Cases**: Test boundary conditions and error cases
4. **Happy Path**: Test normal, expected usage


{example}


- Aim for 80%+ code coverage
- Test all public APIs
- Test error conditions
- Test edge cases and boundary values


- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Keep tests independent
- Use fixtures/mocks appropriately
- Test one thing per test

Please generate tests following this structure.
"""


@mcp.prompt()
async def document_code(style: str = "google") -> str:
    """Template for documenting code.
    
    Args:
        style: Documentation style (e.g., "google", "numpy", "sphinx")
    """
    return f"""Please add comprehensive documentation to this code using {style} style.


- Brief description of what it does
- Parameters with types and descriptions
- Return value with type and description
- Exceptions that may be raised
- Usage examples

- Class purpose and responsibility
- Attributes with types and descriptions
- Method documentation
- Usage examples

- Module purpose
- Key components
- Usage examples


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


@mcp.tool()
async def list_prompts() -> str:
    """List all available code review prompts."""
    prompts = [
        "review_pull_request - Comprehensive PR review checklist",
        "suggest_improvements(language, focus_area) - Code improvement suggestions",
        "write_tests(test_framework) - Test writing template",
        "document_code(style) - Code documentation template",
    ]
    return "Available prompts:\n" + "\n".join(prompts)


def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
