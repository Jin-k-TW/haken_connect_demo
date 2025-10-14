# streamlit_app.py  — loginなしのシンプル版
import os
from datetime import datetime

import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 基本設定
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Dispatch Gate (β)", page_icon="🗂", layout="wide")

DATA_DIR = "data"
OPP_CSV = os.path.join(DATA_DIR, "opportunities.csv")
COM_CSV = os.path.join(DATA_DIR, "companies.csv")
AGY_CSV = os.path.join(DATA_DIR, "agencies.csv")
CON_CSV = os.path.join(DATA_DIR, "connections.csv")

# -----------------------------------------------------------------------------
# ユーティリティ
# -----------------------------------------------------------------------------
@st.cache_data
def load_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def ensure_connections_file():
    """connections.csv が無ければ空で作成"""
    if not os.path.exists(CON_CSV):
        pd.DataFrame(
            columns=[
                "connection_id",
                "timestamp",
                "agency_id",
                "opportunity_id",
                "status",
                "fee_amount",
                "incentive_amount",
                "notes",
            ]
        ).to_csv(CON_CSV, index=False)

def mask_company(name: str) -> str:
    """社名の簡易マスキング（先頭/末尾だけ残す）"""
    if not name or len(name) <= 2:
        return "非公開"
    return name[0] + "＊" * (len(name) - 2) + name[-1]

# -----------------------------------------------------------------------------
# セッション初期化
# -----------------------------------------------------------------------------
if "pricing" not in st.session_state:
    st.session_state["pricing"] = {
        "A": {"fee": 100000, "incentive": 30000},
        "B": {"fee":  50000, "incentive": 15000},
        "C": {"fee":  20000, "incentive":  5000},
    }
if "role" not in st.session_state:
    st.session_state["role"] = "Admin"
if "selected_agency" not in st.session_state:
    st.session_state["selected_agency"] = None

ensure_connections_file()

# -----------------------------------------------------------------------------
# サイドバー
# -----------------------------------------------------------------------------
st.sidebar.title("Dispatch Gate (β)")

# ロール切替（Admin / Agency）
role = st.sidebar.selectbox("ロール", ["Admin", "Agency"], index=0, key="role")

# Agency のときは自社選択
if role == "Agency":
    try:
        agy_df = load_df(AGY_CSV)
        agy_name = st.sidebar.selectbox("派遣会社を選択", agy_df["agency_name"].tolist())
        st.session_state["selected_agency"] = agy_df.loc[
            agy_df["agency_name"] == agy_name, "agency_id"
        ].iloc[0]
    except Exception:
        st.sidebar.warning("派遣会社マスタ（data/agencies.csv）を確認してください。")
else:
    st.session_state["selected_agency"] = None

st.sidebar.markdown("---")
st.sidebar.markdown("**料金設定（参考）**")
for k, v in st.session_state["pricing"].items():
    st.sidebar.write(f"ニーズ{k}: 接続¥{v['fee']:,} / 奨励¥{v['incentive']:,}")

# -----------------------------------------------------------------------------
# 本体 UI
# -----------------------------------------------------------------------------
st.title("🗂 派遣マッチポータル（社内β）")
st.caption("社名は接続まで非公開。接続時に料金が発生します。")

tab1, tab2, tab3 = st.tabs(["案件カタログ", "ダッシュボード", "ヘルプ"])

# ---- 案件カタログ -----------------------------------------------------------
with tab1:
    opp_df = load_df(OPP_CSV)
    com_df = load_df(COM_CSV)

    # 表示用に join（Agency は社名をマスク）
    merged = opp_df.merge(com_df, on="company_id", how="left")

    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
    with col1:
        region = st.selectbox("地域", ["すべて"] + sorted(merged["region"].dropna().unique().tolist()))
    with col2:
        industry = st.selectbox("業種", ["すべて"] + sorted(merged["industry"].dropna().unique().tolist()))
    with col3:
        need = st.selectbox("ニーズ度", ["すべて", "A", "B", "C"])
    with col4:
        headcount_min = st.number_input("人数下限", value=0, min_value=0, step=1)
    with col5:
        kw = st.text_input("キーワード（職種・スキルなど）", value="")

    view = merged.copy()
    if region != "すべて":
        view = view[view["region"] == region]
    if industry != "すべて":
        view = view[view["industry"] == industry]
    if need != "すべて":
        view = view[view["need_level"] == need]
    view = view[view["headcount_needed"] >= headcount_min]
    if kw:
        kw_lower = kw.lower()
        view = view[
            view["role"].str.lower().str.contains(kw_lower)
            | view["requirements"].str.lower().str.contains(kw_lower)
        ]

    st.write(f"検索結果: **{len(view)}件**")
    for _, row in view.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])

            display_name = row["company_name"] if role == "Admin" else mask_company(row["company_name"])
            c1.subheader(display_name)
            c1.write(f"業種: {row['industry']} / 地域: {row['region']}")
            c1.write(f"職種: {row['role']} / 必要人数: {int(row['headcount_needed'])}")

            c2.metric("ニーズ度", row["need_level"])
            fee = st.session_state["pricing"][row["need_level"]]["fee"]
            incentive = st.session_state["pricing"][row["need_level"]]["incentive"]
            c2.write(f"接続料金（税別）: ¥{fee:,}")
            c2.write(f"企業奨励金（目安）: ¥{incentive:,}")

            c3.write(
                f"要件: {row['requirements'][:120]}{'...' if len(row['requirements']) > 120 else ''}"
            )

            # Agency のみ：接続申請ボタン
            if role == "Agency":
                if st.button("この案件に接続申請する ▶︎", key=f"connect_{row['opportunity_id']}"):
                    con_df = pd.read_csv(CON_CSV)
                    new = pd.DataFrame(
                        [
                            {
                                "connection_id": f"CN_{int(pd.Timestamp.utcnow().timestamp())}_{row['opportunity_id']}",
                                "timestamp": datetime.utcnow().isoformat(),
                                "agency_id": st.session_state.get("selected_agency"),
                                "opportunity_id": row["opportunity_id"],
                                "status": "requested",
                                "fee_amount": fee,
                                "incentive_amount": incentive,
                                "notes": "",
                            }
                        ]
                    )
                    con_df = pd.concat([con_df, new], ignore_index=True)
                    con_df.to_csv(CON_CSV, index=False)
                    st.success("接続申請を送信しました。社内で確認後、企業と接続します。")
            else:
                st.caption("Admin表示：編集・審査は今後の拡張で実装予定。")

# ---- ダッシュボード ---------------------------------------------------------
with tab2:
    st.subheader("ダッシュボード（サマリー）")
    opp_df = load_df(OPP_CSV)
    con_df = pd.read_csv(CON_CSV)

    need_counts = opp_df["need_level"].value_counts().reindex(["A", "B", "C"]).fillna(0).astype(int)
    colA, colB, colC, colD = st.columns(4)
    colA.metric("案件数（A）", int(need_counts.get("A", 0)))
    colB.metric("案件数（B）", int(need_counts.get("B", 0)))
    colC.metric("案件数（C）", int(need_counts.get("C", 0)))
    colD.metric("接続申請（累計）", len(con_df))

    st.dataframe(con_df.sort_values("timestamp", ascending=False), use_container_width=True)

# ---- ヘルプ -----------------------------------------------------------------
with tab3:
    st.markdown(
        """
        **Q. 社名は見えますか？**  
        A. Agencyロールでは社名はマスキング表示され、接続時に開示されます。

        **Q. いつ料金が発生しますか？**  
        A. **接続時**（企業と派遣会社を当社が繋いだ時点）に発生します。

        **Q. 企業への奨励金は？**  
        A. 契約ステータスに応じて運用。初期値はサイドバーの金額を参照ください。
        """
    )
