# Deployment Guide for KokoTrader

## ⚠️ Important: WebSocket Limitation on Vercel

**Vercel's serverless functions DO NOT support long-lived WebSocket connections.** You have two options:

### Option 1: Recommended - Deploy Backend Elsewhere (With WebSocket Support)

Deploy your backend to a platform that supports WebSockets:
- **Railway** (https://railway.app) - Easy Python deployment, free tier available
- **Render** (https://render.com) - Free tier available
- **Fly.io** (https://fly.io) - Good for global deployment
- **AWS EC2/ECS** - More control but requires setup
- **Digital Ocean App Platform** - Simple deployment

#### Steps:

1. **Deploy Backend to Railway (Example):**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Initialize project in backend directory
   cd backend
   railway init
   
   # Deploy
   railway up
   
   # Get your deployment URL
   railway domain
   ```

2. **Update Frontend Environment Variables in Vercel:**
   
   Go to your Vercel project settings → Environment Variables → Add:
   ```
   VITE_API_URL=https://your-backend.railway.app
   VITE_WS_URL=wss://your-backend.railway.app/ws
   ```

3. **Update Backend Environment Variable:**
   
   In Railway/Render, add environment variable:
   ```
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

4. **Redeploy Frontend:**
   ```bash
   cd frontend
   vercel --prod
   ```

### Option 2: Keep on Vercel (Without WebSocket)

If you must use Vercel for both, you'll need to disable WebSocket and use polling instead.

#### Changes needed:

1. **Update Frontend to use polling instead of WebSocket:**
   
   Edit `frontend/src/services/api.js` - remove WebSocket connection and use interval-based API calls

2. **Remove WebSocket endpoint from backend**

3. **Set environment variables in Vercel:**
   
   **Backend Project:**
   ```
   FRONTEND_URL=https://your-frontend.vercel.app
   ```
   
   **Frontend Project:**
   ```
   VITE_API_URL=https://your-backend.vercel.app
   VITE_WS_URL=  (leave empty to disable WebSocket)
   ```

## Current Setup

### Frontend (Vercel)

The frontend is already configured with environment variables:

- `VITE_API_URL` - Backend REST API URL
- `VITE_WS_URL` - Backend WebSocket URL

**Set these in Vercel Dashboard:**
1. Go to your project → Settings → Environment Variables
2. Add the variables for Production, Preview, and Development
3. Redeploy

### Backend

**If using Vercel:**
1. Create a new Vercel project for the backend
2. Set root directory to `backend`
3. Add environment variable: `FRONTEND_URL=https://your-frontend.vercel.app`
4. Note: WebSocket endpoint `/ws` will NOT work on Vercel

**If using Railway/Render:**
1. Connect your GitHub repository
2. Set root directory to `backend`
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `FRONTEND_URL=https://your-frontend.vercel.app`

## Port Configuration

- **Local Development:** Backend runs on port 8000
- **Production (Railway/Render):** Uses `$PORT` environment variable (automatically set)
- **Production (Vercel):** Port is managed by Vercel (serverless)

## CORS Configuration

The backend is configured to accept requests from:
- `localhost:3000` and `localhost:5173` (development)
- The URL specified in `FRONTEND_URL` environment variable (production)

## Deployment Checklist

- [ ] Choose deployment platform for backend (Railway/Render recommended for WebSocket)
- [ ] Deploy backend and get URL
- [ ] Update frontend environment variables in Vercel
- [ ] Update backend environment variable (FRONTEND_URL)
- [ ] Test API endpoints
- [ ] Test WebSocket connection (if using Railway/Render)
- [ ] Monitor logs for errors

## Environment Variables Summary

### Frontend (.env.production or Vercel Dashboard)
```env
VITE_API_URL=https://your-backend-url.com
VITE_WS_URL=wss://your-backend-url.com/ws
```

### Backend (Railway/Render/etc.)
```env
FRONTEND_URL=https://your-frontend.vercel.app
PORT=8000  # Usually set automatically by the platform
```

## Testing Deployment

1. **Test API Health:**
   ```bash
   curl https://your-backend-url.com/
   ```
   Should return: `{"message": "Crypto Futures Signals Bot API", "status": "running"}`

2. **Test CORS:**
   Open browser console on your frontend and check for CORS errors

3. **Test WebSocket:**
   Check browser console for WebSocket connection status

## Troubleshooting

### "WebSocket Disconnected" Error
- **On Vercel Backend:** This is expected - Vercel doesn't support WebSockets
- **Solution:** Deploy backend to Railway, Render, or similar platform

### CORS Errors
- Ensure `FRONTEND_URL` is set correctly in backend environment
- Check that URL includes protocol (`https://`) and no trailing slash

### API Connection Errors
- Verify `VITE_API_URL` in frontend environment variables
- Check backend logs for errors
- Ensure backend is running and accessible

### Port Issues
- In production, don't hardcode port 8000
- Use environment variable `PORT` (set by platform)
- Uvicorn command: `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`

