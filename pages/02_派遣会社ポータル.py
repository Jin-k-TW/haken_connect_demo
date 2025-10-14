
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="派遣会社ポータル", page_icon="🏢", layout="wide")

DATA_DIR = "data"
AGY_CSV = os.path.join(DATA_DIR, "agencies.csv")
CON_CSV = os.path.join(DATA_DIR, "connections.csv")

@st.cache_data
def load_df(path):
    return pd.read_csv(path)

st.title("🏢 派遣会社ポータル")
st.caption("自社の接続申請履歴を確認できます。")

agy_df = load_df(AGY_CSV)
con_df = pd.read_csv(CON_CSV) if os.path.exists(CON_CSV) else pd.DataFrame()

agency = st.selectbox("派遣会社を選択", agy_df["agency_name"].tolist())
aid = agy_df.loc[agy_df["agency_name"]==agency, "agency_id"].iloc[0]

st.subheader("接続申請履歴")
st.dataframe(con_df[con_df["agency_id"]==aid].sort_values("timestamp", ascending=False), use_container_width=True)
