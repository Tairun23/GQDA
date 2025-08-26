import dash
from dash import dcc, html, Input, Output
from dash import dash_table
import plotly.express as px
import pandas as pd

# 데이터 로드 및 전처리
def load_data():
    receipts_file = 'admin_embrain_receipts_selected_2025-08-25.xlsx'
    category_file = '롯데멤버스_상품분류표.csv'
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

df_merged = load_data()
users = sorted(df_merged['이름'].dropna().unique())

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('영수증 데이터 대시보드 (Dash)'),
    dcc.Tabs([
        dcc.Tab(label='사용자별 분석', children=[
            html.Label('사용자 선택:'),
            dcc.Dropdown(id='user-dropdown', options=[{'label': u, 'value': u} for u in users], value=users[0]),
            html.Div(id='user-charts'),
        ]),
        dcc.Tab(label='전체 카테고리별 집계', children=[
            html.H3('전체 카테고리별 구매 건수 집계'),
            dash_table.DataTable(
                id='cat-table',
                columns=[{'name': '카테고리', 'id': '카테고리'}, {'name': '건수', 'id': '건수'}],
                data=df_merged['카테고리'].value_counts().reset_index().rename(columns={'index':'카테고리','카테고리':'건수'}).to_dict('records'),
                style_table={'width':'400px'},
                style_cell={'textAlign': 'center'},
            )
        ]),
    ])
])

@app.callback(
    Output('user-charts', 'children'),
    Input('user-dropdown', 'value')
)
def update_user_charts(user):
    user_df = df_merged[df_merged['이름'] == user]
    # 카테고리별 파이차트
    cat_counts = user_df['카테고리'].value_counts()
    fig_cat = px.pie(cat_counts, names=cat_counts.index, values=cat_counts.values, title='카테고리별 구매 비율')
    # 결제채널별 파이차트
    channel_counts = user_df['결제채널'].value_counts()
    fig_channel = px.pie(channel_counts, names=channel_counts.index, values=channel_counts.values, title='결제채널별 구매 비율')
    # 매장명별 파이차트
    store_counts = user_df['매장명'].value_counts()
    fig_store = px.pie(store_counts, names=store_counts.index, values=store_counts.values, title='매장명별 구매 비율')
    # Top5 테이블
    top5_cat = cat_counts.head(5).reset_index().rename(columns={'index':'카테고리','카테고리':'건수'})
    top5_channel = channel_counts.head(5).reset_index().rename(columns={'index':'결제채널','결제채널':'건수'})
    top5_store = store_counts.head(5).reset_index().rename(columns={'index':'매장명','매장명':'건수'})
    # 각 파이차트+테이블을 세로로 묶고, 3개를 가로로 나란히 배치
    def chart_table_block(fig, table_data, col_labels):
        return html.Div([
            dcc.Graph(figure=fig, style={'height':'350px'}),
            dash_table.DataTable(
                columns=[{'name': n, 'id': n} for n in col_labels],
                data=table_data.to_dict('records'),
                style_table={'width':'90%', 'margin':'0 auto'},
                style_cell={'textAlign': 'center'},
                style_header={'fontWeight': 'bold'},
            )
        ], style={'width':'32%', 'minWidth':'320px', 'display':'flex', 'flexDirection':'column', 'alignItems':'center', 'marginRight':'1%'})

    return html.Div([
        chart_table_block(fig_cat, top5_cat, ['카테고리','건수']),
        chart_table_block(fig_channel, top5_channel, ['결제채널','건수']),
        chart_table_block(fig_store, top5_store, ['매장명','건수'])
    ], style={'display':'flex', 'flexDirection':'row', 'justifyContent':'space-between', 'width':'100%'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
