
import streamlit as st

st.set_page_config(page_title="設定：料金と奨励金", page_icon="⚙️", layout="centered")

if "pricing" not in st.session_state:
    st.session_state["pricing"] = {
        "A": {"fee": 100000, "incentive": 30000},
        "B": {"fee":  50000, "incentive": 15000},
        "C": {"fee":  20000, "incentive":  5000},
    }

st.title("⚙️ 設定：料金と奨励金")
st.caption("接続時の料金と企業への奨励金を調整できます（セッション保存）。")

for k in ["A","B","C"]:
    st.subheader(f"ニーズ{k}")
    fee = st.number_input(f"接続料金（{k}）", value=int(st.session_state['pricing'][k]['fee']), step=1000, min_value=0)
    inc = st.number_input(f"企業奨励金（{k}）", value=int(st.session_state['pricing'][k]['incentive']), step=1000, min_value=0)
    st.session_state["pricing"][k]["fee"] = fee
    st.session_state["pricing"][k]["incentive"] = inc

st.success("設定を更新しました（セッション内）。")
