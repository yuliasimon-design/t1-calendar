import requests
from ics import Calendar, Event
from datetime import datetime

def fetch_by_range(calendar_id, start_date, end_date):
    # 使用日期區間嘗試抓取資料
    url = f"https://timetreeapp.com/api/v1/public_calendars/{calendar_id}/events?start_at={start_date}&end_at={end_date}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
    except Exception as e:
        print(f"抓取失敗: {e}")
    return []

if __name__ == "__main__":
    CALENDAR_ID = "t1isthebest"
    c = Calendar()
    
    # 設定抓取 2025-12-01 到 2026-02-01 的所有行程
    events_data = fetch_by_range(CALENDAR_ID, "2025-12-01", "2026-02-01")
    total_found = len(events_data)

    if total_found > 0:
        for item in events_data:
            attrs = item.get('attributes', {})
            e = Event()
            e.name = attrs.get('title')
            e.begin = attrs.get('start_at')
            e.end = attrs.get('end_at')
            e.description = attrs.get('description', '')
            c.events.add(e)
    else:
        # 真的抓不到資料時的提示
        e = Event()
        e.name = "API 回傳 0 筆行程 (請檢查 TimeTree 源頭)"
        e.begin = datetime.now()
        c.events.add(e)

    with open("t1_calendar.ics", 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
    print(f"執行完畢！本次區間抓取共獲得 {total_found} 個行程。")
