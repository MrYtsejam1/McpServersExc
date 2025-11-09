# Exercise 2: Weather Server with External APIs

## Objective

Build a weather server that integrates with the National Weather Service API, learning how to handle external API calls, async operations, and proper error handling in MCP servers.

## What You'll Learn

- Integrating external APIs with MCP servers
- Advanced async/await patterns
- Proper error handling and user feedback
- HTTP client usage with httpx
- Real-world API integration patterns

## Background

This exercise is based on the official Anthropic MCP tutorial. You'll build a server that exposes weather data from the US National Weather Service API, which provides free weather data without requiring an API key.

## Setup

```bash
cd exercises/02-weather-server

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv add "mcp[cli]" httpx
```

## Task

Create a weather server that exposes two tools:

1. `get_alerts` - Get active weather alerts for a US state (by 2-letter state code)
2. `get_forecast` - Get weather forecast for a location (by latitude/longitude)

## Implementation Guide

### Step 1: Set up the server structure

Create `weather.py`:

```python
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"
```

### Step 2: Create helper functions

The National Weather Service API requires proper headers and error handling:

```python
async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
```

### Step 3: Implement the tools

**get_alerts tool:**

```python
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.
    
    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    
    if not data["features"]:
        return "No active alerts for this state."
    
    # Format alerts into readable text
    alerts = []
    for feature in data["features"]:
        props = feature["properties"]
        alert = f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""
        alerts.append(alert)
    
    return "\n---\n".join(alerts)
```

**get_forecast tool:**

The forecast tool requires two API calls:
1. First, get the forecast grid endpoint for the coordinates
2. Then, fetch the actual forecast from that endpoint

```python
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    
    if not points_data:
        return "Unable to fetch forecast data for this location."
    
    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    
    if not forecast_data:
        return "Unable to fetch detailed forecast."
    
    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)
    
    return "\n---\n".join(forecasts)
```

### Step 4: Add the main function

```python
def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
```

## Testing

### Test Coordinates

- San Francisco: 37.7749, -122.4194
- New York: 40.7128, -74.0060
- Chicago: 41.8781, -87.6298

### Test Queries in Claude

- "What's the weather forecast for San Francisco?" (latitude: 37.7749, longitude: -122.4194)
- "Are there any weather alerts in California?" (state: CA)
- "What are the active weather alerts in Texas?" (state: TX)

### Using MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory /absolute/path/to/02-weather-server run weather.py
```

## Best Practices Demonstrated

1. **Async HTTP Requests**: Using `httpx.AsyncClient()` for non-blocking API calls
2. **Error Handling**: Gracefully handling API failures and returning user-friendly messages
3. **Proper Headers**: Including required User-Agent and Accept headers
4. **Timeouts**: Setting reasonable timeouts to prevent hanging
5. **Data Formatting**: Converting API responses into readable text for LLMs
6. **Logging**: Using logger instead of print for debugging

## Verification Checklist

- [ ] Both tools are implemented
- [ ] API requests include proper headers
- [ ] Error handling returns meaningful messages
- [ ] Async/await is used correctly
- [ ] No `print()` statements
- [ ] Server runs without errors
- [ ] Tools work with real API data
- [ ] Forecasts show multiple periods
- [ ] Alerts display properly formatted information

## Common Pitfalls

1. **Missing User-Agent**: NWS API requires a User-Agent header
2. **Not handling None responses**: API calls can fail
3. **Forgetting async context**: httpx.AsyncClient() needs async with
4. **Poor error messages**: Users need to understand what went wrong
5. **Not limiting forecast periods**: Too much data can overwhelm the response

## Challenge Extensions

Try these additional features:

1. Add a `get_radar_station` tool to find nearby radar stations
2. Implement caching to reduce API calls
3. Add input validation for state codes
4. Create a tool to get hourly forecasts

## Solution

Check `solution.py` for a complete implementation.

## Next Steps

Move on to Exercise 3 to learn about MCP Resources:

```bash
cd ../03-resources
cat README.md
```
