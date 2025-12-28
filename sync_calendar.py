import requests
import re
import json
from ics import Calendar, Event
from datetime import datetime

def fetch_events_from_html(slug):
    url = f"https://timetreeapp.com/public_calendars/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        # 挖掘隱藏在網頁原始碼中的 JSON 區塊
        # 尋找包含 "events" 的 JSON 內容
        match = re.search(r'<script id="hydration-data" type="application/json">(.+?)</script>', response.text)
        
        if match:
            raw_json = match.group(1)
            data = json.loads(raw_json)
            # 根據 TimeTree 結構提取行程列表
            # 通常在 data -> publicCalendar -> events 或是類似路徑下
            events_list = []
            
            # 遞迴搜尋所有的事件物件
            def find_events(obj):
                if isinstance(obj, dict):
                    if "title" in obj and "start_at" in obj:
                        events_list.append(obj)
                    for k, v in obj.items():
                        find_events(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_events(item)
            
            find_events(data)
            print(f"✅ 深度挖掘成功！在原始碼中找到 {len(events_list)} 個原始行程片段")
            return events_list
            
    except Exception as e:
        print(f"❌ 挖掘失敗: {e}")
    return []

if __name__ == "__main__":
    SLUG = "t1isthebest"
    c = Calendar()
    
    raw_events = fetch_events_from_html(SLUG)
    
    success_count = 0
    if raw_events:
        for item in raw_events:
            # 過濾掉沒有標題的髒資料
            if not item.get('title'): continue
            
            e = Event()
            e.name = item.get('title')
            e.begin = item.get('start_at')
            e.end = item.get('end_at')
            e.description = item.get('description', '')
            c.events.add(e)
            success_count += 1
            
        print(f"🎉 總計成功轉換 {success_count} 個 T1 行程！")
    else:
        # 保險佔位
        e = Event(name=f"同步檢查(無資料回傳) - {datetime.now().strftime('%m/%d %H:%M')}", begin=datetime.now())
        c.events.add(e)
        print("😭 網頁源碼中未發現行程資料，請檢查網址是否有誤。")

    with open("t1_calendar.ics", 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
