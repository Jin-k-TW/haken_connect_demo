
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="案件カタログ", page_icon="📚", layout="wide")

DATA_DIR = "data"
OPP_CSV = os.path.join(DATA_DIR, "opportunities.csv")
COM_CSV = os.path.join(DATA_DIR, "companies.csv")

@st.cache_data
def load_df(path):
    return pd.read_csv(path)

st.title("📚 案件カタログ（詳細編集は今後実装）")
st.caption("フィルタ・並べ替えで案件を確認できます。")

opp_df = load_df(OPP_CSV)
com_df = load_df(COM_CSV)
view = opp_df.merge(com_df, on="company_id", how="left")
st.dataframe(view, use_container_width=True)
