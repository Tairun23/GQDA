
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import io
from PIL import Image
st.set_page_config(page_title='영수증 데이터 대시보드', layout='wide')




# 사이드바 메뉴 구성
menu = st.sidebar.radio('메뉴', ['분석파일 업로드', '사용자별 분석', '전체 카테고리별 집계'])
uploaded_file = None
users = []
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




# 업로드 메뉴: 파일 업로드만 제공 (세션 상태에 저장)
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None

# 업로드 메뉴: 파일 업로드만 제공 (세션 상태에 저장)
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None

if menu == '분석파일 업로드':
    uploaded = st.file_uploader('영수증 엑셀 파일 업로드', type=['xlsx'])
    if uploaded is not None:
        st.session_state['uploaded_file'] = uploaded
        st.success('파일이 성공적으로 업로드되었습니다!')
    elif st.session_state['uploaded_file'] is None:
        st.info('영수증 엑셀 파일을 업로드하면 해당 파일로 분석됩니다.')
    uploaded_file = st.session_state['uploaded_file']

elif menu == '사용자별 분석':
    uploaded_file = st.session_state['uploaded_file']
    if uploaded_file is None:
        st.warning('분석할 영수증 엑셀 파일을 업로드해 주세요.')
        st.stop()
    df_merged = load_data(uploaded_file)
    users = sorted(df_merged['이름'].dropna().unique())
    st.title('영수증 데이터 대시보드 (Streamlit)')
    # 파일 업로드 시 사용자 선택 초기화 및 업로드 성공 알림
    user = st.selectbox('사용자 선택', [''] + users, index=0, format_func=lambda x: x if x else '--- 사용자 선택 ---')
    if uploaded_file is not None and not user:
        st.success('파일이 성공적으로 업로드되었습니다! 사용자 선택을 다시 해주세요.')
    if not user:
        st.info('사용자를 선택해 주세요.')
        st.stop()
    user_df = df_merged[df_merged['이름'] == user]

    # 카테고리별 파이차트 (범례에 퍼센트 표기)
    cat_counts = user_df['카테고리'].value_counts()
    cat_labels = cat_counts.index.tolist()
    cat_values = cat_counts.values.tolist()
    cat_percents = [value/sum(cat_values)*100 for value in cat_values]
    cat_names = [f"{label} ({percent:.1f}%)" for label, percent in zip(cat_labels, cat_percents)]
    fig_cat = px.pie(values=cat_values, names=cat_names, title='카테고리별 구매 비율', width=320, height=320, hole=0.5)
    fig_cat.update_traces(textinfo='percent', textposition='inside', showlegend=True, insidetextorientation='radial')
    fig_cat.update_layout(title_x=0.5, legend_title_text='카테고리')
    config = {"displayModeBar": False}
    st.plotly_chart(fig_cat, use_container_width=True, config=config)

    # 결제채널별 파이차트 (범례에 퍼센트 표기)
    channel_counts = user_df['결제채널'].value_counts()
    channel_labels = channel_counts.index.tolist()
    channel_values = channel_counts.values.tolist()
    channel_percents = [value/sum(channel_values)*100 for value in channel_values]
    channel_names = [f"{label} ({percent:.1f}%)" for label, percent in zip(channel_labels, channel_percents)]
    fig_channel = px.pie(values=channel_values, names=channel_names, title='결제채널별 구매 비율', width=320, height=320, hole=0.5)
    fig_channel.update_traces(textinfo='percent', textposition='inside', showlegend=True, insidetextorientation='radial')
    fig_channel.update_layout(title_x=0.5, legend_title_text='결제채널')
    st.plotly_chart(fig_channel, use_container_width=True, config=config)

    # 매장명별 파이차트 (범례에 퍼센트 표기)
    store_counts = user_df['매장명'].value_counts()
    store_labels = store_counts.index.tolist()
    store_values = store_counts.values.tolist()
    store_percents = [value/sum(store_values)*100 for value in store_values]
    store_names = [f"{label} ({percent:.1f}%)" for label, percent in zip(store_labels, store_percents)]
    fig_store = px.pie(values=store_values, names=store_names, title='매장명별 구매 비율', width=320, height=320, hole=0.5)
    fig_store.update_traces(textinfo='percent', textposition='inside', showlegend=True, insidetextorientation='radial')
    fig_store.update_layout(title_x=0.5, legend_title_text='매장명')
    st.plotly_chart(fig_store, use_container_width=True, config=config)

elif menu == '전체 카테고리별 집계':
    uploaded_file = st.session_state['uploaded_file']
    if uploaded_file is None:
        st.warning('분석할 영수증 엑셀 파일을 업로드해 주세요.')
        st.stop()
    df_merged = load_data(uploaded_file)
    st.title('영수증 데이터 대시보드 (Streamlit)')
    st.subheader('전체 카테고리별 구매 건수 집계')
    cat_counts = df_merged['카테고리'].value_counts().reset_index().rename(columns={'index':'카테고리','카테고리':'건수'})
    st.dataframe(cat_counts, use_container_width=True)


