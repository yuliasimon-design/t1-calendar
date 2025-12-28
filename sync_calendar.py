import requests
from ics import Calendar, Event
from datetime import datetime

def fetch_events(calendar_id):
    # 抓取當月與下個月的資料，確保行程完整
    now = datetime.now()
    months = [
        (now.year, now.month),
        (now.year + (1 if now.month == 12 else 0), (now.month % 12) + 1)
    ]
    
    all_events = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for year, month in months:
        url = f"https://timetreeapp.com/api/v1/public_calendars/{calendar_id}/events?year={year}&month={month}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                all_events.extend(data.get('data', []))
        except Exception as e:
            print(f"無法抓取 {year}/{month}: {e}")
            
    return all_events

def create_ics(events, filename="t1_calendar.ics"):
    c = Calendar()
    for item in events:
        attrs = item.get('attributes', {})
        e = Event()
        e.name = attrs.get('title')
        e.begin = attrs.get('start_at')
        e.end = attrs.get('end_at')
        e.description = attrs.get('description', '')
        e.location = attrs.get('location', '')
        c.events.add(e)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())

if __name__ == "__main__":
    CALENDAR_ID = "t1isthebest"
    events = fetch_events(CALENDAR_ID)
    if events:
        create_ics(events)
        print(f"成功同步 {len(events)} 個行程！")
    else:
        print("未發現任何行程。")
