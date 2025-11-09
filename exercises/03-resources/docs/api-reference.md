# API Reference

Complete reference for all API methods and endpoints.

## Client

### Constructor

```python
Client(api_key: str, base_url: str = "https://api.example.com")
```

Initialize a new API client.

**Parameters:**
- `api_key` (str): Your API key from the dashboard
- `base_url` (str, optional): Base URL for API requests

**Example:**
```python
client = Client(api_key="your-key")
```

## Data Methods

### get_data

```python
client.get_data(id: str) -> DataObject
```

Retrieves data by ID.

**Parameters:**
- `id` (str): Unique identifier for the data object

**Returns:**
- `DataObject`: The requested data object

**Raises:**
- `NotFoundError`: If the ID doesn't exist
- `AuthenticationError`: If the API key is invalid

**Example:**
```python
data = client.get_data(id="123")
print(data.name)
```

### list_data

```python
client.list_data(limit: int = 10, offset: int = 0) -> List[DataObject]
```

Lists all data objects with pagination.

**Parameters:**
- `limit` (int, optional): Maximum number of items to return (default: 10, max: 100)
- `offset` (int, optional): Number of items to skip (default: 0)

**Returns:**
- `List[DataObject]`: List of data objects

**Example:**
```python
items = client.list_data(limit=20, offset=0)
for item in items:
    print(item.name)
```

### create_data

```python
client.create_data(name: str, value: int, metadata: dict = None) -> DataObject
```

Creates a new data object.

**Parameters:**
- `name` (str): Name of the data object
- `value` (int): Numeric value
- `metadata` (dict, optional): Additional metadata

**Returns:**
- `DataObject`: The created data object

**Example:**
```python
new_item = client.create_data(
    name="My Item",
    value=42,
    metadata={"category": "test"}
)
```

### update_data

```python
client.update_data(id: str, name: str = None, value: int = None) -> DataObject
```

Updates an existing data object.

**Parameters:**
- `id` (str): ID of the object to update
- `name` (str, optional): New name
- `value` (int, optional): New value

**Returns:**
- `DataObject`: The updated data object

**Example:**
```python
updated = client.update_data(id="123", value=100)
```

### delete_data

```python
client.delete_data(id: str) -> bool
```

Deletes a data object.

**Parameters:**
- `id` (str): ID of the object to delete

**Returns:**
- `bool`: True if successful

**Example:**
```python
success = client.delete_data(id="123")
```

## Data Models

### DataObject

```python
class DataObject:
    id: str
    name: str
    value: int
    metadata: dict
    created_at: datetime
    updated_at: datetime
```

## Error Handling

All methods can raise the following exceptions:

- `AuthenticationError`: Invalid or missing API key
- `NotFoundError`: Resource not found
- `ValidationError`: Invalid parameters
- `RateLimitError`: Rate limit exceeded
- `ServerError`: Internal server error

**Example:**
```python
from our_sdk import Client, NotFoundError

client = Client(api_key="your-key")

try:
    data = client.get_data(id="123")
except NotFoundError:
    print("Data not found")
except Exception as e:
    print(f"Error: {e}")
```

## Rate Limits

- Free tier: 100 requests per hour
- Pro tier: 10,000 requests per hour
- Enterprise: Custom limits

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Your rate limit
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets
