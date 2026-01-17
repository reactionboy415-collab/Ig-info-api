from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx # Requests se fast hai aur Async support karta hai
import random
import asyncio

app = FastAPI()

# CORS Enable taaki aap kahi se bhi call kar sako
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
]

@app.get("/")
async def root():
    return {"status": "Superfast API Online", "dev": "t.me/dex4dev"}

@app.get("/api/analyze")
async def analyze(username: str = Query(..., min_length=1)):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    # 🔱 Ultimate Spoofing Headers
    fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "129477",
        "X-Forwarded-For": fake_ip,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.instagram.com/{username}/"
    }

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()['data']['user']
                
                # Proper Structured Response
                return {
                    "success": True,
                    "developer": "t.me/dex4dev",
                    "data": {
                        "profile": {
                            "full_name": data.get('full_name'),
                            "followers": data['edge_followed_by']['count'],
                            "following": data['edge_follow']['count'],
                            "bio": data.get('biography'),
                            "is_private": data.get('is_private'),
                            "profile_pic": data.get('profile_pic_url_hd')
                        },
                        "media": [
                            {
                                "type": "video" if node['node']['is_video'] else "image",
                                "url": f"https://instagram.com/p/{node['node']['shortcode']}",
                                "preview": node['node']['display_url'],
                                "likes": node['node']['edge_liked_by']['count'],
                                "views": node['node'].get('video_view_count', 0)
                            } for node in data['edge_owner_to_timeline_media']['edges']
                        ]
                    }
                }
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
            else:
                return {"success": False, "error": "Rate Limited by IG", "status": response.status_code}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
