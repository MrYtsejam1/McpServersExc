from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import logging
import os
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"
OFFLINE_MODE = os.getenv("MCP_OFFLINE") == "1"


async def load_offline_data(filename: str) -> dict[str, Any] | None:
    """Load data from offline JSON fixtures."""
    data_dir = Path(__file__).parent / "data" / "weather"
    filepath = data_dir / filename
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Offline fixture not found: {filepath}")
        logger.error(f"Please ensure {filename} exists in {data_dir}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return None


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    if OFFLINE_MODE:
        logger.info(f"OFFLINE MODE: Skipping network request to {url}")
        return None
    
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


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.
    
    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    if OFFLINE_MODE:
        logger.info(f"OFFLINE MODE: Loading alerts from local fixture for state {state}")
        data = await load_offline_data(f"alerts_{state}.json")
        if not data:
            return f"Offline mode: No fixture file found for state {state}. Please add data/weather/alerts_{state}.json"
    else:
        url = f"{NWS_API_BASE}/alerts/active/area/{state}"
        data = await make_nws_request(url)
    
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    
    if not data["features"]:
        return "No active alerts for this state."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    if OFFLINE_MODE:
        logger.info(f"OFFLINE MODE: Loading forecast from local fixture for {latitude},{longitude}")
        forecast_data = await load_offline_data(f"forecast_{latitude}_{longitude}.json")
        if not forecast_data:
            return f"Offline mode: No fixture file found for coordinates {latitude},{longitude}. Please add data/weather/forecast_{latitude}_{longitude}.json"
    else:
        points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        points_data = await make_nws_request(points_url)
        
        if not points_data:
            return "Unable to fetch forecast data for this location."
        
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await make_nws_request(forecast_url)
    
    if not forecast_data:
        return "Unable to fetch detailed forecast."
    
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


def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
