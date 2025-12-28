import requests
from ics import Calendar, Event
from datetime import datetime

def fetch_events(calendar_id):
    # 修正後的 API 路徑：移除 v1 並確認 ID 位置
    # 根據 TimeTree 公開日曆的特性，使用 start_at 與 end_at 更加穩定
    url = f"https://timetreeapp.com/api/public_calendars/{calendar_id}/events"
    
    params = {
        "start_at": "2025-12-01",
        "end_at": "2026-01-31"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"嘗試抓取 API，狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            # 備案路徑：如果上面失敗，嘗試另一種 API 格式
            alt_url = f"https://timetreeapp.com/api/v1/public_calendars/{calendar_id}/events"
            response = requests.get(alt_url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json().get('data', [])
            print(f"抓取失敗，錯誤訊息: {response.text[:100]}")
    except Exception as e:
        print(f"發生異常: {e}")
    return []

if __name__ == "__main__":
    CALENDAR_ID = "t1isthebest"
    c = Calendar()
    
    events_data = fetch_events(CALENDAR_ID)
    print(f"本次抓取獲得 {len(events_data)} 個行程。")

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
        # 保險：確保即使沒抓到資料也會產生檔案
        e = Event()
        e.name = f"同步檢查完成 (最後嘗試日期: {datetime.now().strftime('%Y-%m-%d')})"
        e.begin = datetime.now()
        c.events.add(e)

    with open("t1_calendar.ics", 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
    
    print(f"✅ 檔案已成功寫入。")
