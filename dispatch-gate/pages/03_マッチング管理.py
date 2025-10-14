
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="マッチング管理", page_icon="🤝", layout="wide")

DATA_DIR = "data"
CON_CSV = os.path.join(DATA_DIR, "connections.csv")

st.title("🤝 マッチング管理（社内用）")
st.caption("接続申請の承認・却下・メモを管理（簡易版）。")

if not os.path.exists(CON_CSV):
    st.info("接続履歴がありません。トップページから申請を作成してください。")
else:
    con_df = pd.read_csv(CON_CSV)
    st.dataframe(con_df, use_container_width=True)
    st.write("※ 本ページはPoCのため閲覧のみ。今後、承認/請求/奨励金支払の状態管理を追加予定。")
