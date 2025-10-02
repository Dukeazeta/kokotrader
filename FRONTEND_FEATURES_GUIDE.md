# Frontend Features Guide - MTF Analysis & Settings

## 🎨 New Components Added

### 1. **MTF Analysis Component** (`MTFAnalysis.jsx`)
Displays comprehensive multi-timeframe analysis data.

**Features:**
- Combined MTF signal with confidence score
- Individual timeframe breakdown (15m, 30m, 1h, etc.)
- Trend alignment indicator
- Visual alignment score meter
- Color-coded signals (green=LONG, red=SHORT, gray=HOLD)

**Where it appears:** Below the main chart, before the indicators panel

---

### 2. **Settings Panel** (`Settings.jsx`)
User-configurable parameters for signal stability and MTF analysis.

**Configurable Options:**

#### Signal Stability
- **Cooldown Period** (5-30 min): Time between signal flips
  - Day Trader: 5 min (faster signals)
  - Balanced: 10 min (recommended)
  - Swing Trader: 20 min (more stable)

- **Confidence Difference** (10-30%): Required confidence increase to flip
  - Responsive: 10% (more sensitive)
  - Balanced: 15% (recommended)
  - Cautious: 25% (very stable)

#### Multi-Timeframe Analysis
- **Enable MTF Confirmation**: Toggle MTF analysis on/off
- **Timeframes to Analyze** (2-4): Number of timeframes to check
  - 2: Faster (current + 1 higher)
  - 3: Balanced (current + 2 higher)
  - 4: Most accurate (current + 3 higher)

#### Display Options
- **Show Previous Signal**: Display signal change history
- **Auto-Refresh Interval** (10-60s): How often to update data

#### Quick Presets
- **Day Trader**: Fast signals, responsive
- **Balanced**: Recommended for most users
- **Swing Trader**: Stable, patient signals

**How to access:** Click the ⚙️ Settings button in the header

---

### 3. **Enhanced Signal Card**
Now displays signal stability status and previous signal comparison.

**New Elements:**
- ✅ **Signal Confirmed** badge (green) - Signal is stable
- 🔒 **Signal Locked** badge (yellow) - Prevented flip due to stability rules
- **Previous Signal Indicator** - Shows HOLD → LONG or SHORT → HOLD changes
- **Stability Reason** - Explains why signal changed or stayed

---

## 📱 UI Layout

```
┌─────────────────────────────────────────┐
│  Header (Koko Trader) [⚙️ Settings]    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Symbol Selector | Timeframe Selector   │
└─────────────────────────────────────────┘

┌──────────────────┬──────────────────────┐
│  Signal Card     │  Price Chart         │
│  • Stability ✅  │                      │
│  • Change Info   │                      │
│  • Entry/SL/TP   │                      │
└──────────────────┴──────────────────────┘

┌─────────────────────────────────────────┐
│  Multi-Timeframe Analysis (NEW!)        │
│  • Combined Signal                       │
│  • Timeframe Breakdown                   │
│  • Trend Alignment                       │
│  • Alignment Score                       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Technical Indicators                    │
│  • RSI, MACD, ADX, etc.                 │
└─────────────────────────────────────────┘
```

---

## 🎯 How to Use

### First Time Setup

1. **Open Settings** (⚙️ button in header)
2. **Choose a Preset**:
   - New to trading? → **Balanced**
   - Day trading? → **Day Trader**
   - Swing trading? → **Swing Trader**
3. **Click "Save Settings"**
4. Settings are saved in browser (persistent)

### Reading the MTF Analysis

**Example Display:**

```
┌─ Multi-Timeframe Analysis ──────────┐
│ Combined Signal: LONG 87%            │
│ ✅ All 3 timeframes aligned: LONG    │
│                                      │
│ Timeframe Breakdown:                 │
│ • 15m: LONG (75%) [MODERATE]         │
│ • 30m: LONG (82%) [STRONG]           │
│ • 1h:  LONG (88%) [STRONG]           │
│                                      │
│ ✅ Trend Alignment                   │
│ Higher TF (1h): BULLISH              │
│ ✅ LONG aligned with BULLISH higher TF│
│                                      │
│ Alignment Score: 87%                 │
│ ████████████████████░░░░ 87%         │
└──────────────────────────────────────┘
```

**What this means:**
- All 3 timeframes agree = **High confidence trade**
- Higher timeframe is bullish = **Trade with the trend**
- 87% alignment score = **Strong setup**
- Action: **Consider taking the LONG trade**

**Conflicting Timeframes Example:**

```
┌─ Multi-Timeframe Analysis ──────────┐
│ Combined Signal: HOLD 40%            │
│ ⚠️ Conflicting timeframes            │
│                                      │
│ Timeframe Breakdown:                 │
│ • 15m: LONG (72%) [MODERATE]         │
│ • 30m: SHORT (65%) [MODERATE]        │
│ • 1h:  SHORT (80%) [STRONG]          │
│                                      │
│ ⚠️ Trend Alignment                   │
│ Higher TF (1h): BEARISH              │
│ ❌ LONG against BEARISH higher TF    │
│                                      │
│ Alignment Score: 40%                 │
│ ████████░░░░░░░░░░░░░░ 40%          │
└──────────────────────────────────────┘
```

**What this means:**
- Timeframes disagree = **No trade**
- Lower TF says LONG but higher says SHORT = **Dangerous**
- 40% alignment = **Stay out**
- Action: **HOLD - wait for clarity**

### Understanding Signal Stability

**Green Badge (✅ Signal Confirmed):**
```
✅ Signal confirmed: Strong signal detected (88% confidence)
```
- Signal is stable and reliable
- All checks passed
- Safe to consider trading

**Yellow Badge (🔒 Signal Locked):**
```
⚠️ Signal stability lock: Cooldown period (7.3 min < 10 min)
```
- Signal wanted to flip but was blocked
- Reason shown (cooldown, insufficient confidence, etc.)
- Previous signal is being maintained
- Protects you from whipsaws

**Signal Change Indicator:**
```
Signal Changed:
HOLD → LONG
```
- Shows when signal actually flipped
- Only appears when confirmed changes happen
- Helps track signal history

---

## ⚙️ Settings Explained

### Cooldown Period

**What it does:** Minimum time required between signal flips

**Examples:**
- 5 min: Signal can flip every 5 minutes (fast, responsive)
- 10 min: Signal can flip every 10 minutes (balanced)
- 20 min: Signal can flip every 20 minutes (slow, stable)

**When to use:**
- **5 min**: Scalping, very active trading
- **10 min**: Default, works for most strategies
- **20+ min**: Swing trading, longer holds

### Confidence Difference

**What it does:** How much more confident new signal must be

**Examples:**
- 10%: Current 70% LONG → New 80% SHORT = **Allowed** (difference is 10%)
- 15%: Current 70% LONG → New 82% SHORT = **Blocked** (difference only 12%)
- 25%: Requires very strong evidence to flip

**When to use:**
- **10%**: Want responsive signals
- **15%**: Balanced (default)
- **20-25%**: Only want extremely high-confidence flips

### MTF Timeframes

**What it does:** How many timeframes to analyze

**Examples:**
- **2 TFs**: 15m + 30m (faster decisions)
- **3 TFs**: 15m + 30m + 1h (recommended)
- **4 TFs**: 15m + 30m + 1h + 4h (most thorough)

**Trade-off:**
- More timeframes = More accurate but slower API calls
- Fewer timeframes = Faster but less confirmation

---

## 💡 Pro Tips

### 1. Start with Balanced Preset
Don't fiddle with settings initially. Use "Balanced" for 1-2 weeks to understand how it works.

### 2. Watch the MTF Panel
If timeframes are always conflicting, consider:
- Trading longer timeframes
- Waiting for trending markets
- Reducing position sizes

### 3. Trust the Stability Locks
If you see 🔒 **Signal stability lock**, it's protecting you from a bad trade. Don't be frustrated - be grateful!

### 4. Check Alignment Score
- **80%+**: High-confidence setups
- **60-80%**: Moderate setups, reduce size
- **<60%**: Questionable, consider waiting

### 5. Previous Signal Indicator
If signals are flipping frequently (LONG → SHORT → LONG), increase cooldown period and confidence difference.

---

## 🔧 Advanced Usage

### For Day Traders
```
Settings:
- Cooldown: 5 minutes
- Confidence Diff: 10%
- MTF Timeframes: 2
- Auto-refresh: 10 seconds
```

### For Swing Traders
```
Settings:
- Cooldown: 20 minutes
- Confidence Diff: 20%
- MTF Timeframes: 4
- Auto-refresh: 60 seconds
```

### For Conservative Traders
```
Settings:
- Cooldown: 15 minutes
- Confidence Diff: 25%
- MTF Timeframes: 4
- Only trade when alignment score > 80%
```

---

## 🐛 Troubleshooting

**Q: MTF panel not showing**
- Check if `enableMTF` is enabled in settings
- Backend might not be returning MTF data yet
- Check browser console for errors

**Q: Settings not saving**
- Check browser localStorage is enabled
- Try clearing cache and setting again
- Settings are stored per-browser

**Q: Too many signal locks**
- Reduce cooldown period (try 5 min)
- Reduce confidence difference (try 10%)
- Your settings might be too conservative

**Q: Signals changing too often**
- Increase cooldown period (try 15-20 min)
- Increase confidence difference (try 20-25%)
- Enable MTF if disabled

**Q: Slow performance**
- Reduce MTF timeframes from 4 to 2
- Increase auto-refresh interval to 45-60s
- Backend analysis takes time (normal for 3-4 TFs)

---

## 📊 Data Flow

```
User changes settings
    ↓
Settings saved to localStorage
    ↓
Auto-refresh interval updated
    ↓
API calls made to backend
    ↓
Backend checks MTF + Stability
    ↓
Returns signal with mtf_analysis field
    ↓
Frontend displays MTF panel if enabled
    ↓
User sees complete analysis
```

---

## 🎨 Visual Indicators

### Signal Icons
- ↗️ LONG (green)
- ↘️ SHORT (red)
- ➖ HOLD (gray)

### Status Icons
- ✅ Confirmed/Aligned (green)
- ⚠️ Warning/Locked (yellow)
- ❌ Conflicting (red)
- 🔒 Stability Lock (yellow)

### Color Scheme
- **Green**: Bullish, confirmed, aligned
- **Red**: Bearish, error, conflicting
- **Yellow**: Warning, caution, hold
- **Blue**: Neutral, informational
- **Gray**: Inactive, no signal

---

## 📱 Mobile Responsiveness

All components are mobile-friendly:
- Settings panel scrolls on small screens
- MTF grid stacks vertically
- Touch-friendly buttons and sliders
- Optimized for phone/tablet

---

## 🔐 Privacy & Storage

- All settings stored **locally in your browser**
- No server-side storage
- Data never leaves your device
- Clear browser data to reset

---

## 🆘 Support

Issues with the frontend?
1. Check browser console (F12)
2. Verify backend is running and connected
3. Try "Reset to Default" in settings
4. Clear browser cache and reload

---

**Remember:** These tools are designed to help you make **better decisions**, not to make decisions for you. Always use proper risk management! 🎯

