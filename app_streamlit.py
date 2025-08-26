import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import io
from PIL import Image

# 데이터 로드 및 전처리


# 파일 업로드 위젯 (메인 화면 상단)
st.info('영수증 엑셀 파일을 업로드하면 해당 파일로 분석됩니다.')
uploaded_file = st.file_uploader('영수증 엑셀 파일 업로드', type=['xlsx'])
category_file = '롯데멤버스_상품분류표.csv'

def load_data(receipts_file):
    df_receipts = pd.read_excel(receipts_file)
    if '상태' in df_receipts.columns:
        df_receipts = df_receipts[df_receipts['상태'] != '등록중']
    df_category = pd.read_csv(category_file, encoding='cp949')
    df_merged = pd.merge(
        df_receipts,
        df_category,
        left_on='카테고리',
        right_on='소분류명(S_CLASS_NM)',
        how='left'
    )
    return df_merged

if uploaded_file is not None:
    df_merged = load_data(uploaded_file)
    users = sorted(df_merged['이름'].dropna().unique())
else:
    st.warning('분석할 영수증 엑셀 파일을 업로드해 주세요.')
    st.stop()

st.set_page_config(page_title='영수증 데이터 대시보드', layout='wide')
st.title('영수증 데이터 대시보드 (Streamlit)')

menu = st.sidebar.radio('메뉴', ['사용자별 분석', '전체 카테고리별 집계'])

if menu == '사용자별 분석':
    # 파일 업로드 시 사용자 선택 초기화 및 업로드 성공 알림
    if uploaded_file is not None:
        st.success('파일이 성공적으로 업로드되었습니다! 사용자 선택을 다시 해주세요.')
        user = st.selectbox('사용자 선택', [''] + users, index=0, format_func=lambda x: x if x else '--- 사용자 선택 ---')
    else:
        user = st.selectbox('사용자 선택', users)
    if not user:
        st.info('사용자를 선택해 주세요.')
        st.stop()
    user_df = df_merged[df_merged['이름'] == user]
    # 카테고리별 파이차트
    cat_counts = user_df['카테고리'].value_counts()
    fig_cat = px.pie(cat_counts, names=cat_counts.index, values=cat_counts.values, title='카테고리별 구매 비율', width=320, height=320, hole=0.5)
    fig_cat.update_traces(textinfo='percent', textposition='inside')
    fig_cat.update_layout(showlegend=True, title_x=0.5)
    # 결제채널별 파이차트
    channel_counts = user_df['결제채널'].value_counts()
    fig_channel = px.pie(channel_counts, names=channel_counts.index, values=channel_counts.values, title='결제채널별 구매 비율', width=320, height=320, hole=0.5)
    fig_channel.update_traces(textinfo='percent', textposition='inside')
    fig_channel.update_layout(showlegend=True, title_x=0.5)
    # 매장명별 파이차트
    store_counts = user_df['매장명'].value_counts()
    fig_store = px.pie(store_counts, names=store_counts.index, values=store_counts.values, title='매장명별 구매 비율', width=320, height=320, hole=0.5)
    fig_store.update_traces(textinfo='percent', textposition='inside')
    fig_store.update_layout(showlegend=True, title_x=0.5)
    # Top5 테이블
    top5_cat = cat_counts.head(5).reset_index()
    if top5_cat.shape[1] == 2:
        top5_cat.columns = ['카테고리', '건수']
    if 'No' in top5_cat.columns:
        top5_cat = top5_cat.drop('No', axis=1)
    top5_channel = channel_counts.head(5).reset_index()
    if top5_channel.shape[1] == 2:
        top5_channel.columns = ['결제채널', '건수']
    if 'No' in top5_channel.columns:
        top5_channel = top5_channel.drop('No', axis=1)
    top5_store = store_counts.head(5).reset_index()
    if top5_store.shape[1] == 2:
        top5_store.columns = ['매장명', '건수']
    if 'No' in top5_store.columns:
        top5_store = top5_store.drop('No', axis=1)

    fig_cat.update_layout(title_x=0)
    fig_channel.update_layout(title_x=0)
    fig_store.update_layout(title_x=0)
    config = {"displayModeBar": False}
    st.plotly_chart(fig_cat, use_container_width=True, config=config)
    st.dataframe(top5_cat.set_index(pd.Index(range(1, len(top5_cat)+1))), use_container_width=True, column_config={col: {"align": "center"} for col in top5_cat.columns})

    st.plotly_chart(fig_channel, use_container_width=True, config=config)
    st.dataframe(top5_channel.set_index(pd.Index(range(1, len(top5_channel)+1))), use_container_width=True, column_config={col: {"align": "center"} for col in top5_channel.columns})

    st.plotly_chart(fig_store, use_container_width=True, config=config)
    st.dataframe(top5_store.set_index(pd.Index(range(1, len(top5_store)+1))), use_container_width=True, column_config={col: {"align": "center"} for col in top5_store.columns})


elif menu == '전체 카테고리별 집계':
    st.subheader('전체 카테고리별 구매 건수 집계')
    cat_counts = df_merged['카테고리'].value_counts().reset_index().rename(columns={'index':'카테고리','카테고리':'건수'})
    st.dataframe(cat_counts, use_container_width=True)
