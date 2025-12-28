import requests
import re
from ics import Calendar, Event
from datetime import datetime

def get_real_id(slug):
    """從網頁原始碼中破解出真正的內部 ID"""
    url = f"https://timetreeapp.com/public_calendars/{slug}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers)
        # 尋找原始碼中的 public_calendar_id
        match = re.search(r'"public_calendar_id":"([^"]+)"', response.text)
        if match:
            real_id = match.group(1)
            print(f"✅ 成功破解內部 ID: {real_id}")
            return real_id
    except Exception as e:
        print(f"❌ 破解 ID 失敗: {e}")
    return slug

def fetch_events(real_id):
    """使用內部 ID 抓取 12 月與 1 月的行程"""
    all_found = []
    # 嘗試不同的 API 路徑以確保成功
    for year, month in [(2025, 12), (2026, 1)]:
        url = f"https://timetreeapp.com/api/v1/public_calendars/{real_id}/events?year={year}&month={month}"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                events = res.json().get('data', [])
                all_found.extend(events)
                print(f"📅 {year}/{month} 抓取成功，找到 {len(events)} 個行程")
            else:
                print(f"⚠️ {year}/{month} 抓取失敗 (代碼: {res.status_code})")
        except:
            pass
    return all_found

if __name__ == "__main__":
    SLUG = "t1isthebest"
    REAL_ID = get_real_id(SLUG)
    
    c = Calendar()
    events_data = fetch_events(REAL_ID)
    
    if events_data:
        for item in events_data:
            attrs = item.get('attributes', {})
            e = Event()
            e.name = attrs.get('title')
            e.begin = attrs.get('start_at')
            e.end = attrs.get('end_at')
            e.description = attrs.get('description', '')
            c.events.add(e)
        print(f"🎉 總計成功轉換 {len(events_data)} 個 T1 行程！")
    else:
        # 如果還是空的，放入一個當前時間的標記方便測試
        e = Event(name=f"最後同步嘗試: {datetime.now().strftime('%H:%M')}", begin=datetime.now())
        c.events.add(e)
        print("😭 依然沒抓到資料，請確認網址 ID 是否正確。")

    with open("t1_calendar.ics", 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
