import requests
from ics import Calendar, Event
from datetime import datetime

def fetch_events(calendar_id, year, month):
    url = f"https://timetreeapp.com/api/v1/public_calendars/{calendar_id}/events?year={year}&month={month}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
    except Exception as e:
        print(f"抓取 {year}/{month} 失敗: {e}")
    return []

if __name__ == "__main__":
    CALENDAR_ID = "t1isthebest"
    c = Calendar()
    
    # 強制抓取 12 月和 1 月
    target_months = [(2025, 12), (2026, 1)]
    total_found = 0

    for year, month in target_months:
        events_data = fetch_events(CALENDAR_ID, year, month)
        total_found += len(events_data)
        for item in events_data:
            attrs = item.get('attributes', {})
            e = Event()
            e.name = attrs.get('title')
            e.begin = attrs.get('start_at')
            e.end = attrs.get('end_at')
            e.description = attrs.get('description', '')
            c.events.add(e)

    # 如果還是抓不到，才放保險行程
    if total_found == 0:
        e = Event()
        e.name = "系統測試：未抓到 TimeTree 資料"
        e.begin = datetime.now()
        c.events.add(e)

    with open("t1_calendar.ics", 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
    print(f"完成！共抓到 {total_found} 個行程。")
