import asyncio
import aiohttp
from datetime import datetime

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1462469762625044705/raA1mxIotEeoDwEYgOD-64m5nwf19SKitqMneaaYiz8hprm8mh44-yq8ufYq2lyUWGQq"
PUSHOVER_USER_KEY = "ubmu2gu7mey1xvir5yym731p92mj8n"
PUSHOVER_API_TOKEN = "ag57t6qmvv45wf1fx3bqgyov3voh96"


async def test_discord():
    """Test Discord webhook"""
    print("Testing Discord webhook...")
    
    embed = {
        "title": "🧪 Test - New tweet from @Gold_Cryptoz",
        "description": "This is a test message to verify Discord integration is working!",
        "url": "https://x.com/Gold_Cryptoz",
        "color": 1942002,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "Twitter Monitor Test"
        }
    }
    
    payload = {"embeds": [embed]}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(DISCORD_WEBHOOK, json=payload) as resp:
            if resp.status == 204:
                print("✅ Discord webhook working!")
                return True
            else:
                print(f"❌ Discord webhook failed: {resp.status}")
                text = await resp.text()
                print(f"Response: {text}")
                return False


async def test_pushover():
    """Test Pushover notification"""
    print("\nTesting Pushover notification...")
    
    payload = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": "This is a test notification from your Twitter monitor!",
        "title": "🧪 Test - @Gold_Cryptoz Monitor",
        "priority": 0,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.pushover.net/1/messages.json", data=payload) as resp:
            if resp.status == 200:
                print("✅ Pushover notification sent!")
                return True
            else:
                print(f"❌ Pushover failed: {resp.status}")
                text = await resp.text()
                print(f"Response: {text}")
                return False


async def main():
    print("=" * 50)
    print("Twitter Monitor - Testing Integrations")
    print("=" * 50)
    
    discord_ok = await test_discord()
    pushover_ok = await test_pushover()
    
    print("\n" + "=" * 50)
    if discord_ok and pushover_ok:
        print("✅ All tests passed! Ready to deploy.")
    else:
        print("❌ Some tests failed. Check credentials.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
