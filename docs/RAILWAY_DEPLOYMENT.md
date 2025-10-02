# Deploy Backend to Railway (100% Free - No Credit Card)

## Why Railway?
- ✅ **$5 free credit/month** (enough for this app)
- ✅ **No credit card required** for trial
- ✅ **WebSocket support**
- ✅ **Auto-deploys from GitHub**
- ✅ **Very fast deployment**

## Step-by-Step Deployment

### 1. Sign Up
1. Go to [railway.app](https://railway.app)
2. Click **"Login"** → Sign up with **GitHub**
3. Authorize Railway to access your repositories

### 2. Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **kokotrader** repository
4. Railway will scan and detect the backend

### 3. Configure Root Directory
1. After project is created, click on your service
2. Go to **"Settings"** tab
3. Find **"Root Directory"** 
4. Enter: `backend`
5. Click **"Save"**

### 4. Add Environment Variable
1. Go to **"Variables"** tab
2. Click **"+ New Variable"**
3. Add:
   ```
   FRONTEND_URL = https://kokotraderweb.vercel.app
   ```
4. Click **"Add"**

### 5. Deploy
Railway automatically deploys! Wait 2-3 minutes for the build to complete.

### 6. Generate Public URL
1. Go to **"Settings"** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. You'll get a URL like: `https://kokotrader-backend-production.up.railway.app`
5. **Copy this URL!**

### 7. Update Vercel Frontend
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your **kokotrader** project
3. Go to **Settings** → **Environment Variables**
4. Add/Update these for **Production**:
   ```
   VITE_API_URL = https://your-backend-production.up.railway.app
   VITE_WS_URL = wss://your-backend-production.up.railway.app/ws
   ```
   (Use your actual Railway URL)
5. Go to **Deployments** → Click **"..."** on latest → **"Redeploy"**

### 8. Test It!
Open your Vercel app and check the browser console:
- You should see: `✅ WebSocket connected`
- Signals should load automatically

## Usage & Limits
- **$5/month credit** = ~500 hours of runtime
- Your app will use ~$2-3/month with normal usage
- After free credit runs out, app sleeps (upgrade if needed)

## Monitoring
- View logs in Railway dashboard
- Check usage under **"Metrics"**
- Get alerts when credit is low

## Troubleshooting

### "Railway project not building"
- Check that Root Directory is set to `backend`
- Verify `requirements.txt` exists in backend folder

### "Environment variable not working"
- Make sure you clicked "Add" after entering the variable
- Redeploy: Settings → "Deploy" → "Redeploy"

### "Domain not working"
- Wait 2-3 minutes after generating domain
- Check deployment status is "Success"

## Files Already Configured
✅ `railway.json` - Railway configuration
✅ `backend/main.py` - Uses PORT environment variable
✅ `Procfile` - Start command

Everything is ready to deploy!

