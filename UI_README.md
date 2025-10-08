# Poker Chip Distribution UI

A modern, classy web interface for calculating optimal poker chip distributions for home games.

![Poker Chip Distribution](https://img.shields.io/badge/Status-Production%20Ready-success)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)
![Vanilla JS](https://img.shields.io/badge/JavaScript-Vanilla-yellow)

## 🎨 Features

### Beautiful Modern Interface
- **Dark poker-themed design** with elegant gold accents
- **Smooth animations** and transitions
- **Fully responsive** - works on desktop, tablet, and mobile
- **Accessibility-focused** with proper contrast and readable fonts

### Smart Functionality
- **Real-time calculation** of optimal chip distributions
- **Alternative suggestions** when inventory is limited
- **Variable buy-ins** support for mixed-stake games
- **Advanced options** for fine-tuning (hidden by default for simplicity)
- **Inventory viewer** to check available chips
- **Visual feedback** with color-coded badges and status indicators

### User-Friendly Design
- **Intuitive form controls** with helpful tooltips
- **Clear result display** with tables and visual chips
- **Recommendation banners** guiding you to the best option
- **Error handling** with friendly error messages
- **Loading states** for better UX during calculations

## 🚀 Quick Start

### Local Development

1. **Start the server:**
   ```bash
   cd poker-chip-distribution
   python api.py
   ```

2. **Open your browser:**
   ```
   http://localhost:8000
   ```

### Docker

```bash
docker-compose up
```

Then visit `http://localhost:8000`

## 📖 Usage Guide

### Basic Calculation

1. **Enter number of players** (1-20)
2. **Set buy-in amount** (in PLN or your currency)
3. **Configure blind structure** (small blind and big blind)
4. **Click "Calculate Distribution"**

The UI will show:
- ✅ Optimal chip distribution with multiplier
- 📊 Chip counts per player in a clear table
- 💰 Total chips needed from inventory
- 🎯 Stack depths in big blinds
- ⚠️ Any inventory shortages

### Advanced Features

#### Variable Buy-ins

Enable **"Variable buy-ins per player"** to set different buy-in amounts for each player:

```
Player 1: 100 PLN
Player 2: 200 PLN
Player 3: 150 PLN
```

Perfect for:
- Players with different budgets
- Re-buys and add-ons
- Tournament structures

#### Force Multiplier

Use **Advanced Options → Force Multiplier** to lock a specific chip value:

- `0.01` = 1 chip = 0.01 PLN (1 cent)
- `0.1` = 1 chip = 0.10 PLN (10 cents)
- `1` = 1 chip = 1 PLN

Useful when:
- You want consistency across multiple games
- You have a preferred chip value
- You're matching a specific tournament structure

#### Alternative Distributions

By default, the calculator shows up to 5 alternative distributions if the optimal one has chip shortages.

Each alternative shows:
- Different multiplier
- Different chip distribution
- Feasibility status
- Stack depth comparison

## 🎯 Understanding Results

### Result Components

#### 1. Recommendation Banner
- **Green (✓)**: Optimal solution is feasible - ready to play!
- **Yellow (⚠)**: Shortages detected, alternative suggested
- **Red (✗)**: No feasible solution with current inventory

#### 2. Configuration Info
- **Multiplier**: How much each chip is worth in real money
- **Chip Values**: Human-readable explanation (e.g., "1 chip = 0.01 PLN")
- **Stack Depth**: How many big blinds each player gets
- **Total Buy-in**: Combined buy-in from all players

#### 3. Chip Distribution Table
Shows exactly how many chips each player receives:
- Color-coded by denomination (white, red, green, blue, purple, gold)
- Easy to read and follow
- Ready for chip distribution at the table

#### 4. Total Chips Needed
Summary of chips required from your inventory:
- Visual chip indicators with colors
- Quick inventory check
- Shortage warnings if applicable

### Chip Colors

The UI uses standard casino colors:
- **White**: 1 chip
- **Red**: 5 chips
- **Green**: 25 chips
- **Blue**: 100 chips
- **Purple**: 500 chips
- **Gold**: 1000 chips

## 💡 Tips & Best Practices

### For Home Games

1. **Start with the default inventory** (500 of each denomination)
2. **Use round numbers** for buy-ins (10, 20, 50, 100 PLN)
3. **Aim for 100-200 BB stack depths** for cash games
4. **Keep 20-50% extra chips** for re-buys

### For Tournaments

1. **Use force multiplier** for consistent chip values
2. **Plan for color-ups** at higher blind levels
3. **Higher stack depths** (200-300 BB) for deeper play
4. **Account for re-entries** in chip planning

### For Mixed Games

1. **Enable variable buy-ins** for different stakes
2. **Check alternatives** for flexibility
3. **Keep extra small denominations** for side pots
4. **Document your setup** for future reference

## 🔧 Customization

### Modify Default Inventory

Edit `main.py`:

```python
chips = {
    1: 500,    # 500 white chips
    5: 500,    # 500 red chips
    25: 300,   # 300 green chips
    100: 200,  # 200 blue chips
    500: 50,   # 50 purple chips
    1000: 50   # 50 gold chips
}
```

### Change Color Scheme

Edit `static/styles.css` CSS variables:

```css
:root {
    --color-primary: #2d5f3f;       /* Poker table green */
    --color-accent: #d4af37;         /* Gold accent */
    --color-background: #0f1419;     /* Dark background */
}
```

### Modify Form Defaults

Edit `static/app.js`:

```javascript
const state = {
    numPlayers: 6,        // Default players
    smallBlind: 1,        // Default small blind
    bigBlind: 2,          // Default big blind
    maxAlternatives: 5    // Max alternatives to show
};
```

## 📱 Mobile Support

The UI is fully responsive and works great on:
- 📱 **Phones** (iOS, Android)
- 📱 **Tablets** (iPad, Android tablets)
- 💻 **Laptops** (all screen sizes)
- 🖥️ **Desktops** (full-screen experience)

### Mobile Features
- Touch-friendly buttons and inputs
- Optimized layouts for small screens
- Readable text sizes
- Efficient data display

## 🌐 Browser Support

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

Uses modern web standards:
- CSS Grid & Flexbox
- CSS Custom Properties
- ES6+ JavaScript
- Fetch API

## 🎭 Design Philosophy

### Classy & Professional
- Inspired by high-end poker rooms
- Sophisticated color palette
- Smooth, subtle animations
- Premium feel without being gaudy

### User-First
- Simple by default, powerful when needed
- Clear visual hierarchy
- Helpful feedback at every step
- No jargon or complex terminology

### Performance
- Vanilla JavaScript (no framework overhead)
- Minimal dependencies
- Fast loading times
- Efficient rendering

## 🐛 Troubleshooting

### UI not loading
- Check that FastAPI is running
- Verify static files are in `/static` directory
- Check browser console for errors

### Calculations failing
- Verify API is accessible at `/distribute`
- Check network tab for failed requests
- Review API logs for errors

### Styling issues
- Hard refresh browser (Ctrl+F5 / Cmd+Shift+R)
- Clear browser cache
- Check that `styles.css` is loading

### Mobile display problems
- Check viewport meta tag in HTML
- Test responsive design in browser dev tools
- Verify media queries are working

## 📄 API Integration

The UI communicates with these endpoints:

### POST /distribute
Calculate distribution with parameters

### GET /inventory
Fetch current chip inventory

### GET /health
Check API health status

### GET /docs
Swagger API documentation

See [API_README.md](./API_README.md) for full API documentation.

## 🎨 Screenshots

### Main Interface
Clean, intuitive form with all necessary controls

### Results Display
Clear presentation of optimal and alternative distributions

### Mobile View
Fully responsive design that works on any device

### Inventory Modal
Quick view of available chips

## 🔮 Future Enhancements

Potential features for future versions:
- [ ] Save/load custom chip sets
- [ ] Print-friendly distribution sheets
- [ ] Tournament timer integration
- [ ] Blind level management
- [ ] Multi-language support
- [ ] Dark/light theme toggle
- [ ] Export results as PDF
- [ ] Share results via link

## 🤝 Contributing

Suggestions for UI improvements:
1. Open an issue describing the enhancement
2. Include mockups or examples if possible
3. Consider accessibility and mobile support
4. Keep the classy, professional aesthetic

## 📜 License

Part of the Poker Chip Distribution project.

---

**Enjoy planning your poker nights! 🎰♠♥♣♦**