# Twitter to Discord Monitor

Monitors @Gold_Cryptoz for new tweets and replies, sends them to Discord, and pushes notifications via Pushover.

## Features
- 🔄 Checks Twitter every 30 seconds for new tweets/replies
- 💬 Posts to Discord with embedded tweet format
- 📱 Sends Pushover notifications (silent priority)
- 💾 Tracks seen tweets to avoid duplicates
- 🚀 Runs continuously on Render

## Deployment Instructions

### Step 1: Prepare Your Code

1. Create a new GitHub repository (can be private)
2. Upload all these files to the repository:
   - `monitor.py`
   - `requirements.txt`
   - `Dockerfile`
   - `render.yaml`
   - `.gitignore`

### Step 2: Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will automatically detect the `Dockerfile`
5. Configure the service:
   - **Name**: twitter-monitor (or whatever you prefer)
   - **Region**: Choose closest to you
   - **Branch**: main
   - **Instance Type**: Starter ($7/month)
6. Click "Create Web Service"

### Step 3: Wait for Deployment

- Render will build the Docker image (takes 5-10 minutes first time)
- Once deployed, the monitor will start automatically
- Check logs to see it working

## How It Works

1. **Every 30 seconds**, the script scrapes https://x.com/Gold_Cryptoz
2. Extracts tweets and replies using Playwright (headless browser)
3. Compares against previously seen tweet IDs
4. For each new tweet:
   - Posts to Discord webhook with embedded format
   - Sends Pushover notification
   - Saves tweet ID to prevent duplicates

## Configuration

You can modify these settings in `monitor.py`:

- `CHECK_INTERVAL = 30` - How often to check (in seconds)
- Pushover priority is set to `0` (normal, not loud)
- Discord embed color is Twitter blue

## Troubleshooting

### Monitor not finding tweets
- Twitter may have rate limited the scraper
- Check Render logs for errors
- May need to add delays or use residential proxies

### Missing notifications
- Check Discord webhook URL is correct
- Verify Pushover credentials
- Check Render logs for error messages

### High memory usage
- Playwright uses ~300-500MB RAM
- Starter plan has 512MB, should be sufficient
- If issues, reduce `CHECK_INTERVAL` to 60 seconds

## File Persistence

The `seen_tweets.json` file stores IDs of tweets already processed. On Render's free/starter plans, this file will persist as long as the service runs, but **will be lost on redeploy**. This means:

- After redeploying, it may send notifications for recent tweets again
- This is generally not a problem as it only happens on deploys
- For permanent storage, you'd need to use Render Disks (additional cost)

## Logs

View logs in Render dashboard to see:
- When tweets are detected
- Discord/Pushover delivery status
- Any errors or issues

## Cost

- Render Starter: $7/month
- Pushover: One-time $5 (already purchased)
- Total: $7/month

## Notes

- Monitor runs 24/7 automatically
- Restarts automatically if it crashes
- Twitter may block scraping - if this happens frequently, may need Twitter API access
