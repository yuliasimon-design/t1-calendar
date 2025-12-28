import requests
from ics import Calendar, Event
from datetime import datetime, timedelta

def fetch_events(calendar_id):
    # 擴大範圍：抓取前後三個月，確保能抓到資料
    all_events = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # 產生最近 6 個月的清單
    now = datetime.now()
    check_dates = [(now + timedelta(days=30*i)) for i in range(-1, 5)]
    months = sorted(list(set((d.year, d.month) for d in check_dates)))
    
    for year, month in months:
        url = f"https://timetreeapp.com/api/v1/public_calendars/{calendar_id}/events?year={year}&month={month}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                events = data.get('data', [])
                all_events.extend(events)
                print(f"檢查 {year}/{month}: 找到 {len(events)} 個行程")
        except Exception as e:
            print(f"無法抓取 {year}/{month}: {e}")
            
    return all_events

def create_ics(events, filename="t1_calendar.ics"):
    c = Calendar()
    # 即使沒行程也加入一個「日曆已同步」的標記行程，避免檔案消失
    if not events:
        e = Event()
        e.name = "T1 日曆同步正常 (目前無行程)"
        e.begin = datetime.now()
        e.description = "目前 TimeTree 上暫無公開行程。"
        c.events.add(e)
    else:
        for item in events:
            attrs = item.get('attributes', {})
            e = Event()
            e.name = attrs.get('title')
            e.begin = attrs.get('start_at')
            e.end = attrs.get('end_at')
            e.description = attrs.get('description', '')
            c.events.add(e)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())

if __name__ == "__main__":
    CALENDAR_ID = "t1isthebest"
    events = fetch_events(CALENDAR_ID)
    create_ics(events) # 強制產生檔案
    print(f"處理完成！")
