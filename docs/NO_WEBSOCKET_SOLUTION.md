# Deploy Both Frontend & Backend on Vercel (Without WebSocket)

## The Trade-off
- ❌ No real-time WebSocket updates
- ✅ Simple deployment (both on Vercel)
- ✅ No extra platforms needed
- ✅ Polling updates instead (fetch data every 30 seconds)

## Quick Setup

### 1. Deploy Backend to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your **kokotrader** repository again
3. Configure:
   - **Project Name:** `kokotrader-backend`
   - **Root Directory:** `backend`
   - **Framework Preset:** Other
4. Add Environment Variable:
   ```
   FRONTEND_URL = https://kokotraderweb.vercel.app
   ```
5. Click **Deploy**
6. **Copy the backend URL** (e.g., `https://kokotrader-backend.vercel.app`)

### 2. Update Frontend Environment Variables

In your **frontend Vercel project**:

1. Go to **Settings** → **Environment Variables**
2. Update for **Production**:
   ```
   VITE_API_URL = https://kokotrader-backend.vercel.app
   VITE_WS_URL = 
   ```
   (Leave `VITE_WS_URL` empty - this disables WebSocket)

### 3. Modify Frontend to Use Polling

The frontend will need a small code change to poll instead of using WebSocket.

Edit `frontend/src/App.jsx` or wherever WebSocket is used:

**Find this:**
```javascript
// WebSocket connection
const connection = connectWebSocket(handleMessage, handleStatus)
```

**Replace with polling:**
```javascript
// Poll for updates every 30 seconds instead of WebSocket
useEffect(() => {
  const pollInterval = setInterval(async () => {
    try {
      const signal = await fetchSignal(selectedSymbol, selectedTimeframe)
      // Update state with signal data
    } catch (error) {
      console.error('Error fetching signal:', error)
    }
  }, 30000) // 30 seconds

  return () => clearInterval(pollInterval)
}, [selectedSymbol, selectedTimeframe])
```

### 4. Redeploy Frontend

Push changes and Vercel will auto-deploy.

## Pros & Cons

### Pros ✅
- Single platform (Vercel)
- Simple setup
- No credit cards or limits
- Both frontend and backend auto-deploy

### Cons ❌
- No real-time updates (30-second delay)
- More API calls (could hit rate limits)
- Less efficient than WebSockets

## When to Use This
- You want simplest deployment
- Real-time updates aren't critical
- You don't want to manage multiple platforms

