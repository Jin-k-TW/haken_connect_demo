# Dispatch Gate (β) — 派遣マッチポータル（社内用）

**目的**: 「派遣ニーズのある企業」をカタログ化し、派遣会社が”接続申請”できる社内向けPoC。
- 企業は無料登録（協力奨励金あり）
- 派遣会社は案件の**接続時**に課金（ニーズ度A/B/Cによって変動）
- 社名は**接続まで非公開**（マスキング表示）

## 使い方（ローカル）
```bash
# 1) 仮想環境（任意）を作成後、依存をインストール
pip install -r requirements.txt

# 2) 起動
streamlit run streamlit_app.py
```

## 使い方（Streamlit Cloud / GitHub）
1. このフォルダをGitHubにpush（例: `dispatch-gate`）
2. Streamlit Cloudで新アプリを作成し、このリポジトリを選択
3. メインファイルは `streamlit_app.py` を指定

## ロールとマスキング
- サイドバーで `ロール` を切り替え
  - **Admin**（社内）: すべて閲覧可・編集可
  - **Agency**（派遣会社）: 企業名はマスキング、接続申請のみ可能

## データ構成
- `data/opportunities.csv` … 案件（企業×ニーズ×条件）
- `data/companies.csv` … 企業マスタ
- `data/agencies.csv` … 派遣会社マスタ
- `data/connections.csv` … 接続申請ログ（初回起動時に自動生成）

## 料金ロジック（初期値）
- ニーズA: 接続料金 100,000 円 / 企業奨励金 30,000 円
- ニーズB: 接続料金 50,000 円 / 企業奨励金 15,000 円
- ニーズC: 接続料金 20,000 円 / 企業奨励金 5,000 円

> 設定ページで変更可能。

## 今後の拡張
- Stripe請求書連携 / freee会計連携
- 社名伏せたままチャット機能（ブリッジ）
- AIスコアリング（成約確率予測）
- ログイン/権限（Streamlit-Authenticator等）

Made for internal PoC.
