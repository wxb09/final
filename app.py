import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import jieba
from collections import Counter
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Line, Scatter, Radar, Kline, WordCloud
from pyecharts.commons.utils import JsCode
import matplotlib.pyplot as plt
import chardet  # 导入chardet库用于自动检测编码

# 创建一个文本输入框
url = st.sidebar.text_input("请输入文章URL", "")

# 获取文本内容
def fetch_text_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        # 使用chardet检测编码
        encoding = chardet.detect(response.content)['encoding']
        # 根据检测到的编码解码内容
        return response.content.decode(encoding)
    else:
        return "无法获取内容，URL可能不正确或服务器返回了错误状态码。"

# 使用正则表达式去除HTML标签
def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# 去除文本中的标点符号
def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)

# 对文本进行分词
def segment_text(text):
    words = jieba.cut(text)
    return ' '.join(words)

# 统计词频
def count_word_frequency(words):
    return Counter(words.split())

# 处理文本，包括去除HTML标签和标点符号
def process_text(text):
    text = remove_html_tags(text)
    text = remove_punctuation(text)
    return text

# 分词并统计词频
def tokenize_and_count(text):
    processed_text = process_text(text)
    segmented_text = segment_text(processed_text)
    return count_word_frequency(segmented_text)

# 使用pyecharts绘制词云
def create_wordcloud(word_counts):
    wordcloud = WordCloud()
    wordcloud.add("", list(word_counts.items()), word_size_range=[20, 100])
    wordcloud.set_global_opts(title_opts=opts.TitleOpts(title="词云"))
    return wordcloud

# 使用Matplotlib绘制柱状图
def create_matplotlib_bar_chart(word_counts):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
    plt.figure(figsize=(10, 6))
    plt.bar(word_counts.keys(), word_counts.values())
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Word Frequency - Matplotlib')
    return plt

import seaborn as sns
# 使用Matplotlib绘制饼图
def create_matplotlib_sie_chart(word_counts):
    labels = list(word_counts.keys())
    sizes = list(word_counts.values())
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('词频分布 - Matplotlib')
    return plt


import pygal


import plotly.express as px
# 使用Plotly绘制交互式折线图
def create_plotly_line_chart(word_counts):
    df = pd.DataFrame(list(word_counts.items()), columns=['Word', 'Frequency'])
    # 确保 'Word' 列是字符串类型，'Frequency' 列是数值类型
    df['Word'] = df['Word'].astype(str)
    df['Frequency'] = df['Frequency'].astype(float)
    fig = px.line(df, x='Word', y='Frequency', title='Word Frequency - Plotly')
    fig.update_traces(mode='lines+markers')  # 添加数据点标记
    return fig

# 使用pyecharts绘制散点图
def create_scatter_chart(word_counts):
    scatter = Scatter()
    scatter.add_xaxis(list(word_counts.keys()))
    scatter.add_yaxis("词频", list(word_counts.values()))
    scatter.set_global_opts(title_opts=opts.TitleOpts(title="散点图"))
    return scatter

import pandas as pd
# 使用Plotly绘制雷达图
def create_plotly_radar_chart(word_counts):
    df = pd.DataFrame(list(word_counts.items()), columns=['Word', 'Frequency'])
    fig = px.line_polar(df, r='Frequency', theta='Word', line_close=True)
    fig.update_traces(fill='toself')  # 填充雷达图区域
    fig.update_layout(title='词频雷达图')
    return fig

# 使用pyecharts绘制K线图
def create_kline_chart(word_counts):
    kline = Kline()
    kline.add_xaxis(list(word_counts.keys()))
    kline.add_yaxis("词频", list(word_counts.values()))
    kline.set_global_opts(title_opts=opts.TitleOpts(title="K线图"))
    return kline

# 获取网页内容并在网页中显示
content = fetch_text_from_url(url) if url else ""
#st.write("获取的内容如下：")
#st.write(content)

# 处理文本并统计词频
word_counts = tokenize_and_count(content) if content else Counter()

# 选择图表类型
chart_type = st.sidebar.selectbox("选择图表类型", ["词云", "柱状图", "饼图", "折线图", "散点图", "雷达图", "K线图"])

# 过滤低频词
min_freq = st.sidebar.slider("设置最低词频阈值", 1, 100, 10)
filtered_word_counts = {word: count for word, count in word_counts.items() if count >= min_freq}
filtered_word_counts = Counter(filtered_word_counts)  # 转换为Counter对象

# 展示词频排名前20的词汇
top_words = filtered_word_counts.most_common(20)
st.write("词频排名前20的词汇：")
st.table(top_words)  # 使用Streamlit的table组件来显示排名列表

# 根据选择的图表类型展示不同的图表
if chart_type == "词云":
    # 将Pyecharts图表转换为HTML
    wordcloud = create_wordcloud(filtered_word_counts)
    html_content = wordcloud.render_embed()
    # 使用Streamlit的html组件来显示Pyecharts图表
    st.components.v1.html(html_content, height=600)  # 修改height参数为数值\
elif chart_type == "柱状图":
    # 绘制柱状图
    st.pyplot(create_matplotlib_bar_chart(filtered_word_counts))

elif chart_type == "饼图":
    # 绘制饼图
    st.pyplot(create_matplotlib_sie_chart(filtered_word_counts))
elif chart_type == "折线图":
    # 确保 filtered_word_counts 中的值是数值类型
    filtered_word_counts = {word: float(count) for word, count in filtered_word_counts.items()}

    # 绘制折线图
    fig = create_plotly_line_chart(filtered_word_counts)
    st.plotly_chart(fig, use_container_width=True)
elif chart_type == "散点图":
    scatter_chart = create_scatter_chart(filtered_word_counts)
    html_content = scatter_chart.render_embed()
    st.components.v1.html(html_content, height=600)
elif chart_type == "雷达图":
    # 绘制雷达图
    radar_chart = create_plotly_radar_chart(filtered_word_counts)
    st.plotly_chart(radar_chart, use_container_width=True)
elif chart_type == "K线图":
    kline_chart = create_kline_chart(filtered_word_counts)
    html_content = kline_chart.render_embed()
    st.components.v1.html(html_content, height=600)
