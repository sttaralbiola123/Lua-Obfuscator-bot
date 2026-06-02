# 🤖 Lua Obfuscator Bot - Render Deployment Guide

## 🚀 Deploy to Render

### Step 1: Connect GitHub Repository
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub account
4. Select `sttaralbiola123/Lua-Obfuscator-bot` repository

### Step 2: Configure Deployment
1. **Name:** `lua-obfuscator-bot`
2. **Runtime:** Python 3
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `python discord_bot.py`
5. **Instance Type:** Free tier (sufficient for bot)

### Step 3: Set Environment Variables
In Render Dashboard, go to **Environment** and add:
```
DISCORD_TOKEN=your_actual_discord_bot_token_here
```

**How to get Discord Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click your bot application
3. Go to **Token** section
4. Click **Copy** (keep this SECRET!)
5. Paste in Render Environment Variables

### Step 4: Deploy
1. Click **Create Web Service**
2. Render will automatically deploy
3. Check logs for any errors
4. Once deployed, bot will start running 24/7

---

## 🔧 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'audioop'`
**Solution:** This happens with Python 3.14. The bot doesn't need voice features, so this is harmless.

**Fix Options:**
1. **Use Python 3.11/3.12** - Go to Render settings, change Python version
2. **Or** - Bot still runs despite warning (just ignore it)

### Error: Bot not responding
**Check:**
1. DISCORD_TOKEN is set correctly
2. Bot has proper permissions in Discord server
3. Check Render logs for errors: `Logs` tab in dashboard
4. Verify Discord bot is invited to server with `applications.commands` scope

### Bot stays offline
1. Check if Render instance is running (green status)
2. Check environment variables
3. Restart the service: Dashboard → **Restart**

---

## 📊 Monitoring

### View Logs
- Dashboard → Select service → **Logs** tab
- Shows real-time bot output

### Check Status
- Green = Running
- Yellow = Restarting
- Red = Error (check logs)

---

## 💰 Pricing

**Free Tier (Sufficient):**
- 0.5 GB RAM
- 0.5 CPU
- 750 hours/month (enough for always-on)
- Perfect for Discord bots

**When Free Tier Ends:**
- Instance goes to sleep if inactive for 15 min
- Manual restart required

**Upgrade to Paid ($12/month):**
- Always running
- No sleep/restart needed
- More reliability

---

## 🎯 After Deployment

### Bot Commands Available
```
/obfuscate     - Main obfuscation command
/methods       - Show all 7 methods
/example       - Show example
/help          - Show help
/info          - Show technical info
```

### Invite Bot to Your Server
1. Go to [Developer Portal](https://discord.com/developers/applications)
2. Select your bot
3. Go to **OAuth2** → **URL Generator**
4. Select scopes:
   - `bot`
   - `applications.commands`
5. Select permissions:
   - `Send Messages`
   - `Attach Files`
   - `Read Messages/View Channels`
6. Copy generated URL and open in browser
7. Select server and authorize

---

## 📝 Quick Deploy Checklist

- [ ] GitHub repo connected
- [ ] Build command set: `pip install -r requirements.txt`
- [ ] Start command set: `python discord_bot.py`
- [ ] DISCORD_TOKEN environment variable added
- [ ] Service deployed successfully (green status)
- [ ] Bot invited to Discord server
- [ ] Try `/help` command in Discord

---

## 🆘 Support

If deployment fails:
1. Check Render logs (click **Logs** tab)
2. Copy error message
3. Common issues: Missing env var, wrong start command, Python version incompatibility

---

**Deployment ready! Your bot will run 24/7 on Render.** 🎉
