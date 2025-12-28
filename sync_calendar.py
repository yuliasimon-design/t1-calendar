import requests
from ics import Calendar, Event
from datetime import datetime, timedelta

def fetch_events(calendar_id):
    all_events = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # --- 修改這裡：擴大時間範圍 ---
    now = datetime.now()
    # range(-3, 7) 代表：從 3 個月前開始，一直抓到往後 6 個月 (共 10 個月)
    check_dates = [(now + timedelta(days=30*i)) for i in range(-3, 7)]
    months = sorted(list(set((d.year, d.month) for d in check_dates)))
    # ----------------------------
    
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
    if not events:
        e = Event()
        e.name = "T1 日曆同步正常 (目前範圍內無行程)"
        e.begin = datetime.now()
        e.description = "請檢查 TimeTree 網址是否有更新行程。"
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
    create_ics(events)
    print(f"處理完成，共抓取到 {len(events)} 個行程！")
