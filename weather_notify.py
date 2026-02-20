#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天気予報LINE通知スクリプト（Render用）
- Open-Meteo APIで天気予報を取得
- LINE Messaging APIでプッシュ通知
- line-bot-sdkは使わず、requestsだけで動作
"""

import requests
import os
import sys
from datetime import datetime, timedelta, timezone

# ============================================================
# 設定（環境変数から読み込み）
# ============================================================

# LINE Messaging API
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN", "")
LINE_USER_ID = os.environ.get("LINE_USER_ID", "")

# 天気予報を取得する場所（佐賀県神埼市脊振町服巻）
LATITUDE = 33.414966
LONGITUDE = 130.352316
LOCATION_NAME = "大島産業脊振支店"

# ============================================================
# WMO Weather Code → 日本語＋絵文字 変換テーブル
# ============================================================

WEATHER_CODES = {
    0:  ("快晴",     "☀️"),
    1:  ("晴れ",     "🌤️"),
    2:  ("一部曇り", "⛅"),
    3:  ("曇り",     "☁️"),
    45: ("霧",       "🌫️"),
    48: ("霧氷",     "🌫️"),
    51: ("霧雨",     "🌧️"),
    53: ("霧雨",     "🌧️"),
    55: ("霧雨",     "🌧️"),
    56: ("氷結霧雨", "🌧️❄️"),
    57: ("氷結霧雨", "🌧️❄️"),
    61: ("小雨",     "🌧️"),
    63: ("雨",       "🌧️"),
    65: ("大雨",     "🌧️"),
    66: ("氷雨",     "🌧️❄️"),
    67: ("氷雨",     "🌧️❄️"),
    71: ("小雪",     "🌨️"),
    73: ("雪",       "❄️"),
    75: ("大雪",     "❄️"),
    77: ("霧雪",     "❄️"),
    80: ("にわか雨", "🌦️"),
    81: ("にわか雨", "🌦️"),
    82: ("激しいにわか雨", "🌦️"),
    85: ("にわか雪", "🌨️"),
    86: ("にわか雪", "🌨️"),
    95: ("雷雨",     "⛈️"),
    96: ("雷雨と雹", "⛈️"),
    99: ("雷雨と雹", "⛈️"),
}


def get_weather_forecast():
    """
    Open-Meteo APIから天気予報（時間別）を取得する。
    APIキーは不要。
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "temperature_2m,precipitation_probability,weather_code",
        "timezone": "Asia/Tokyo",
        "forecast_days": 2,
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def create_message(weather_data):
    """
    天気予報データから、LINEで送るメッセージ文字列を作成する。
    現在時刻から 0, 2, 4, 6, 8, 10, 12, 13 時間後の8行を表示。
    """
    JST = timezone(timedelta(hours=9))
    now = datetime.now(JST)

    header = f"🌤 {LOCATION_NAME}の天気予報\n"
    header += f"📅 {now.strftime('%Y/%m/%d %H:%M')} 時点\n"
    header += "━" * 16 + "\n"

    hourly = weather_data["hourly"]
    time_list = hourly["time"]
    temp_list = hourly["temperature_2m"]
    precip_list = hourly["precipitation_probability"]
    code_list = hourly["weather_code"]

    # 表示する時間オフセット（時間後）
    offsets = [0, 2, 4, 6, 8, 10, 12, 13]
    lines = []

    for offset in offsets:
        target_time = now + timedelta(hours=offset)
        # Open-Meteo は "YYYY-MM-DDTHH:00" 形式
        target_key = target_time.strftime("%Y-%m-%dT%H:00")

        try:
            idx = time_list.index(target_key)
        except ValueError:
            continue

        time_str = target_time.strftime("%H:%M")
        temp = temp_list[idx]
        precip = precip_list[idx]
        code = code_list[idx]
        desc, icon = WEATHER_CODES.get(code, ("不明", "❓"))

        lines.append(f"{time_str} {icon}{desc} {temp}°C 💧{precip}%")

    if not lines:
        return header + "（天気データを取得できませんでした）"

    return header + "\n".join(lines)


def send_line_message(message):
    """
    LINE Messaging API v2 でブロードキャストメッセージを送信する。
    公式LINEの友だち全員に一斉送信する。
    line-bot-sdk は使わず、requests だけで動作する。
    """
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    payload = {
        "messages": [
            {
                "type": "text",
                "text": message,
            }
        ],
    }
    response = requests.post(url, headers=headers, json=payload, timeout=15)

    if response.status_code != 200:
        print(f"LINE API Error [{response.status_code}]: {response.text}")
        response.raise_for_status()

    return response


def main():
    """メイン処理"""
    # 環境変数チェック
    if not CHANNEL_ACCESS_TOKEN:
        print("エラー: 環境変数 CHANNEL_ACCESS_TOKEN が設定されていません。")
        sys.exit(1)
    if not LINE_USER_ID:
        print("エラー: 環境変数 LINE_USER_ID が設定されていません。")
        sys.exit(1)

    print(f"[{datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S JST')}] 天気予報の取得を開始...")

    try:
        # 天気予報を取得
        weather_data = get_weather_forecast()
        print("天気予報データを取得しました。")

        # メッセージ作成
        message = create_message(weather_data)
        print("--- 送信メッセージ ---")
        print(message)
        print("--------------------")

        # LINE送信
        send_line_message(message)
        print("LINEに天気予報を送信しました！")

    except requests.exceptions.RequestException as e:
        error_msg = f"エラーが発生しました: {e}"
        print(error_msg)

        # エラー時もLINEに通知を試みる
        try:
            if CHANNEL_ACCESS_TOKEN and LINE_USER_ID:
                send_line_message(f"⚠️ 天気予報の取得に失敗しました\n{e}")
        except Exception:
            print("エラー通知の送信にも失敗しました。")

        sys.exit(1)

    except Exception as e:
        error_msg = f"予期せぬエラー: {e}"
        print(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
