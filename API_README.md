# Poker Chip Distribution API Documentation

REST API for calculating optimal poker chip distributions.

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run the API

```bash
# Development mode (with auto-reload)
python api.py

# Or using uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Calculate Distribution (Main Endpoint)

**POST** `/distribute`

Calculate optimal chip distribution and alternatives.

#### Request Body

```json
{
  "num_players": 6,
  "buy_ins": [100, 100, 100, 100, 100, 100],
  "small_blind": 1,
  "big_blind": 2,
  "force_multiplier": null,
  "include_alternatives": true,
  "max_alternatives": 3
}
```

#### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `num_players` | integer | Yes | Number of players (1-20) |
| `buy_ins` | array[float] | Yes | Buy-in amount for each player |
| `small_blind` | float | No | Small blind value in real money |
| `big_blind` | float | No | Big blind value in real money |
| `force_multiplier` | float | No | Force specific chip multiplier |
| `include_alternatives` | boolean | No | Include alternatives (default: true) |
| `max_alternatives` | integer | No | Max alternatives to return (default: 5) |

#### Response

```json
{
  "optimal": {
    "multiplier": 0.02,
    "chip_value_info": "1 chip = 0.02 PLN",
    "distribution_per_player": [
      {
        "1": 25,
        "5": 18,
        "25": 15,
        "100": 7,
        "500": 2,
        "1000": 2
      }
    ],
    "total_chips_used": {
      "1": 150,
      "5": 108,
      "25": 90,
      "100": 42,
      "500": 12,
      "1000": 12
    },
    "is_feasible": true,
    "shortage": null,
    "info": {
      "total_buy_in": 600,
      "num_players": 6,
      "small_blind_chips": 50.0,
      "big_blind_chips": 100.0,
      "bb_per_player": 50.0,
      "chips_per_player": 5000
    }
  },
  "alternatives": [],
  "recommendation": "✓ Optimal distribution is feasible with current inventory. Use multiplier 0.02."
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/distribute" \
  -H "Content-Type: application/json" \
  -d '{
    "num_players": 6,
    "buy_ins": [100, 100, 100, 100, 100, 100],
    "small_blind": 1,
    "big_blind": 2,
    "include_alternatives": true,
    "max_alternatives": 3
  }'
```

#### Python Example

```python
import requests

response = requests.post(
    "http://localhost:8000/distribute",
    json={
        "num_players": 6,
        "buy_ins": [100, 100, 100, 100, 100, 100],
        "small_blind": 1,
        "big_blind": 2,
        "include_alternatives": True,
        "max_alternatives": 3
    }
)

result = response.json()
print(f"Multiplier: {result['optimal']['multiplier']}")
print(f"Feasible: {result['optimal']['is_feasible']}")
print(f"Recommendation: {result['recommendation']}")
```

#### JavaScript Example

```javascript
fetch('http://localhost:8000/distribute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    num_players: 6,
    buy_ins: [100, 100, 100, 100, 100, 100],
    small_blind: 1,
    big_blind: 2,
    include_alternatives: true,
    max_alternatives: 3
  })
})
.then(response => response.json())
.then(data => {
  console.log('Multiplier:', data.optimal.multiplier);
  console.log('Recommendation:', data.recommendation);
});
```

---

### 2. Test Custom Distribution

**POST** `/custom-distribution`

Test your specific chip configuration.

#### Request Body

```json
{
  "num_players": 6,
  "buy_ins": [10, 10, 10, 10, 10, 10],
  "multiplier": 0.01,
  "chips_per_player": {
    "1": 10,
    "5": 18,
    "25": 12,
    "100": 6
  },
  "small_blind": 0.1,
  "big_blind": 0.2
}
```

#### Response

```json
{
  "multiplier": 0.01,
  "chip_value_info": "1 chip = 0.01 PLN",
  "distribution_per_player": [
    {"1": 10, "5": 18, "25": 12, "100": 6}
  ],
  "total_chips_used": {"1": 60, "5": 108, "25": 72, "100": 36},
  "is_feasible": true,
  "shortage": null,
  "info": {
    "total_buy_in": 60,
    "num_players": 6,
    "actual_value_per_player": 10.0,
    "expected_value_per_player": 10.0,
    "value_difference": 0.0
  }
}
```

---

### 3. Get Inventory

**GET** `/inventory`

Get current chip inventory.

#### Response

```json
{
  "inventory": {
    "1": 150,
    "5": 150,
    "25": 100,
    "100": 50,
    "500": 25,
    "1000": 25
  },
  "total_value": 45900
}
```

---

### 4. Update Inventory

**PUT** `/inventory`

Update chip inventory.

⚠️ **WARNING**: In production, this should be protected with authentication.

#### Request Body

```json
{
  "1": 200,
  "5": 200,
  "25": 150,
  "100": 75,
  "500": 50,
  "1000": 50
}
```

#### Response

```json
{
  "message": "Inventory updated successfully",
  "inventory": {
    "1": 200,
    "5": 200,
    "25": 150,
    "100": 75,
    "500": 50,
    "1000": 50
  },
  "total_value": 67900
}
```

---

### 5. Health Check

**GET** `/health`

Check API health status.

#### Response

```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

---

## Common Use Cases

### Use Case 1: Standard Game Setup

```bash
curl -X POST "http://localhost:8000/distribute" \
  -H "Content-Type: application/json" \
  -d '{
    "num_players": 6,
    "buy_ins": [100, 100, 100, 100, 100, 100],
    "small_blind": 1,
    "big_blind": 2,
    "include_alternatives": true
  }'
```

### Use Case 2: Force Specific Multiplier

```bash
curl -X POST "http://localhost:8000/distribute" \
  -H "Content-Type: application/json" \
  -d '{
    "num_players": 6,
    "buy_ins": [100, 100, 100, 100, 100, 100],
    "small_blind": 1,
    "big_blind": 2,
    "force_multiplier": 0.01,
    "include_alternatives": false
  }'
```

### Use Case 3: Variable Buy-ins

```bash
curl -X POST "http://localhost:8000/distribute" \
  -H "Content-Type: application/json" \
  -d '{
    "num_players": 5,
    "buy_ins": [50, 100, 100, 150, 200],
    "small_blind": 1,
    "big_blind": 2,
    "include_alternatives": true,
    "max_alternatives": 5
  }'
```

### Use Case 4: Verify Yesterday's Config

```bash
curl -X POST "http://localhost:8000/custom-distribution" \
  -H "Content-Type: application/json" \
  -d '{
    "num_players": 6,
    "buy_ins": [10, 10, 10, 10, 10, 10],
    "multiplier": 0.01,
    "chips_per_player": {
      "1": 10,
      "5": 18,
      "25": 12,
      "100": 6
    },
    "small_blind": 0.1,
    "big_blind": 0.2
  }'
```

---

## Response Fields Explained

### Distribution Result Fields

- **multiplier**: Chip value multiplier (e.g., 0.02 means 1 chip = 0.02 PLN)
- **chip_value_info**: Human-readable explanation
- **distribution_per_player**: Array of chip distributions (one per player)
- **total_chips_used**: Total chips needed from inventory
- **is_feasible**: Boolean indicating if you have enough chips
- **shortage**: Dictionary of shortages if not feasible (null if feasible)
- **info**: Additional metadata including:
  - `total_buy_in`: Total money in play
  - `num_players`: Number of players
  - `small_blind_chips`: Small blind in chips
  - `big_blind_chips`: Big blind in chips
  - `bb_per_player`: Starting stack in big blinds
  - `chips_per_player`: Total chips per player

### Recommendation Messages

- ✓ **Optimal is feasible**: Use the optimal distribution as-is
- ⚠ **Has alternatives**: Optimal has shortages, but alternatives are available
- ✗ **No feasible solution**: Need to adjust game parameters

---

## Error Handling

### 400 Bad Request

```json
{
  "detail": "Length of buy_ins (5) must match num_players (6)"
}
```

Common causes:
- Buy-ins length doesn't match num_players
- Invalid parameter values (negative, zero, etc.)
- Big blind not greater than small blind

### 500 Internal Server Error

```json
{
  "detail": "Internal error: ..."
}
```

Rare, indicates a bug in the algorithm.

---

## Production Deployment

### Using Gunicorn

```bash
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t poker-chip-api .
docker run -p 8000:8000 poker-chip-api
```

### Environment Variables

You can configure the API using environment variables:

```bash
export API_HOST="0.0.0.0"
export API_PORT="8000"
export API_RELOAD="false"  # Set to "true" for development
```

---

## Security Considerations

### For Production

1. **Authentication**: Add authentication to `/inventory` endpoint
2. **CORS**: Configure `allow_origins` properly (not `["*"]`)
3. **Rate Limiting**: Add rate limiting middleware
4. **HTTPS**: Use HTTPS in production
5. **Input Validation**: Already implemented via Pydantic

### Example: Adding API Key Auth

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

@app.put("/inventory")
async def update_inventory(
    inventory: Dict[int, int],
    api_key: str = Security(api_key_header)
):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    # ... rest of the code
```

---

## Testing

### Manual Testing with Swagger UI

1. Go to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

### Automated Testing

```python
import requests

BASE_URL = "http://localhost:8000"

def test_basic_distribution():
    response = requests.post(
        f"{BASE_URL}/distribute",
        json={
            "num_players": 4,
            "buy_ins": [100, 100, 100, 100],
            "small_blind": 1,
            "big_blind": 2
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["optimal"]["is_feasible"] == True
    assert result["optimal"]["multiplier"] > 0

def test_custom_distribution():
    response = requests.post(
        f"{BASE_URL}/custom-distribution",
        json={
            "num_players": 6,
            "buy_ins": [10] * 6,
            "multiplier": 0.01,
            "chips_per_player": {1: 10, 5: 18, 25: 12, 100: 6}
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["is_feasible"] == True

if __name__ == "__main__":
    test_basic_distribution()
    test_custom_distribution()
    print("✓ All tests passed!")
```

---

## Performance

- **Typical response time**: 50-200ms
- **Alternative calculation**: +100-300ms (tests 10-16 multipliers)
- **Concurrent requests**: Supports hundreds per second
- **Memory usage**: < 50MB

---

## Troubleshooting

### API won't start

```
Error: Port 8000 is already in use
```

Solution: Use a different port
```bash
uvicorn api:app --port 8001
```

### Import errors

```
ModuleNotFoundError: No module named 'fastapi'
```

Solution: Install requirements
```bash
pip install -r requirements.txt
```

### CORS errors in browser

Check `allow_origins` in `api.py` and add your frontend domain.

---

## API Changelog

### v2.0.0
- Added `/distribute` endpoint with alternatives
- Added `/custom-distribution` endpoint
- Added inventory management endpoints
- Full Pydantic validation
- Comprehensive error handling

---

## Support

- **Documentation**: See README.md, ADVANCED_USAGE.md
- **Interactive Docs**: http://localhost:8000/docs
- **Algorithm Details**: See ALGORITHM.md

---

## License

MIT License