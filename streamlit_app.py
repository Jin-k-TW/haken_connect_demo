import os
from data.init_db import init_db
from data.insert_sample_data import insert_sample_data

if not os.path.exists("data/haken_connect.db"):
    init_db()
    insert_sample_data()

import os
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

# =============================================================================
# Brand
# =============================================================================
BRAND_NAME = "Haken Connect"
BRAND_COLOR = "#5EC2FE"        # Light Blue
BRAND_COLOR_DARK = "#24a9f0"
ACCENT_BG = "#F3FAFF"
MUTED = "#6b7280"

st.set_page_config(page_title=f"{BRAND_NAME}（社内β）", page_icon="🔗", layout="wide")

# =============================================================================
# CSS (Theme + components + mascot)
# =============================================================================
st.markdown(
    f"""
<style>
:root {{
  --brand: {BRAND_COLOR};
  --brand-dark: {BRAND_COLOR_DARK};
  --muted: {MUTED};
}}
.main .block-container {{
  padding-top: 0.8rem;
  padding-bottom: 3rem;
}}
body {{
  background: linear-gradient(180deg, rgba(94,194,254,0.10), rgba(94,194,254,0.02));
}}
.brand-hero {{
  position: relative;
  padding: 20px 24px 16px 24px;
  border-radius: 18px;
  background: radial-gradient(1200px 300px at 20% -10%, rgba(94,194,254,0.35), transparent),
              linear-gradient(180deg, #fff, #fff);
  border: 1px solid #e9eef5;
  box-shadow: 0 6px 24px rgba(21,126,179,0.08);
  margin-bottom: 14px;
}}
.brand-row {{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; }}
.brand-badge {{
  display:flex; align-items:center; gap:10px;
  padding:10px 14px; border-radius: 999px;
  background: {ACCENT_BG}; border: 1px solid rgba(94,194,254,0.25);
  font-weight:700; color:#0f172a;
}}
.brand-badge .dot {{
  width:10px; height:10px; border-radius:999px; background:{BRAND_COLOR};
  box-shadow: 0 0 0 3px rgba(94,194,254,0.25);
}}
.brand-sub {{ color:#334155; font-size:13px; margin-left:2px; }}
.brand-wave {{ position:absolute; inset:auto 0 0 0; height:52px; overflow:hidden; }}
.brand-wave svg {{ display:block; width:100%; height:100%; }}
.card {{padding:14px 16px; border:1px solid #e9ecef; border-radius:14px; margin-bottom:12px; background:#fff;}}
.rank {{font-size:44px; font-weight:800; letter-spacing:1px; line-height:1; margin:2px 0 8px 0; color:#0f172a;}}
.fee {{font-size:12px; color:var(--muted); margin-top:2px;}}
.label {{font-size:12px; color:#6c757d; margin-right:6px;}}
.meta {{font-size:14px; color:#111; margin-bottom:6px;}}
.company {{font-size:20px; font-weight:700; margin-left:8px; color:#0f172a;}}
.blurred {{filter: blur(8px); text-shadow: 0 0 12px rgba(0,0,0,0.25); user-select:none;}}
.right-wrap {{display:flex; flex-direction:column; height:100%;}}
.job {{flex:1 1 auto; white-space:pre-wrap;}}
.right-actions {{flex:0 0 auto; text-align:right; margin-top:12px;}}
.badge {{
  display:inline-block; padding:2px 10px; font-size:12px; border-radius:999px;
  background: {ACCENT_BG}; color:#0f172a; border:1px solid rgba(94,194,254,0.28);
}}
.stTabs [role="tablist"] button[role="tab"] {{
  border-radius: 10px 10px 0 0 !important;
  background: #ffffffaa;
  border: 1px solid #e9eef5; margin-right: 6px;
}}
.stTabs [role="tablist"] button[aria-selected="true"] {{
  border-bottom-color: #ffffff;
  color:#0f172a; box-shadow: 0 -2px 0 var(--brand) inset;
}}
.stButton>button {{
  border-radius: 10px; border:1px solid var(--brand);
  background: var(--brand); color:#fff; font-weight:700; padding: 8px 14px;
  box-shadow: 0 6px 16px rgba(94,194,254,0.35);
}}
.stButton>button:hover {{ background: var(--brand-dark); border-color: var(--brand-dark); }}
.sidebar .sidebar-content, section[data-testid="stSidebar"]>div {{
  background: linear-gradient(180deg, #ffffff, #f9fcff);
  border-right: 1px solid #e9eef5;
}}
.hc-mascot-wrap{{
  position: fixed;
  top: 14px;
  right: 18px;
  width: clamp(110px, 15vw, 180px);
  z-index: 9999;
  user-select: none;
  pointer-events: none;
  filter: drop-shadow(0 8px 22px rgba(30,144,255,.35));
  animation: hc-float 4s ease-in-out infinite;
}}
.hc-mascot-wrap svg{{
  width: 100%;
  height: auto;
  display: block;
  shape-rendering: geometricPrecision;
  text-rendering: geometricPrecision;
  image-rendering: optimizeQuality;
}}
@keyframes hc-float{{
  0%{{ transform: translateY(0) }}
  50%{{ transform: translateY(-6px) }}
  100%{{ transform: translateY(0) }}
}}
.hc-mascot-tip{{
  position: fixed;
  top: calc(14px + clamp(110px, 15vw, 180px) + 8px);
  right: 22px;
  background: #fff;
  border: 1px solid #e6f3ff;
  padding: 6px 10px;
  border-radius: 10px;
  font-size: 12px;
  color: #0f172a;
  box-shadow: 0 8px 18px rgba(94,194,254,.18);
}}
.hc-mascot-tip b{{ color:#1377c8; }}
</style>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# Data paths & DB
# =============================================================================
DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "haken_connect.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

# =============================================================================
# Utils
# =============================================================================
def load_df(table: str) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql_query(f"SELECT * FROM {table}", conn)

def insert_connection(row: dict):
    with get_conn() as conn:
        columns = ",".join(row.keys())
        placeholders = ",".join(["?"] * len(row))
        values = list(row.values())
        conn.execute(
            f"INSERT INTO connections ({columns}) VALUES ({placeholders})", values
        )
        conn.commit()

def mosaic_html(text: str) -> str:
    safe = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<span class="company blurred">{safe}</span>'

def get_mascot_svg(fill="#5EC2FE") -> str:
    return f"""
<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"
     aria-label="Haken Connect Mascot" role="img">
  <!-- Body -->
  <path d="M170 180c0-46 36-84 82-84s82 38 82 84v18c28 10 44 34 44 61
           0 38-35 68-90 68h-72c-55 0-90-30-90-68 0-29 18-54 48-62v-17z"
        fill="{fill}"/>
  <!-- Belly -->
  <ellipse cx="252" cy="274" rx="66" ry="56" fill="#fff" fill-opacity=".92"/>
  <!-- Muzzle -->
  <ellipse cx="252" cy="206" rx="34" ry="24" fill="#fff"/>
  <!-- Nose & Eyes -->
  <circle cx="268" cy="206" r="5" fill="#0f172a"/>
  <circle cx="230" cy="186" r="6" fill="#0f172a"/>
  <circle cx="286" cy="186" r="6" fill="#0f172a"/>
  <path d="M238 212c8 8 20 8 28 0" stroke="#0f172a" stroke-width="3" stroke-linecap="round"/>
  <!-- Ears -->
  <path d="M198 138c-12-10-30-12-44-4 6 18 23 28 40 26l4-22z" fill="{fill}"/>
  <path d="M306 138c12-10 30-12 44-4-6 18-23 28-40 26l-4-22z" fill="{fill}"/>
  <!-- Arms & Legs -->
  <path d="M166 258c-18 10-32 22-42 36 13-8 29-14 46-18l-4-8z" fill="{fill}"/>
  <path d="M338 258c18 10 32 22 42 36-13-8-29-14-46-18l4-8z" fill="{fill}"/>
  <path d="M206 354c-2 22-8 44-18 64 10-12 19-27 25-43l-7-21z" fill="{fill}"/>
  <path d="M298 354c2 22 8 44 18 64-10-12-19-27-25-43l7-21z" fill="{fill}"/>
  <!-- Magnifying glass (right hand) -->
  <g transform="translate(332,236) rotate(20)">
    <circle cx="44" cy="44" r="36" fill="#fff" stroke="#0f172a" stroke-width="6"/>
    <circle cx="44" cy="44" r="18" fill="{fill}" fill-opacity=".35"/>
    <rect x="38" y="76" width="12" height="34" rx="6" fill="#0f172a"/>
  </g>
  <!-- Friendly cheek -->
  <circle cx="214" cy="196" r="7" fill="#FDB4C8" fill-opacity=".9"/>
  <!-- Line accents -->
  <path d="M170 198v-18" stroke="{fill}" stroke-width="6" stroke-linecap="round"/>
  <path d="M334 198v-18" stroke="{fill}" stroke-width="6" stroke-linecap="round"/>
</svg>
""".strip()

def inject_mascot(show_tip: bool = True, color: str = BRAND_COLOR, size_css: str = None):
    svg = get_mascot_svg(color)
    wrap_style = f'style="{size_css}"' if size_css else ""
    st.markdown(f'<div class="hc-mascot-wrap" {wrap_style}>{svg}</div>', unsafe_allow_html=True)
    if show_tip:
        st.markdown(f'<div class="hc-mascot-tip">🔎 <b>{BRAND_NAME}</b> で発見！</div>', unsafe_allow_html=True)

# =============================================================================
# Session init
# =============================================================================
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

# =============================================================================
# Sidebar
# =============================================================================
st.sidebar.title(BRAND_NAME)
role = st.sidebar.selectbox("ロール", ["Admin", "Agency"], index=0, key="role")

try:
    agy_df = load_df("agencies")
    agy_name = st.sidebar.selectbox("派遣会社を選択", agy_df["agency_name"].tolist())
    st.session_state["selected_agency"] = agy_df.loc[
        agy_df["agency_name"] == agy_name, "agency_id"
    ].iloc[0]
except Exception:
    st.sidebar.warning("派遣会社マスタ（agenciesテーブル）を確認してください。")

st.sidebar.markdown("---")
st.sidebar.markdown("**料金設定（参考）**")
for k, v in st.session_state["pricing"].items():
    st.sidebar.write(f"企業ランク{k}: ご紹介料金 ¥{v['fee']:,}")

# =============================================================================
# Brand hero
# =============================================================================
def hero_svg():
    return f"""
<div class="brand-hero">
  <div class="brand-row">
    <div class="brand-badge"><span class="dot"></span> {BRAND_NAME}</div>
    <div class="brand-sub">社内β / 企業ランクと要件でスマートにアプローチ</div>
  </div>
  <div class="brand-wave">
    <svg viewBox="0 0 1440 140" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="g1" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="{BRAND_COLOR}" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="{BRAND_COLOR}" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path d="M0,60 C240,140 420,0 720,60 C1020,120 1200,40 1440,90 L1440,140 L0,140 Z" fill="url(#g1)"/>
    </svg>
  </div>
</div>
"""
st.markdown(hero_svg(), unsafe_allow_html=True)

inject_mascot(show_tip=True)

# =============================================================================
# Main
# =============================================================================
st.caption("社名は接続まで非公開。接続時にご紹介料金（接続料）が発生します。")

tab1, tab2, tab3 = st.tabs(["案件カタログ", "ダッシュボード", "ヘルプ"])

# ==== Catalog ================================================================
with tab1:
    opp_df = load_df("opportunities")
    com_df = load_df("companies")
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
        company_html = (
            f'<span class="company">{row["company_name"]}</span>'
            if role == "Admin" else mosaic_html(row["company_name"])
        )

        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            left, mid, right = st.columns([1, 3.5, 3.5])

            # Left: Rank + fee
            with left:
                st.markdown(f'<div class="rank">{row["need_level"]}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="fee"><span class="label">ご紹介料金（接続料）</span><br/>¥{fee:,}（税別）</div>',
                    unsafe_allow_html=True
                )

            # Middle: Company + meta（地域→業種→職種/人数）
            with mid:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:6px;">'
                    f'<span class="badge">企業ランク {row["need_level"]}</span>'
                    f'{company_html}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                meta_block = (
                    f'<div class="meta"><span class="label">地域</span>{row["region"]}</div>'
                    f'<div class="meta"><span class="label">業種</span>{row["industry"]}</div>'
                    f'<div class="meta"><span class="label">職種/必要人数</span>{row["role"]} / {int(row["headcount_needed"])}</div>'
                )
                st.markdown(meta_block, unsafe_allow_html=True)

            # Right: Job description + action bottom-right
            with right:
                st.markdown('<div class="right-wrap">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="job"><span class="label">仕事内容</span><br>{row["requirements"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="right-actions">', unsafe_allow_html=True)
                if role == "Agency":
                    if st.button("アプローチ ▶︎", key=f"approach_{row['opportunity_id']}"):
                        new = {
                            "connection_id": f"CN_{int(pd.Timestamp.utcnow().timestamp())}_{row['opportunity_id']}",
                            "timestamp": datetime.utcnow().isoformat(),
                            "agency_id": st.session_state.get("selected_agency"),
                            "opportunity_id": row["opportunity_id"],
                            "status": "requested",
                            "fee_amount": fee,
                            "incentive_amount": None,
                            "notes": "",
                        }
                        insert_connection(new)
                        st.success("アプローチを送信しました。社内で確認後、企業にご連絡します。")
                else:
                    st.caption("（Admin表示）企業奨励金は社内管理でのみ扱います。")
                st.markdown('</div>', unsafe_allow_html=True)  # right-actions
                st.markdown('</div>', unsafe_allow_html=True)  # right-wrap

            st.markdown('</div>', unsafe_allow_html=True)  # card

# ==== Dashboard ==============================================================
with tab2:
    st.subheader("ダッシュボード（サマリー）")
    opp_df = load_df("opportunities")
    con_df = load_df("connections")

    need_counts = opp_df["need_level"].value_counts().reindex(["A","B","C"]).fillna(0).astype(int)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("案件数（A）", int(need_counts.get("A",0)))
    c2.metric("案件数（B）", int(need_counts.get("B",0)))
    c3.metric("案件数（C）", int(need_counts.get("C",0)))
    c4.metric("アプローチ申請（累計）", len(con_df))

    st.dataframe(con_df.sort_values("timestamp", ascending=False), use_container_width=True)

# ==== Help ===================================================================
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
