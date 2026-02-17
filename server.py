#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天気予報LINE通知サーバー（Render Web Service用）
- Flask + APScheduler で常駐し、毎日 6:30 / 18:30 (JST) に自動実行
- /health エンドポイントでヘルスチェック対応
- /trigger エンドポイントで手動実行も可能
"""

import os
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from weather_notify import main as send_weather_notify

# ============================================================
# Flask アプリケーション
# ============================================================

app = Flask(__name__)

# スケジューラの設定
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Tokyo"))


@app.route("/")
def index():
    """トップページ（動作確認用）"""
    return jsonify({
        "status": "running",
        "service": "Weather LINE Notify",
        "description": "毎日 6:30 / 18:30 (JST) に天気予報をLINEに送信します",
    })


@app.route("/health")
def health():
    """ヘルスチェック用エンドポイント"""
    return jsonify({"status": "ok"})


@app.route("/trigger")
def trigger():
    """手動で天気予報を送信するエンドポイント"""
    try:
        send_weather_notify()
        return jsonify({"status": "success", "message": "天気予報を送信しました"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def scheduled_job():
    """スケジューラから呼び出されるジョブ"""
    print("=" * 40)
    print("スケジュール実行: 天気予報の送信を開始")
    print("=" * 40)
    try:
        send_weather_notify()
    except SystemExit:
        # main() 内の sys.exit() をキャッチ（サーバーは止めない）
        print("天気予報の送信でエラーが発生しましたが、サーバーは継続します。")
    except Exception as e:
        print(f"スケジュール実行エラー: {e}")


def start_scheduler():
    """スケジューラを開始する"""
    # 毎日 6:30 JST に実行
    scheduler.add_job(
        scheduled_job,
        CronTrigger(hour=6, minute=30, timezone=pytz.timezone("Asia/Tokyo")),
        id="morning_weather",
        name="朝の天気予報 (6:30 JST)",
        replace_existing=True,
    )

    # 毎日 18:30 JST に実行
    scheduler.add_job(
        scheduled_job,
        CronTrigger(hour=18, minute=30, timezone=pytz.timezone("Asia/Tokyo")),
        id="evening_weather",
        name="夕方の天気予報 (18:30 JST)",
        replace_existing=True,
    )

    scheduler.start()
    print("スケジューラを開始しました。")
    print("  - 朝の天気予報: 毎日 6:30 JST")
    print("  - 夕方の天気予報: 毎日 18:30 JST")

    # 次回実行時刻を表示
    for job in scheduler.get_jobs():
        print(f"  [{job.id}] 次回実行: {job.next_run_time}")


# サーバー起動時にスケジューラを開始
start_scheduler()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
