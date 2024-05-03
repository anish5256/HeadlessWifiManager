import requests
import json


def get_modem_status():
    base_url = "http://192.168.8.1"
    url = f"{base_url}/api/json"
    payload = '{"fid":"login","username":"","password":"admin","sessionId":""}'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": base_url,
        "Referer": base_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        return {"error": "Failed to login due to" + str(response.text)}
    session_id = response.json()["session"]
    payload = {
        "fid": "queryFields",
        "fields": {
            "simCardState": "invalid",
            "sn": "",
            "imei": "",
            "imsi": "",
            "mac": "",
            "iccId": "",
            "ssidName": "",
            "signalStrength": "",
            "hardwareVersion": "",
            "systemVersion": "",
            "appVersion": "",
            "wanIpAddress": "",
            "basebandVersion": "",
        },
        "sessionId": session_id,
    }

    simPayload = {
        "fid": "queryApn",
        "fields": {
            "currentApn": "cmnet",
            "apnMode": "auto",
            "currentConfig": "Default",
            "id": -1,
            "selectId": -1,
            "apnConfigs": [{"id": 0, "name": "apn1"}, {"id": 1, "name": "apn2"}],
            "pdpType": "IPv4",
            "configName": "Default",
            "apn": "cmnet",
            "authtype": -1,
            "apnUser": "",
            "apnPassword": "",
        },
        "sessionId": session_id,
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": session_id,
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": url,
        "Referer": url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    response = requests.request("POST", url, headers=headers, data=str(payload))
    sim_response = requests.request("POST", url, headers=headers, data=str(simPayload))
    data = response.json()
    data["sim_card"] = sim_response.json().get("fields", {}).get("configName", "unknown")
    return data
