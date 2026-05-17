#!/usr/bin/env python3
"""全国40城市AQI爬虫 - 抓取、排序、更新README、存历史"""
import json, urllib.request, ssl, base64, os, datetime, time

ssl._create_default_https_context = ssl._create_unverified_context
TOKEN = os.environ["WAQI_TOKEN"]

CITIES = {
    "西宁":"xining","西安":"xian","石家庄":"shijiazhuang","兰州":"lanzhou",
    "呼和浩特":"hohhot","银川":"yinchuan","天津":"tianjin","青岛":"qingdao",
    "长春":"changchun","拉萨":"lhasa","重庆":"chongqing","昆明":"kunming",
    "太原":"taiyuan","郑州":"zhengzhou","北京":"beijing","成都":"chengdu",
    "澳门":"macau","沈阳":"shenyang","乌鲁木齐":"urumqi","苏州":"suzhou",
    "深圳":"shenzhen","武汉":"wuhan","济南":"jinan","上海":"shanghai",
    "大连":"dalian","合肥":"hefei","台北":"taipei","厦门":"xiamen",
    "南京":"nanjing","香港":"hongkong","杭州":"hangzhou","长沙":"changsha",
    "贵阳":"guiyang","南宁":"nanning","南昌":"nanchang","福州":"fuzhou",
    "哈尔滨":"harbin","海口":"haikou","宁波":"ningbo","广州":"guangzhou"
}

def fetch_all():
    results = []
    for cn, en in CITIES.items():
        try:
            url = f"https://api.waqi.info/feed/{en}/?token={TOKEN}"
            resp = json.loads(urllib.request.urlopen(urllib.request.Request(
                url, headers={"User-Agent":"AQI/2.0"}), timeout=10).read())
            if resp.get("status")=="ok":
                d,iaqi = resp["data"],resp["data"].get("iaqi",{})
                aqi = d.get("aqi")
                results.append({"city":cn,"aqi":aqi if aqi else "停更",
                    "aqi_num":int(aqi) if aqi and str(aqi).isdigit() else 0,
                    "pm25":iaqi.get("pm25",{}).get("v","-"),"pm10":iaqi.get("pm10",{}).get("v","-"),
                    "o3":iaqi.get("o3",{}).get("v","-"),"temp":iaqi.get("t",{}).get("v","-"),
                    "humidity":iaqi.get("h",{}).get("v","-"),"wind":iaqi.get("w",{}).get("v","-")})
            else:
                results.append({"city":cn,"aqi":"停更","aqi_num":0,"pm25":"-","pm10":"-","o3":"-","temp":"-","humidity":"-","wind":"-"})
        except:
            results.append({"city":cn,"aqi":"停更","aqi_num":0,"pm25":"-","pm10":"-","o3":"-","temp":"-","humidity":"-","wind":"-"})
    results.sort(key=lambda x:x["aqi_num"],reverse=True)
    return results

def emoji(v):
    if v=="停更" or v==0: return "⚪"
    v=int(v)
    if v<=50: return "🟢"
    if v<=100: return "🟡"
    if v<=150: return "🟠"
    return "🔴"

def build_readme(results):
    bjt = (datetime.datetime.utcnow()+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    table = "| 城市 | AQI | PM2.5 | PM10 | O₃ | 🌡温度 | 💧湿度 | 🌬风力 |\n|------|-----|-------|------|-----|--------|--------|--------|\n"
    for r in results:
        c,e = r["city"],emoji(r["aqi"])
        t = f"{r['temp']}°C" if r['temp']!='-' else '-°C'
        h = f"{r['humidity']}%" if r['humidity']!='-' else '-%'
        w = str(r['wind']) if r['wind']!='-' else '-'
        table += f"| {c} | {r['aqi']} {e} | {r['pm25']} | {r['pm10']} | {r['o3']} | {t} | {h} | {w} |\n"
    return f"""# 🌏 全国城市空气质量监测

> 数据来源: [WAQI](https://waqi.info/) · 每2小时自动更新 · 北京时间

📅 更新时间: **{bjt}** (北京时间)

{table}
---
📊 图例: 🟢 优(0-50) 🟡 良(51-100) 🟠 轻度(101-150) 🔴 中度+(>150) ⚪ 停更
""", bjt

if __name__ == "__main__":
    results = fetch_all()
    readme, bjt = build_readme(results)
    
    # Save to files
    with open("README.md","w") as f: f.write(readme)
    
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    os.makedirs("data",exist_ok=True)
    save_data = {"update_time":bjt,"data":[{k:v for k,v in r.items() if k!='aqi_num'} for r in results]}
    with open(f"data/{today}.json","w") as f: json.dump(save_data,f,ensure_ascii=False,indent=2)
    
    # Print summary
    for r in results[:5]:
        print(f"{r['city']} AQI:{r['aqi']} PM2.5:{r['pm25']}")
    print(f"\nDone. {len(results)} cities. Data saved to data/{today}.json")
