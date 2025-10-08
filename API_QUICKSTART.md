# API Quick Start Guide

Get the Poker Chip Distribution REST API running in 2 minutes!

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd poker-chip-distribution
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows
pip install fastapi "uvicorn[standard]"
```

### 2. Start the API

```bash
python api.py
```

The API will start at: **http://localhost:8000**

### 3. View Interactive Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 Main Endpoint

### POST `/distribute`

Calculate optimal chip distribution with alternatives.

**Example Request:**

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

**Example Response:**

```json
{
  "optimal": {
    "multiplier": 0.02,
    "is_feasible": true,
    "distribution_per_player": [
      {"1": 25, "5": 18, "25": 15, "100": 7, "500": 2, "1000": 2}
    ],
    "info": {
      "bb_per_player": 50.0,
      "big_blind_chips": 100.0
    }
  },
  "alternatives": [],
  "recommendation": "✓ Optimal distribution is feasible with current inventory. Use multiplier 0.02."
}
```

## 🎯 Common Use Cases

### Force Specific Multiplier

```bash
curl -X POST "http://localhost:8000/distribute" \
  -H "Content-Type: application/json" \
  -d '{
    "num_players": 6,
    "buy_ins": [100, 100, 100, 100, 100, 100],
    "small_blind": 1,
    "big_blind": 2,
    "force_multiplier": 0.01
  }'
```

### Test Your Custom Configuration

```bash
curl -X POST "http://localhost:8000/custom-distribution" \
  -H "Content-Type: application/json" \
  -d '{
    "num_players": 6,
    "buy_ins": [10, 10, 10, 10, 10, 10],
    "multiplier": 0.01,
    "chips_per_player": {"1": 10, "5": 18, "25": 12, "100": 6},
    "small_blind": 0.1,
    "big_blind": 0.2
  }'
```

### Get Chip Inventory

```bash
curl http://localhost:8000/inventory
```

## 🐍 Python Client Example

```python
import requests

response = requests.post(
    "http://localhost:8000/distribute",
    json={
        "num_players": 6,
        "buy_ins": [100, 100, 100, 100, 100, 100],
        "small_blind": 1,
        "big_blind": 2,
        "include_alternatives": True
    }
)

result = response.json()
print(f"Multiplier: {result['optimal']['multiplier']}")
print(f"Feasible: {result['optimal']['is_feasible']}")
print(f"Recommendation: {result['recommendation']}")
```

## 🌐 JavaScript/Fetch Example

```javascript
fetch('http://localhost:8000/distribute', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    num_players: 6,
    buy_ins: [100, 100, 100, 100, 100, 100],
    small_blind: 1,
    big_blind: 2,
    include_alternatives: true
  })
})
.then(res => res.json())
.then(data => {
  console.log('Multiplier:', data.optimal.multiplier);
  console.log('Feasible:', data.optimal.is_feasible);
  console.log('Recommendation:', data.recommendation);
});
```

## 🐳 Docker Quick Start

```bash
# Build image
docker build -t poker-chip-api .

# Run container
docker run -p 8000:8000 poker-chip-api

# Or use docker-compose
docker-compose up
```

## 📚 Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/inventory` | Get chip inventory |
| PUT | `/inventory` | Update inventory |
| POST | `/distribute` | **Main endpoint - calculate distribution** |
| POST | `/custom-distribution` | Test custom chip setup |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

## 🧪 Test the API

Run the test suite:

```bash
source .venv/bin/activate
python test_api.py
```

Or test individual endpoints in the Swagger UI at http://localhost:8000/docs

## 📖 Full Documentation

- **API_README.md** - Complete API documentation
- **README.md** - Algorithm overview
- **ADVANCED_USAGE.md** - Advanced features
- **ALGORITHM.md** - Technical details

## 💡 Key Features

✅ **Optimal distribution calculation** - Automatically finds best chip multiplier
✅ **Alternative solutions** - Get 3-5 backup options when optimal has shortages
✅ **Force specific multiplier** - Lock to a known working value
✅ **Custom config testing** - Validate your exact chip setup
✅ **Inventory management** - Check and update chip availability
✅ **Interactive docs** - Try all endpoints in your browser

## 🎰 Real Example

**Your game from yesterday:**

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

Response shows it's feasible and matches 10 PLN per player perfectly! ✓

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

```bash
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

## ⚠️ Notes

- The `/inventory` endpoint modifies global state - protect it in production
- CORS is open by default (`allow_origins=["*"]`) - configure for production
- Add authentication for sensitive endpoints
- Consider rate limiting for public APIs

## 🎉 You're Ready!

Start the server and visit http://localhost:8000/docs to explore all endpoints interactively!

For more examples and detailed documentation, see **API_README.md**.