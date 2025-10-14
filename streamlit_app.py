# streamlit_app.py — UI改修版（ログインなし）
import os
from datetime import datetime

import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 基本設定
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Dispatch Gate (β)", page_icon="🗂", layout="wide")

# ちょっとした見た目調整（カード・モザイク等）
st.markdown("""
<style>
.card {padding:14px 16px; border:1px solid #e9ecef; border-radius:14px; margin-bottom:12px; background:#fff;}
.rank {font-size:44px; font-weight:800; letter-spacing:1px; line-height:1; margin:2px 0 8px 0;}
.fee {font-size:12px; color:#666; margin-top:2px;}
.label {font-size:12px; color:#6c757d; margin-right:6px;}
.meta {font-size:14px; color:#111; margin-bottom:6px;}
.company {font-size:20px; font-weight:700; margin-left:8px;}
.blurred {filter: blur(8px); text-shadow: 0 0 12px rgba(0,0,0,0.25); user-select:none;}
.right-wrap {display:flex; flex-direction:column; height:100%;}
.job {flex:1 1 auto; white-space:pre-wrap;}
.right-actions {flex:0 0 auto; text-align:right; margin-top:12px;}
.badge {display:inline-block; padding:2px 8px; font-size:12px; border-radius:999px; background:#f1f3f5; color:#495057; margin-right:6px;}
</style>
""", unsafe_allow_html=True)

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

def mask_company_hard(text: str) -> str:
    """モザイク風に表示。実体文字を残すと選択で読めることがあるため、伏字を返す"""
    if not text:
        return "非公開"
    return "非公開（モザイク）"

def mosaic_html(text: str) -> str:
    """HTML/CSSでモザイク（ぼかし）表示。選択不可にしておく"""
    safe = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<span class="company blurred">{safe}</span>'

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
    st.sidebar.write(f"企業ランク{k}: ご紹介料金 ¥{v['fee']:,}")

# -----------------------------------------------------------------------------
# 本体 UI
# -----------------------------------------------------------------------------
st.title("🗂 派遣マッチポータル（社内β）")
st.caption("社名は接続まで非公開。接続時にご紹介料金（接続料）が発生します。")

tab1, tab2, tab3 = st.tabs(["案件カタログ", "ダッシュボード", "ヘルプ"])

# ---- 案件カタログ -----------------------------------------------------------
with tab1:
    opp_df = load_df(OPP_CSV)
    com_df = load_df(COM_CSV)

    # 表示用に join（Agency には会社名モザイク）
    merged = opp_df.merge(com_df, on="company_id", how="left")

    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
    with col1:
        region = st.selectbox("地域", ["すべて"] + sorted(merged["region"].dropna().unique().tolist()))
    with col2:
        industry = st.selectbox("業種", ["すべて"] + sorted(merged["industry"].dropna().unique().tolist()))
    with col3:
        need = st.selectbox("企業ランク", ["すべて", "A", "B", "C"])
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
        fee = st.session_state["pricing"][row["need_level"]]["fee"]

        # 会社名（Admin: 通常、Agency: モザイク）
        if role == "Admin":
            company_html = f'<span class="company">{row["company_name"]}</span>'
        else:
            # 実体文字をぼかし表示（=見えない）。さらに伏字テキストを title にしない
            company_html = mosaic_html(row["company_name"])

        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)

            # レイアウト： 左（ランク＋ご紹介料金）｜中央（会社名＋メタ）｜右（仕事内容＋右下ボタン）
            left, mid, right = st.columns([1, 3.5, 3.5])

            # --- 左：企業ランク（大）＋ ご紹介料金 ---
            with left:
                st.markdown(f'<div class="rank">{row["need_level"]}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="fee"><span class="label">ご紹介料金（接続料）</span><br/>¥{fee:,}（税別）</div>',
                    unsafe_allow_html=True
                )

            # --- 中央：会社名（ランクの横に）＋ 地域/業種/職種必要人数 ---
            with mid:
                # 見出し行：ランク横に会社名
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:6px;">'
                    f'<span class="badge">企業ランク {row["need_level"]}</span>'
                    f'{company_html}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # 会社名の下に、地域 → 業種 → 職種/必要人数
                meta_block = (
                    f'<div class="meta"><span class="label">地域</span>{row["region"]}</div>'
                    f'<div class="meta"><span class="label">業種</span>{row["industry"]}</div>'
                    f'<div class="meta"><span class="label">職種/必要人数</span>{row["role"]} / {int(row["headcount_needed"])}</div>'
                )
                st.markdown(meta_block, unsafe_allow_html=True)

            # --- 右：仕事内容（要件）＆ 右下アクション ---
            with right:
                st.markdown('<div class="right-wrap">', unsafe_allow_html=True)
                # 仕事内容
                st.markdown(
                    f'<div class="job"><span class="label">仕事内容</span><br>{row["requirements"]}</div>',
                    unsafe_allow_html=True,
                )

                # 右下にアクションボタン（Agencyのみ）
                st.markdown('<div class="right-actions">', unsafe_allow_html=True)
                if role == "Agency":
                    if st.button("アプローチ ▶︎", key=f"approach_{row['opportunity_id']}"):
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
                                    "incentive_amount": None,   # 企業奨励金は非表示・非公開
                                    "notes": "",
                                }
                            ]
                        )
                        con_df = pd.concat([con_df, new], ignore_index=True)
                        con_df.to_csv(CON_CSV, index=False)
                        st.success("アプローチを送信しました。社内で確認後、企業にご連絡します。")
                else:
                    st.caption("（Admin表示）企業奨励金は社内管理でのみ扱います。")
                st.markdown('</div>', unsafe_allow_html=True)  # .right-actions
                st.markdown('</div>', unsafe_allow_html=True)  # .right-wrap

            st.markdown('</div>', unsafe_allow_html=True)  # .card

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
    colD.metric("アプローチ申請（累計）", len(con_df))

    st.dataframe(con_df.sort_values("timestamp", ascending=False), use_container_width=True)

# ---- ヘルプ -----------------------------------------------------------------
with tab3:
    st.markdown(
        """
        **Q. 社名は見えますか？**  
        A. Agencyロールでは社名はモザイク表示となり、接続完了後に開示されます。

        **Q. いつ料金が発生しますか？**  
        A. 企業と派遣会社を当社が接続した**接続時**に、ご紹介料金（接続料）が発生します。

        **Q. 企業への奨励金は？**  
        A. 派遣会社には公開しません（社内でのみ管理）。
        """
    )
