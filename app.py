from flask import Flask, request, send_file
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import base64

matplotlib.use('Agg')
matplotlib.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

app = Flask(__name__)

def render_nav(active):
        return f'''
        <nav style="margin-bottom:20px;">
            <a href="/" style="margin-right:20px;{'font-weight:bold;text-decoration:underline;' if active=='user' else ''}">사용자별 분석</a>
            <a href="/category-summary" style="{'font-weight:bold;text-decoration:underline;' if active=='cat' else ''}">전체 카테고리별 집계</a>
        </nav>
        '''

@app.route('/')
def index():
    # 데이터 불러오기
    receipts_file = 'admin_embrain_receipts_selected_2025-08-25.xlsx'
    category_file = '롯데멤버스_상품분류표.csv'
    df_receipts = pd.read_excel(receipts_file)
    # '상태' 컬럼이 있으면 '등록중' 제외
    if '상태' in df_receipts.columns:
        df_receipts = df_receipts[df_receipts['상태'] != '등록중']
    df_category = pd.read_csv(category_file, encoding='cp949')

    # 상품명+카테고리 기준으로 소분류명 매핑(간단 예시: 카테고리명 기준)
    df_merged = pd.merge(
        df_receipts,
        df_category,
        left_on='카테고리',
        right_on='소분류명(S_CLASS_NM)',
        how='left'
    )

    # 사용자별 카테고리별 구매수량 집계
    user_category = df_merged.groupby(['이름', '카테고리'])['수량'].sum().unstack(fill_value=0)

    # 사용자별 카테고리별/채널별 파이차트 이미지 생성 (모든 사용자)
    user_imgs = {}
    user_channel_imgs = {}
    user_store_imgs = {}
    user_top5 = {}
    # 각 사용자별 3개 파이차트 PNG를 하나로 합쳐 저장하는 함수
    def save_user_charts(user):
        import numpy as np
        fig, axs = plt.subplots(1, 3, figsize=(12, 4))
        # 카테고리별
        row = user_category.loc[user]
        row[row>0].plot.pie(ax=axs[0], autopct='%1.1f%%', startangle=90, counterclock=False)
        axs[0].set_title('카테고리별')
        axs[0].set_ylabel('')
        # 결제채널별
        user_df = df_merged[df_merged['이름'] == user]
        channel_counts = user_df['결제채널'].value_counts()
        if not channel_counts.empty:
            channel_counts.plot.pie(ax=axs[1], autopct='%1.1f%%', startangle=90, counterclock=False)
            axs[1].set_title('결제채널별')
        else:
            axs[1].axis('off')
        axs[1].set_ylabel('')
        # 매장명별
        store_counts = user_df['매장명'].value_counts()
        if not store_counts.empty:
            store_counts.plot.pie(ax=axs[2], autopct='%1.1f%%', startangle=90, counterclock=False)
            axs[2].set_title('매장명별')
        else:
            axs[2].axis('off')
        axs[2].set_ylabel('')
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf

    for user, row in user_category.iterrows():
        # 카테고리별
        plt.figure(figsize=(4,4))
        row[row>0].plot.pie(autopct='%1.1f%%', startangle=90, counterclock=False)
        plt.title(f'{user} - 카테고리별 구매 비율')
        plt.ylabel('')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        user_imgs[user] = img_b64
        plt.close()
        # 카테고리 Top5
        top5_category = row[row>0].sort_values(ascending=False).head(5)
        top5_category_html = '<table border="1" style="margin-top:8px;font-size:13px;"><tr><th>카테고리</th><th>건수</th></tr>' + ''.join([f'<tr><td>{cat}</td><td>{int(cnt)}</td></tr>' for cat, cnt in top5_category.items()]) + '</table>'

        # 결제채널별
        user_df = df_merged[df_merged['이름'] == user]
        channel_counts = user_df['결제채널'].value_counts()
        plt.figure(figsize=(4,4))
        if not channel_counts.empty:
            channel_counts.plot.pie(autopct='%1.1f%%', startangle=90, counterclock=False)
            plt.title(f'{user} - 결제채널별 구매 비율')
            plt.ylabel('')
            buf2 = io.BytesIO()
            plt.savefig(buf2, format='png', bbox_inches='tight')
            buf2.seek(0)
            img_b64_2 = base64.b64encode(buf2.getvalue()).decode()
            user_channel_imgs[user] = img_b64_2
            plt.close()
            top5_channel = channel_counts.head(5)
            top5_channel_html = '<table border="1" style="margin-top:8px;font-size:13px;"><tr><th>결제채널</th><th>건수</th></tr>' + ''.join([f'<tr><td>{ch}</td><td>{int(cnt)}</td></tr>' for ch, cnt in top5_channel.items()]) + '</table>'
        else:
            user_channel_imgs[user] = ''
            top5_channel_html = '<div>데이터 없음</div>'

        # 매장명별
        store_counts = user_df['매장명'].value_counts()
        plt.figure(figsize=(4,4))
        if not store_counts.empty:
            store_counts.plot.pie(autopct='%1.1f%%', startangle=90, counterclock=False)
            plt.title(f'{user} - 매장명별 구매 비율')
            plt.ylabel('')
            buf3 = io.BytesIO()
            plt.savefig(buf3, format='png', bbox_inches='tight')
            buf3.seek(0)
            img_b64_3 = base64.b64encode(buf3.getvalue()).decode()
            user_store_imgs[user] = img_b64_3
            plt.close()
            top5_store = store_counts.head(5)
            top5_store_html = '<table border="1" style="margin-top:8px;font-size:13px;"><tr><th>매장명</th><th>건수</th></tr>' + ''.join([f'<tr><td>{store}</td><td>{int(cnt)}</td></tr>' for store, cnt in top5_store.items()]) + '</table>'
        else:
            user_store_imgs[user] = ''
            top5_store_html = '<div>데이터 없음</div>'

        user_top5[user] = {
            'category': top5_category_html,
            'channel': top5_channel_html,
            'store': top5_store_html
        }

    # 사용자 선택 드롭다운 및 JS 동적 렌더링
    user_options = ''.join([
        f"<option value='{user}'>{user}</option>"
        for user in user_imgs.keys()
    ])
    user_divs = ''.join([
        f"<div id='user_{user}' style='display:none; display:flex; gap:40px; align-items:flex-start;'>"
        f"<div><h3>{user} - 카테고리별</h3><img src='data:image/png;base64,{user_imgs[user]}'/>{user_top5[user]['category']}</div>"
        f"<div><h3>{user} - 결제채널별</h3>" + (f"<img src='data:image/png;base64,{user_channel_imgs[user]}'/>" if user_channel_imgs[user] else '<div>데이터 없음</div>') + f"{user_top5[user]['channel']}" + "</div>"
        f"<div><h3>{user} - 매장명별</h3>" + (f"<img src='data:image/png;base64,{user_store_imgs[user]}'/>" if user_store_imgs[user] else '<div>데이터 없음</div>') + f"{user_top5[user]['store']}" + "</div>"
        f"<div style='position:absolute;right:30px;top:30px;'><button onclick=\"downloadCharts('{user}')\">파이차트 PNG 저장</button></div>"
        "</div>"
        for user in user_imgs.keys()
    ])
    first_user = next(iter(user_imgs.keys())) if user_imgs else ''
    html = f"""
    {render_nav('user')}
    <h1>사용자별 구매 비율(카테고리/결제채널/매장명 파이차트)</h1>
    <div>
      <label for='user_select'>사용자 선택: </label>
      <select id='user_select' onchange="showUser(this.value)">{user_options}</select>
    </div>
    {user_divs}
    <script>
    function showUser(user) {{
        {';'.join([f"document.getElementById('user_{u}').style.display='none'" for u in user_imgs.keys()])};
        document.getElementById('user_' + user).style.display = 'flex';
    }}
    // 최초 진입시 첫 사용자 표시
    window.onload = function() {{
        if('{first_user}') showUser('{first_user}');
    }}
    function downloadCharts(user) {{
        window.open('/download-charts?user=' + encodeURIComponent(user), '_blank');
    }}
    </script>
    """
    return html
# 파이차트 3개를 하나의 PNG로 저장해서 다운로드하는 엔드포인트
@app.route('/download-charts')
def download_charts():
    user = request.args.get('user')
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
    user_category = df_merged.groupby(['이름', '카테고리'])['수량'].sum().unstack(fill_value=0)
    def save_user_charts_and_tables(user):
        import matplotlib.pyplot as plt
        import io
        from matplotlib.gridspec import GridSpec
        fig = plt.figure(figsize=(14, 8))
        gs = GridSpec(2, 3, height_ratios=[2, 1])
        # --- 파이차트 3개 ---
        row = user_category.loc[user]
        ax1 = fig.add_subplot(gs[0, 0])
        row[row>0].plot.pie(ax=ax1, autopct='%1.1f%%', startangle=90, counterclock=False)
        ax1.set_title('카테고리별')
        ax1.set_ylabel('')
        user_df = df_merged[df_merged['이름'] == user]
        channel_counts = user_df['결제채널'].value_counts()
        ax2 = fig.add_subplot(gs[0, 1])
        if not channel_counts.empty:
            channel_counts.plot.pie(ax=ax2, autopct='%1.1f%%', startangle=90, counterclock=False)
            ax2.set_title('결제채널별')
        else:
            ax2.axis('off')
        ax2.set_ylabel('')
        store_counts = user_df['매장명'].value_counts()
        ax3 = fig.add_subplot(gs[0, 2])
        if not store_counts.empty:
            store_counts.plot.pie(ax=ax3, autopct='%1.1f%%', startangle=90, counterclock=False)
            ax3.set_title('매장명별')
        else:
            ax3.axis('off')
        ax3.set_ylabel('')
        # --- Top5 테이블 3개 ---
        # 카테고리 Top5
        top5_category = row[row>0].sort_values(ascending=False).head(5)
        cat_table = [[cat, int(cnt)] for cat, cnt in top5_category.items()]
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.axis('off')
        ax4.table(cellText=cat_table, colLabels=['카테고리', '건수'], loc='center', cellLoc='center')
        ax4.set_title('카테고리 Top5')
        # 결제채널 Top5
        top5_channel = channel_counts.head(5)
        ch_table = [[ch, int(cnt)] for ch, cnt in top5_channel.items()]
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.axis('off')
        if ch_table:
            ax5.table(cellText=ch_table, colLabels=['결제채널', '건수'], loc='center', cellLoc='center')
        ax5.set_title('결제채널 Top5')
        # 매장명 Top5
        top5_store = store_counts.head(5)
        st_table = [[store, int(cnt)] for store, cnt in top5_store.items()]
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.axis('off')
        if st_table:
            ax6.table(cellText=st_table, colLabels=['매장명', '건수'], loc='center', cellLoc='center')
        ax6.set_title('매장명 Top5')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf
    buf = save_user_charts_and_tables(user)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name=f'{user}_piecharts.png')


# 전체 카테고리별 집계 테이블 페이지
@app.route('/category-summary')
def category_summary():
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
    cat_counts = df_merged['카테고리'].value_counts().reset_index()
    cat_counts.columns = ['카테고리', '건수']
    table_html = '<table border="1" style="margin-top:16px;font-size:15px;"><tr><th>카테고리</th><th>건수</th></tr>'
    for _, row in cat_counts.iterrows():
        table_html += f'<tr><td>{row["카테고리"]}</td><td>{row["건수"]}</td></tr>'
    table_html += '</table>'
    html = f"""
    {render_nav('cat')}
    <h1>전체 카테고리별 구매 건수 집계</h1>
    {table_html}
    """
    return html

if __name__ == '__main__':
    app.run(debug=True)


