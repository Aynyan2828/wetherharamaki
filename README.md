# 毎日決まった時間に天気予報をLINEに通知するシステム on Render

こんにちは！ このプロジェクトは、指定した場所の天気予報を、毎日決まった時間に自動でLINEに通知するためのシステムです。

ここでは、このシステムを「Render」というWebサービスに設置（デプロイ）して、実際に動かすまでの手順を、中学生にもわかるように丁寧に解説します。

## ⚙️ はじめに：必要なもの

このシステムを動かすには、いくつかのアカウントやツールが必要です。先に準備しておきましょう。

1.  **LINEアカウント**: いつも使っている個人のLINEアカウントでOKです。
2.  **GitHubアカウント**: プログラムのコードを置いておくためのサービスです。無料で作成できます。[➡️ GitHub](https://github.com/)
3.  **Renderアカウント**: 作ったプログラムを動かすためのサービスです。GitHubアカウントで簡単に登録できます。[➡️ Render](https://render.com/)

---

## STEP 1: LINEの準備（トークンとIDの取得）

LINEに通知を送るためには、「誰が」「誰に」送るのかを証明するための特別なキー（トークンとID）が必要です。少し難しいですが、画面の指示通りに進めれば大丈夫です。

1.  **LINE Developersにログイン**
    *   [LINE Developers](https://developers.line.biz/ja/) にアクセスし、自分のLINEアカウントでログインします。

2.  **プロバイダーの作成**
    *   初めて利用する場合は、「プロバイダー」というものを作成します。名前は「自分の名前」などでOKです。

3.  **チャネルの作成**
    *   プロバイダーができたら、「チャネルを作成する」ボタンを押します。
    *   「**Messaging API**」を選択します。
    *   必要な情報を入力します。
        *   **チャネルの種類**: Messaging API
        *   **プロバイダー**: 先ほど作成したもの
        *   **チャネル名**: 「天気予報通知」など、わかりやすい名前
        *   **チャネル説明**: 「自分用の天気予報通知」など
        *   **大業種・小業種**: 「個人」→「個人（IT・Webサービス）」などでOK
    *   利用規約に同意して作成します。

4.  **チャネルアクセストークンの取得**
    *   作成したチャネルの「**Messaging API設定**」タブを開きます。
    *   一番下にある「**チャネルアクセストークン**」の「発行」ボタンを押します。
    *   表示された `lineoa...` から始まる長い文字列が **`CHANNEL_ACCESS_TOKEN`** です。後で使うので、メモ帳などにコピーしておきましょう。

5.  **ユーザーIDの取得**
    *   作成したチャネル（LINE公式アカウント）を、自分のLINEで「友だち追加」します。
    *   チャネルの「Messaging API設定」タブにあるQRコードをスマホで読み取ると簡単です。
    *   次に、あなたのLINEユーザーIDを調べます。LINE Developersのページでは直接確認できないため、[こちらのサイト](https://line-user-id.info/)などを参考に、自分のLINEアカウントのユーザーID（`U`から始まる長い文字列）を調べてください。
    *   これが **`LINE_USER_ID`** です。これもメモ帳にコピーしておきましょう。

> ⚠️ **注意**: チャネルアクセストークンとユーザーIDは、パスワードと同じくらい大事な情報です。絶対に他の人に見せたり、ネット上に公開したりしないでください。

---

## STEP 2: GitHubの準備（プログラムのアップロード）

次に、動かしたいプログラムのコード一式をGitHubにアップロードします。

1.  **新しいリポジトリの作成**
    *   [GitHub](https://github.com/)にログインし、右上の「+」アイコンから「New repository」を選びます。
    *   **Repository name**: `weather-line-notify` など、好きな名前をつけます。
    *   **Public** を選択します。（PrivateでもOKですが、Renderの無料プランではPublicリポジトリが必要です）
    *   「Create repository」ボタンを押します。

2.  **ファイルのアップロード**
    *   作成したリポジトリのページで、「Add file」→「Upload files」を選びます。
    *   このプロジェクトに含まれる以下のファイルを、すべてドラッグ＆ドロップしてアップロードします。
        *   `weather_notify.py`
        *   `server.py`
        *   `requirements.txt`
        *   `render.yaml`
        *   `Procfile`
        *   `runtime.txt`
        *   `.gitignore`
        *   `README.md` （このファイルです）
    *   画面下の「Commit changes」ボタンを押して、アップロードを完了します。

これで、プログラムの置き場所ができました！

---

## STEP 3: Renderへのデプロイ（システムの設置）

いよいよ、GitHubに置いたプログラムをRenderで動かします。方法は2つあります。

| 方法 | 料金 | メリット | デメリット |
| :--- | :--- | :--- | :--- |
| **A: Cron Job** | **有料**（月$2〜） | ・設定が簡単で確実<br>・時間通りに必ず動く | ・お金がかかる |
| **B: Web Service** | **無料** | ・お金がかからない | ・設定が少し複雑<br>・サーバーが寝てしまい、動かないことがある |

**最初は、確実で簡単な「方法A: Cron Job」をおすすめします。**

### 方法A: Cron Jobで動かす（推奨）

朝と夕方の2つのタイマー（Cron Job）を設定します。

1.  **Renderにログイン**
    *   [Render](https://render.com/)にアクセスし、GitHubアカウントでログインします。

2.  **1つ目のCron Jobを作成（朝用）**
    *   ダッシュボードで「New」→「Cron Job」を選びます。
    *   「Connect a repository」で、先ほど作成した `weather-line-notify` リポジトリの「Connect」ボタンを押します。
    *   次の画面で、以下のように設定します。
        *   **Name**: `weather-notify-morning` （朝用だとわかる名前）
        *   **Region**: Singapore (Southeast Asia) など、日本に近い場所を選ぶと少し速いかも
        *   **Build Command**: `pip install -r requirements.txt`
        *   **Start Command**: `python weather_notify.py`
        *   **Schedule**: `30 21 * * *` （UTCの21:30 = 日本時間の朝6:30）
    *   「Create Cron Job」ボタンを押します。

3.  **2つ目のCron Jobを作成（夕方用）**
    *   同じ手順で、もう一つCron Jobを作成します。
        *   **Name**: `weather-notify-evening` （夕方用だとわかる名前）
        *   **Region**: （朝用と同じでOK）
        *   **Build Command**: `pip install -r requirements.txt`
        *   **Start Command**: `python weather_notify.py`
        *   **Schedule**: `30 9 * * *` （UTCの9:30 = 日本時間の夕方18:30）
    *   「Create Cron Job」ボタンを押します。

4.  **環境変数の設定**
    *   作成した2つのCron Job（`weather-notify-morning` と `weather-notify-evening`）それぞれに、LINEのキーを設定します。
    *   各Cron Jobのページの「Environment」タブを開きます。
    *   「Add Environment Variable」ボタンを2回押して、以下の2つを追加します。
        *   **Key**: `CHANNEL_ACCESS_TOKEN`, **Value**: （STEP 1でメモしたチャネルアクセストークン）
        *   **Key**: `LINE_USER_ID`, **Value**: （STEP 1でメモしたあなたのユーザーID）
    *   「Save Changes」を押します。
    *   **この作業を、朝用と夕方用の両方のCron Jobで行ってください。**

これで設定は完了です！ Renderが自動でプログラムを準備し、指定した時間になると実行してくれます。

### 方法B: Web Serviceで動かす（無料・上級者向け）

こちらは、Webサーバーを常に起動させておき、そのサーバー自身がタイマー機能（APScheduler）で天気予報を送る方法です。無料枠で動かせますが、Renderの無料Webサービスは**15分間アクセスがないとスリープ（休止）してしまう**ため、工夫が必要です。

1.  **Blueprintから作成**
    *   Renderのダッシュボードで「New」→「Blueprint」を選びます。
    *   `weather-line-notify` リポジトリの「Connect」ボタンを押します。
    *   Renderが `render.yaml` ファイルを読み込み、自動で設定を提案してくれます。しかし、このままだとCron Jobが作られてしまうので、ファイルを修正します。

2.  **`render.yaml` の修正**
    *   GitHubのリポジトリに戻り、`render.yaml` ファイルを開いて編集します。
    *   「方法A」の部分をすべてコメントアウト（行頭に `#` をつける）し、「方法B」の部分のコメントアウトを解除します。
    *   修正後、ファイルを保存（Commit changes）します。

3.  **Renderで再度設定**
    *   Renderの画面に戻り、一度キャンセルして、もう一度「New」→「Blueprint」からやり直します。
    *   今度は `weather-notify-server` という名前のWeb Serviceが提案されるはずです。
    *   「Apply」ボタンを押してサービスを作成します。

4.  **環境変数の設定**
    *   作成した `weather-notify-server` の「Environment」タブを開き、方法Aと同じように `CHANNEL_ACCESS_TOKEN` と `LINE_USER_ID` を設定します。

5.  **スリープ防止対策**
    *   このままだとサーバーが寝てしまうので、外部のサービスを使って定期的にアクセスし、起こし続ける必要があります。
    *   [UptimeRobot](https://uptimerobot.com/) などの無料サービスに登録します。
    *   RenderのWeb ServiceのURL（`https://weather-notify-server.onrender.com/health` のようなURL）を、5〜10分おきに監視するように設定します。

---

## STEP 4: 動作確認

設定がうまくできているか、手動で実行して確認してみましょう。

*   **方法A (Cron Job) の場合**: 
    *   Renderの各Cron Jobのページにある「Trigger Run」ボタンを押します。
*   **方法B (Web Service) の場合**: 
    *   Web ServiceのURLに `/trigger` をつけたアドレス（例: `https://weather-notify-server.onrender.com/trigger`）にブラウザでアクセスします。

数秒〜数十秒後、あなたのLINEに天気予報が届けば成功です！ 🎉

もし届かない場合は、Renderの「Logs」タブを見て、エラーが出ていないか確認してみてください。

## 困ったときは（トラブルシューティング）

*   **LINEに通知が届かない**
    *   環境変数 `CHANNEL_ACCESS_TOKEN` と `LINE_USER_ID` が正しく設定されているか、もう一度確認してください。コピー＆ペーストの際に、前後に余計なスペースが入っていないかもチェックしましょう。
    *   LINE Developersで作成したチャネルを、自分のLINEで「友だち追加」しているか確認してください。
*   **Renderでエラーが出る**
    *   「Logs」タブのエラーメッセージをよく読んでみましょう。`pip install` に失敗している場合は `requirements.txt` の中身が正しいか、`command not found` と出る場合は `Start Command` が正しいか確認します。
*   **時間がずれる**
    *   RenderのCron Jobの時間はUTC（協定世界時）です。日本時間（JST）にするには、-9時間で計算する必要があります。（例: 日本の朝7時は、UTCの前日22時）

これで、あなただけの天気予報通知システムの完成です！
