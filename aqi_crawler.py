#!/usr/bin/env python3
"""Air Quality Index Crawler - fetches AQI data from WAQI API"""
import os, json, time, urllib.request

TOKEN = os.environ.get("WAQI_TOKEN", "")
CITY = os.environ.get("WAQI_CITY", "here")
OUTPUT = os.environ.get("WAQI_OUTPUT", "/tmp/aqi_data.json")

def fetch_aqi():
    url = f"https://api.waqi.info/feed/{CITY}/?token={TOKEN}"
    req = urllib.request.Request(url, headers={"User-Agent": "AQI-Crawler/1.0"})
    resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
    if resp.get("status") != "ok":
        return {"error": resp.get("data", "unknown")}
    data = resp["data"]
    return {
        "aqi": data.get("aqi"),
        "city": data["city"]["name"],
        "time": data["time"]["s"],
        "iaqi": data.get("iaqi", {}),
        "dominentpol": data.get("dominentpol")
    }

if __name__ == "__main__":
    result = fetch_aqi()
    # Save to file
    with open(OUTPUT, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    # Also print summary
    if "error" not in result:
        print(f"AQI {result['aqi']} - {result['city']} ({result['time']})")
    else:
        print(f"Error: {result['error']}")
