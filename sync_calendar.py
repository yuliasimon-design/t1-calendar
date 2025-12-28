import requests
from ics import Calendar, Event
from datetime import datetime

def fetch_monthly_events(calendar_id, year, month):
    # 使用 TimeTree 最穩定的月份 API 格式
    url = f"https://timetreeapp.com/api/v1/public_calendars/{calendar_id}/events?year={year}&month={month}"
    
    # 增加更完整的 Header，防止被 API 拒絕
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": f"https://timetreeapp.com/p/{calendar_id}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"嘗試抓取 {year}/{month}，狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('data', [])
            return events
        else:
            print(f"抓取失敗，錯誤訊息: {response.text[:100]}")
    except Exception as e:
        print(f"發生異常: {e}")
    return []

if __name__ == "__main__":
    # 確認 ID 是否為 t1isthebest
    CALENDAR_ID = "t1isthebest"
    c = Calendar()
    
    all_events_found = []
    # 抓取 12 月和 1 月
    for y, m in [(2025, 12), (2026, 1)]:
        found = fetch_monthly_events(CALENDAR_ID, y, m)
        all_events_found.extend(found)
        print(f"{y}/{m} 發現 {len(found)} 個行程")

    if all_events_found:
        for item in all_events_found:
            attrs = item.get('attributes', {})
            e = Event()
            e.name = attrs.get('title')
            e.begin = attrs.get('start_at')
            e.end = attrs.get('end_at')
            e.description = attrs.get('description', '')
            c.events.add(e)
    else:
        # 如果還是抓不到，至少留下當前時間的標記，確保檔案有更新
        e = Event()
        e.name = f"同步檢查完成 (未發現行程) - {datetime.now().strftime('%H:%M')}"
        e.begin = datetime.now()
        c.events.add(e)

    with open("t1_calendar.ics", 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
    
    print(f"✅ 處理完畢！總共寫入 {len(all_events_found)} 個行程。")
