# this was fully drunk-vibe-coded with claude 4.5 i have no clue what's the math behind that, there's a lot of markdown docs so it explains something ig

# Poker Chip Distribution Algorithm

An intelligent algorithm for distributing poker chips based on player buy-ins and blind structure.

**🎉 NEW: Now available as a REST API with a beautiful Web UI!** See [Quick Start](#-quick-start)

## 🚀 Quick Start

### Use the Web Interface (Easiest)

1. **Start the server:**
   ```bash
   cd poker-chip-distribution
   python3 api.py
   ```

2. **Open your browser:**
   ```
   http://localhost:8000
   ```

3. **Calculate your distribution:**
   - Enter players and buy-ins
   - Set your blind structure
   - Click "Calculate Distribution"
   - Get instant results with alternatives!

### Docker (Recommended for Deployment)

```bash
docker-compose up
```

Then visit `http://localhost:8000`

---

## Overview

This algorithm solves the problem of determining optimal chip distribution for home poker games. It automatically:

1. **Calculates the optimal chip-to-money multiplier** to ensure easy mental math
2. **Distributes chips efficiently** across available denominations
3. **Validates inventory** to ensure you have enough chips
4. **Provides clear output** showing exactly how to distribute chips to each player
5. **Finds alternative solutions** when optimal distribution doesn't work with your chips
6. **Supports forced multipliers** for consistency across games
7. **Tests custom configurations** to verify your exact chip setup

## Key Features

### 🌐 Modern Web Interface

- **Beautiful dark poker-themed UI** with gold accents
- **Real-time calculations** with instant results
- **Alternative suggestions** when inventory is limited
- **Mobile-friendly** responsive design
- **Inventory viewer** to check available chips
- See [UI_README.md](UI_README.md) for UI features and customization

### 🎯 Easy Mental Math

The algorithm prioritizes chip value multipliers that make it easy for players to calculate bets:
- Multipliers are powers of 10: `0.01`, `0.02`, `0.05`, `0.1`, `0.2`, `0.5`, `1`, `2`, `5`, `10`, etc.
- Example: If multiplier = `0.1`, then a chip with nominal `5` = `0.5 PLN` (easy to calculate!)

### 🎲 Smart Blind Structure Integration

When blind values are provided:
- Big blind becomes a "round number" in chips (e.g., 10, 20, 50, 100 chips)
- Starting stacks target 100-200 big blinds for comfortable play
- Smallest chip denomination is sized appropriately for blind posting (typically 1-5% of big blind)

### 💰 Balanced Chip Distribution

The algorithm distributes chips following poker best practices:
- **Large denominations** (35-40% of stack value) - fewer chips for bulk value
- **Medium denominations** (25-30% of stack value) - moderate amounts
- **Small denominations** (capped at 20 chips) - just enough for change-making
- Prevents giving out hundreds of tiny denomination chips

### ✅ Inventory Validation

Checks available chip inventory and reports:
- Whether distribution is feasible
- Exact shortages by denomination
- Total chips needed vs. available

## Algorithm Design

### Step 1: Determine Optimal Multiplier

The multiplier determines what `1 chip` equals in real money.

**With blinds provided:**
```
Find multiplier where:
- Big blind / multiplier = round number (5, 10, 20, 25, 50, 100, 200, 500)
- Smallest chip ≤ Big blind / 4 (usable for change)
- Starting stack ≈ 100-200 big blinds
```

**Without blinds:**
```
Target: Smallest chip = 0.5-2% of average buy-in
This keeps chip counts reasonable (not thousands of tiny chips)
```

### Step 2: Calculate Chips Needed Per Player

```
chips_needed = buy_in_amount / multiplier
```

### Step 3: Distribute Across Denominations

Working from largest to smallest chip denomination:

| Position | Denomination | Strategy | Chip Count |
|----------|-------------|----------|------------|
| Largest | 1st | 35-40% of stack value | Max 8 chips |
| 2nd Largest | 2nd | 25-30% of stack value | Max 8 chips |
| 3rd Largest | 3rd | 15-20% of stack value | Max 10 chips |
| Middle | 4-5th | Fill gaps | Max 10 chips |
| 2nd Smallest | Near blind size | Good for small bets | 10-15 chips |
| Smallest | For change | Change-making only | **Max 20 chips** |

**Important:** The smallest denomination is capped at 20 chips to prevent unrealistic distributions (e.g., 10,000 chips with nominal 1).

### Step 4: Handle Remainders

If value remains after initial distribution:
- Add chips to larger denominations (avoiding smallest)
- Maximum 5 additional chips per denomination
- Ensures exact buy-in amounts while maintaining reasonable distributions

## REST API

The algorithm is available as a REST API with a modern web interface!

### Web UI Features

- **Modern Interface**: Classy poker-themed design
- **Real-time Calculations**: Instant distribution results
- **Alternative Solutions**: Automatic suggestions for chip shortages
- **Variable Buy-ins**: Support for different player stakes
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Inventory Management**: View available chips

### API Endpoints

```bash
# Start the server
python3 api.py

# Access:
- Web UI:     http://localhost:8000
- API Docs:   http://localhost:8000/docs
- API Info:   http://localhost:8000/api
- Health:     http://localhost:8000/health
```

### API Example

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

**API Features:**
- ✅ Calculate optimal distributions
- ✅ Get alternative solutions automatically
- ✅ Test custom configurations
- ✅ Force specific multipliers
- ✅ Interactive API documentation (Swagger UI)
- ✅ Docker support
- ✅ Ready for deployment (Railway, Render, Fly.io)

**Documentation:**
- [API_QUICKSTART.md](API_QUICKSTART.md) - API basics
- [API_README.md](API_README.md) - Complete API reference
- [UI_README.md](UI_README.md) - Web interface guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy to production

---

## Python Library Usage

### Basic Example

```python
from main import distribution_algorithm, print_distribution_result

# 6 players, equal buy-ins, with blinds
result = distribution_algorithm(
    num_players=6,
    buy_ins=[100, 100, 100, 100, 100, 100],
    small_blind=1,
    big_blind=2
)

print_distribution_result(result)
```

### Advanced Features

**Force a specific multiplier:**
```python
result = distribution_algorithm(
    num_players=6,
    buy_ins=[100, 100, 100, 100, 100, 100],
    small_blind=1,
    big_blind=2,
    force_multiplier=0.01  # Use exactly this multiplier
)
```

**Find alternative solutions when optimal doesn't work:**
```python
from main import find_alternative_distributions, print_alternatives

alternatives = find_alternative_distributions(
    num_players=8,
    buy_ins=[200] * 8,
    small_blind=2,
    big_blind=5,
    max_alternatives=5
)

print_alternatives(alternatives, show_count=3)
```

**Test your custom chip configuration:**
```python
from main import custom_distribution, print_custom_distribution_result

result = custom_distribution(
    num_players=6,
    buy_ins=[10] * 6,
    multiplier=0.01,
    chips_per_player={1: 10, 5: 18, 25: 12, 100: 6},
    small_blind=0.1,
    big_blind=0.2
)

print_custom_distribution_result(result)
```

### Parameters

- `num_players` (int): Number of players in the game
- `buy_ins` (list[float]): Buy-in amount for each player in PLN (or your currency)
- `small_blind` (Optional[float]): Small blind value in real money
- `big_blind` (Optional[float]): Big blind value in real money
- `force_multiplier` (Optional[float]): Force a specific multiplier instead of auto-calculating

### Return Value

The algorithm returns a dictionary containing:

```python
{
    "multiplier": 0.02,  # 1 chip = 0.02 PLN
    "chip_value_info": "1 chip = 0.02 PLN (e.g., chip nominal 1 = 0.02 PLN)",
    "distribution_per_player": [
        {1: 20, 5: 12, 25: 10, 100: 7, 500: 2, 1000: 2},  # Player 1
        {1: 20, 5: 12, 25: 10, 100: 7, 500: 2, 1000: 2},  # Player 2
        # ... more players
    ],
    "total_chips_used": {1: 120, 5: 72, 25: 60, 100: 42, 500: 12, 1000: 12},
    "is_feasible": True,  # or False if not enough chips
    "shortage": None,  # or dict of shortages if not feasible
    "info": {
        "total_buy_in": 600,
        "num_players": 6,
        "small_blind_chips": 50.0,
        "big_blind_chips": 100.0,
        "bb_per_player": 50.0,
        "chips_per_player": 5000
    }
}
```

## Example Scenarios

### Scenario 1: Home Cash Game
```
Players: 6
Buy-in: 100 PLN each
Blinds: 1/2 PLN
```

**Result:**
- Multiplier: `0.02`
- Big blind: `100 chips`
- Starting stack: `50 BB`
- Distribution per player: `20×1, 12×5, 10×25, 7×100, 2×500, 2×1000`

### Scenario 2: Tournament Style
```
Players: 8
Buy-in: 200 PLN each
Blinds: 2/5 PLN
```

**Result:**
- Multiplier: `0.05`
- Big blind: `100 chips`
- Starting stack: `40 BB`
- Distribution per player: `20×1, 12×5, 10×25, 6×100, 2×500, 2×1000`

### Scenario 3: Casual Game (No Blinds)
```
Players: 4
Buy-ins: 50, 100, 150, 200 PLN
No blinds specified
```

**Result:**
- Multiplier: `1.0`
- Each player gets proportional chip distribution
- Smallest chips represent 1 PLN each (very easy math!)

## Available Chip Inventory

Default inventory (can be modified in `chips` dict):

```python
chips = {
    1: 150,     # 150 chips with nominal 1
    5: 150,     # 150 chips with nominal 5
    25: 100,    # 100 chips with nominal 25
    100: 50,    # 50 chips with nominal 100
    500: 25,    # 25 chips with nominal 500
    1000: 25    # 25 chips with nominal 1000
}
```

Total inventory value: 45,900 chip nominals

## Why This Approach Works

### Problem: Traditional Chip Sets

Traditional poker chip sets come with fixed denominations (e.g., $1, $5, $25, $100) which may not match your currency or blind structure.

### Solution: Dynamic Multiplier

By calculating an optimal multiplier, the algorithm adapts any chip set to any currency and blind structure while maintaining:
- ✅ Easy mental math
- ✅ Appropriate chip counts
- ✅ Playable stack depths
- ✅ Realistic distributions

### Mathematical Foundation

The algorithm balances three competing objectives:

1. **Simplicity**: Multiplier should be a round number
2. **Playability**: Stack depth should be 100-200 BB
3. **Efficiency**: Minimize small denomination chips

By scoring each possible multiplier against these criteria, it finds the optimal "sweet spot" for your specific game.

## Handling Chip Shortages

If the optimal solution requires more chips than you have:

1. **Find alternatives**: Use `find_alternative_distributions()` to get multiple options ranked by feasibility
2. **Force a multiplier**: Use `force_multiplier` parameter to test specific values you know work
3. **Test custom configs**: Use `custom_distribution()` to validate your exact chip setup before the game

See [ADVANCED_USAGE.md](ADVANCED_USAGE.md) for detailed examples.

## Running the Examples

```bash
python3 main.py
```

This runs example scenarios including:
- Standard cash games
- Forced multiplier usage
- Finding alternatives when there are shortages
- Custom distribution testing

For more examples:
```bash
python3 example_usage.py
```

## Documentation

### Web Interface
- **[UI_README.md](UI_README.md)** - Web interface features and usage
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy to Railway, Render, or other platforms

### API Documentation
- **[API_QUICKSTART.md](API_QUICKSTART.md)** - Start API in 2 minutes
- **[API_README.md](API_README.md)** - Complete API reference with examples

### Python Library Documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[ADVANCED_USAGE.md](ADVANCED_USAGE.md)** - Handle shortages, force multipliers, find alternatives
- **[ALGORITHM.md](ALGORITHM.md)** - Technical deep-dive into the algorithm design
- **[example_usage.py](example_usage.py)** - 8+ practical examples

## Deployment

### Quick Deploy to Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Railway will automatically:
- ✅ Build using the Dockerfile
- ✅ Expose your app on HTTPS
- ✅ Provide a public URL
- ✅ Handle environment variables

**Other Options:**
- **Render**: Great Docker support, automatic HTTPS
- **Fly.io**: Global deployment with edge hosting
- **Heroku**: Classic PaaS with container support

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Styling**: Custom CSS with CSS Grid and Flexbox
- **API Docs**: Swagger UI (built-in with FastAPI)
- **Deployment**: Docker, Railway, Render, Fly.io
- **Server**: Uvicorn (ASGI)

## Future Enhancements

Possible improvements:
- ✅ REST API (DONE!)
- ✅ Web UI (DONE!)
- ✅ Docker deployment (DONE!)
- Save/load custom chip configurations
- Print-friendly distribution sheets
- Tournament chip distributions with color-ups
- Rebuy and add-on handling
- Multiple currency support
- Multi-language support
- Dark/light theme toggle
- Export results as PDF

## License

MIT License - Feel free to use and modify for your poker games!
