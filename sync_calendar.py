import requests
from ics import Calendar, Event
from datetime import datetime

def fetch_events(calendar_id):
    # 嘗試 TimeTree 公開日曆最常用的 Web API 路徑
    # 注意：這裡使用的是 'calendar' (單數)
    url = f"https://timetreeapp.com/api/public/calendar/{calendar_id}/events"
    
    params = {
        "year": 2025,
        "month": 12
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": f"https://timetreeapp.com/public_calendars/{calendar_id}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"嘗試抓取 12 月行程，狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            # 如果失敗，嘗試不帶年份月份的抓取
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('data', [])
            print(f"抓取失敗，錯誤內容: {response.text[:100]}")
    except Exception as e:
        print(f"程式異常: {e}")
    return []

if __name__ == "__main__":
    CALENDAR_ID = "t1isthebest"
    c = Calendar()
    
    # 抓取 12 月行程
    events_data = fetch_events(CALENDAR_ID)
    print(f"✅ 本次成功抓取到 {len(events_data)} 個行程。")

    if events_data:
        for item in events_data:
            attrs = item.get('attributes', {})
            e = Event()
            e.name = attrs.get('title')
            e.begin = attrs.get('start_at')
            e.end = attrs.get('end_at')
            e.description = attrs.get('description', '')
            c.events.add(e)
    else:
        # 保險佔位
        e = Event()
        e.name = f"同步檢查中 (目前 API 未回傳資料) - {datetime.now().strftime('%H:%M')}"
        e.begin = datetime.now()
        c.events.add(e)

    with open("t1_calendar.ics", 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
    
    print(f"處理結束。")
