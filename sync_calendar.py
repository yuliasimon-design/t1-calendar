import requests
import re
import json
from ics import Calendar, Event
from datetime import datetime

def get_calendar_data(slug):
    # 嘗試多個可能的 API 終端點
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://timetreeapp.com/public_calendars/{slug}"
    }
    
    # 1. 嘗試直接從網頁原始碼提取 (最可靠，因為網頁上看得到)
    try:
        web_url = f"https://timetreeapp.com/public_calendars/{slug}"
        res = requests.get(web_url, headers=headers)
        # 搜尋頁面中所有可能的 JSON 區塊
        json_matches = re.findall(r'<script [^>]*type="application/json"[^>]*>(.*?)</script>', res.text, re.DOTALL)
        for j in json_matches:
            try:
                content = json.loads(j)
                # 遞迴尋找包含 title 的物件
                events = []
                def extract(obj):
                    if isinstance(obj, dict):
                        if "title" in obj and "start_at" in obj:
                            events.append(obj)
                        for v in obj.values(): extract(v)
                    elif isinstance(obj, list):
                        for i in obj: extract(i)
                extract(content)
                if events:
                    print(f"✅ 從網頁原始碼挖掘成功！找到 {len(events)} 個行程片段。")
                    return events
            except:
                continue
    except Exception as e:
        print(f"❌ 網頁挖掘異常: {e}")

    # 2. 如果挖掘失敗，嘗試不同的 API 格式
    api_formats = [
        f"https://timetreeapp.com/api/public/calendar/{slug}/events?year=2025&month=12",
        f"https://timetreeapp.com/api/v1/public_calendars/{slug}/events?year=2025&month=12",
        f"https://timetreeapp.com/api/public_calendars/{slug}/events"
    ]
    
    for url in api_formats:
        try:
            print(f"🔍 嘗試請求: {url}")
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json().get('data', [])
                if data:
                    print(f"✅ API 請求成功！找到 {len(data)} 個行程。")
                    return data
        except:
            continue
            
    return []

if __name__ == "__main__":
    SLUG = "t1isthebest"
    c = Calendar()
    
    # 取得原始資料
    events_data = get_calendar_data(SLUG)
    
    if not events_data:
        print("😭 所有方法都失敗了，TimeTree 拒絕回傳資料。")
        # 建立一個測試標記
        e = Event(name=f"同步異常-檢查日誌({datetime.now().strftime('%H:%M')})", begin=datetime.now())
        c.events.add(e)
    else:
        for item in events_data:
            # 兼容不同的 JSON 格式
            title = item.get('title') or (item.get('attributes', {}).get('title'))
            start = item.get('start_at') or (item.get('attributes', {}).get('start_at'))
            end = item.get('end_at') or (item.get('attributes', {}).get('end_at'))
            
            if title and start:
                e = Event(name=title, begin=start, end=end)
                # 加入描述以防萬一
                e.description = item.get('description', '') or str(item.get('attributes', {}).get('description', ''))
                c.events.add(e)
        print(f"🎉 成功轉換並準備寫入 {len(c.events)} 個行程。")

    with open("t1_calendar.ics", 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
