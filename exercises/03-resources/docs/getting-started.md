# Getting Started

Welcome to our API! This guide will help you get started quickly.

## Installation

Install our SDK using pip:

```bash
pip install our-sdk
```

Or using npm for JavaScript:

```bash
npm install our-sdk
```

## Authentication

Get your API key from the dashboard:

1. Sign up at https://example.com
2. Navigate to Settings > API Keys
3. Generate a new API key
4. Keep it secure!

## Quick Example

### Python

```python
from our_sdk import Client

# Initialize the client
client = Client(api_key="your-api-key-here")

# Fetch some data
result = client.get_data(id="123")
print(result)

# Create a new item
new_item = client.create_item(
    name="My Item",
    value=42
)
print(f"Created item with ID: {new_item.id}")
```

### JavaScript

```javascript
const { Client } = require('our-sdk');

// Initialize the client
const client = new Client({ apiKey: 'your-api-key-here' });

// Fetch some data
const result = await client.getData({ id: '123' });
console.log(result);

// Create a new item
const newItem = await client.createItem({
  name: 'My Item',
  value: 42
});
console.log(`Created item with ID: ${newItem.id}`);
```

## Next Steps

- Read the [API Reference](docs://api-reference) for detailed documentation
- Check out the [FAQ](docs://faq) for common questions
- Join our community on Discord
- Follow us on Twitter for updates

## Support

Need help? Contact us:
- Email: support@example.com
- Discord: https://discord.gg/example
- GitHub Issues: https://github.com/example/sdk/issues
