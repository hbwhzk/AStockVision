import streamlit as st
import pandas as pd
import numpy as np
from plotly import graph_objects as go
from Ashare import get_price
import datetime
from datetime import datetime

def calculate_bollinger_bands(df, window=20):
    """计算布林带"""
    df['SMA'] = df['close'].rolling(window=window).mean()
    df['STD'] = df['close'].rolling(window=window).std()
    df['Upper'] = df['SMA'] + (2 * df['STD'])
    df['Lower'] = df['SMA'] - (2 * df['STD'])
    return df

def identify_bollinger_signals(df):
    """识别买卖信号"""
    buy_signals = (df['close'] < df['Lower'])
    sell_signals = (df['close'] > df['Upper'])
    df['Buy'] = np.where(buy_signals, df['close'], np.nan)
    df['Sell'] = np.where(sell_signals, df['close'], np.nan)
    return df

def app():
    st.title('A股个股数据研究')

    # 用户输入部分
    code = st.text_input('输入股票代码', value='000001.XSHG')
    frequency_options = {'日': '1d', '周': '1w', '月': '1M', '1分钟（仅支持最近320条数据）': '1m', '5分钟': '5m', '15分钟': '15m', '30分钟': '30m', '60分钟': '60m'}
    frequency = st.selectbox('选择数据频率', options=list(frequency_options.keys()), index=0)
    count = st.number_input('数据点数量', min_value=20, value=100)
    end_date = st.date_input('选择结束日期', datetime.now())

    if st.button('获取数据'):
        end_date_str = end_date.strftime('%Y-%m-%d')
        actual_frequency = frequency_options[frequency]
        df = get_price(code, end_date=end_date_str, count=count, frequency=actual_frequency)

        if not df.empty:
            st.write(f'显示 {code} 的股票数据, 数据量: {len(df)} 条')
            st.dataframe(df)

            # 计算布林带
            df = calculate_bollinger_bands(df)
            df = identify_bollinger_signals(df)

            # 确定刻度位置
            num_labels = 5
            tick_vals = np.linspace(0, len(df) - 1, num_labels, dtype=int)
            tick_text = [df.index[i].strftime('%Y-%m-%d') for i in tick_vals]


            # 绘制K线图
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['open'], 
                high=df['high'],
                low=df['low'], 
                close=df['close']
            )])
            fig.update_layout(
                title='K线图',
                # xaxis_title='日期',
                # yaxis_title='价格',
                xaxis=dict(
                    type='category',
                    tickvals=[df.index[i] for i in tick_vals],
                    ticktext=tick_text,
                    rangeslider=dict(visible=False),
                    showspikes=True,
                ),
                yaxis=dict(showspikes=True),
                height=600,
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

            # 绘制量图
            fig2 = go.Figure(data=[go.Bar(
                x=df.index, 
                y=df['volume']
            )])
            fig2.update_layout(
                title='交易量图', 
                # xaxis_title='日期', 
                # yaxis_title='交易量',
                xaxis=dict(
                    type='category',
                    tickvals=[df.index[i] for i in tick_vals],
                    ticktext=tick_text,
                    showspikes=True,
                ),
                yaxis=dict(showspikes=True),
                height=600,
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig2, use_container_width=True)

            # 绘制布林带图
            fig3 = go.Figure(data=[
                go.Scatter(x=df.index, y=df['Upper'], line=dict(color='red'), name='Upper Band'),
                go.Scatter(x=df.index, y=df['SMA'], line=dict(color='blue'), name='Middle Band'),
                go.Scatter(x=df.index, y=df['Lower'], line=dict(color='red'), name='Lower Band'),
                go.Scatter(x=df.index, y=df['Buy'], mode='markers', marker=dict(color='green', size=10), name='Buy Signal'),
                go.Scatter(x=df.index, y=df['Sell'], mode='markers', marker=dict(color='orange', size=10), name='Sell Signal')
            ])
            fig3.update_layout(
                title='布林带图',
                # xaxis_title='日期',
                # yaxis_title='价格',
                xaxis=dict(
                    type='category',
                    tickvals=[df.index[i] for i in tick_vals],
                    ticktext=tick_text,
                    showspikes=True,
                ),
                yaxis=dict(showspikes=True),
                height=600,
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.error('未能获取数据，请检查股票代码和网络连接')

if __name__ == '__main__':
    app()





