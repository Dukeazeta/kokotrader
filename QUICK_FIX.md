# Quick Fix for WebSocket Disconnection on Vercel

## The Problem

**Vercel doesn't support WebSockets for serverless functions.** Your backend needs to run on a platform that supports long-lived connections.

## The Solution (Choose One)

### Option A: Deploy Backend to Railway (Recommended - 5 minutes)

Railway supports WebSockets and has a generous free tier.

1. **Go to [Railway.app](https://railway.app) and sign up/login**

2. **Create New Project → Deploy from GitHub**
   - Select your repository
   - Choose the `backend` directory as the root

3. **Railway will auto-detect Python and deploy**

4. **Add Environment Variable in Railway:**
   - Go to Variables tab
   - Add: `FRONTEND_URL` = `https://your-frontend.vercel.app`
   - (Replace with your actual Vercel frontend URL)

5. **Get your Railway URL:**
   - Click "Settings" → "Generate Domain"
   - Copy the URL (e.g., `https://kokotrader-backend.railway.app`)

6. **Update Vercel Frontend Environment Variables:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add/Update these variables for **Production**:
     ```
     VITE_API_URL = https://your-backend.railway.app
     VITE_WS_URL = wss://your-backend.railway.app/ws
     ```
   - Redeploy your frontend

7. **Done! Test your app** ✅

### Option B: Deploy Backend to Render (Alternative)

1. **Go to [Render.com](https://render.com) and sign up/login**

2. **New → Web Service**
   - Connect your GitHub repository
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variable:**
   - `FRONTEND_URL` = `https://your-frontend.vercel.app`

4. **Get your Render URL and update Vercel** (same as Railway step 6)

### Option C: Keep on Vercel (No WebSocket)

If you must use Vercel for both, WebSocket won't work, but you can use polling:

1. **Update Vercel Environment Variables for Frontend:**
   ```
   VITE_API_URL = https://your-backend.vercel.app
   VITE_WS_URL = (leave empty or remove)
   ```

2. **Update Vercel Environment Variables for Backend:**
   ```
   FRONTEND_URL = https://your-frontend.vercel.app
   ```

3. **Modify your frontend code** to check if `WS_URL` is empty and use polling instead

## Verify It's Working

After deployment, open your browser console and you should see:
- ✅ WebSocket connected (if using Railway/Render)
- API calls returning data
- No CORS errors

## Current Configuration Status

✅ Backend now uses `PORT` environment variable (required for Railway/Render)
✅ Frontend uses `VITE_API_URL` and `VITE_WS_URL` from environment
✅ CORS configured to accept requests from `FRONTEND_URL`

## Need Help?

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs

