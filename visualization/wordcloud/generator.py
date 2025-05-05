#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/5
# @Author  : MediaCrawler Project
# @Description : 词云生成器

import os
import jieba
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.colors as mcolors


def load_stopwords(stopwords_file):
    """
    加载停用词
    """
    if not os.path.exists(stopwords_file):
        print(f"警告: 停用词文件不存在 {stopwords_file}")
        return set()
    
    with open(stopwords_file, 'r', encoding='utf-8') as f:
        stopwords = {line.strip() for line in f.readlines() if line.strip()}
    return stopwords


def preprocess_text(text, stopwords=None):
    """
    文本预处理：分词并去除停用词
    """
    if stopwords is None:
        stopwords = set()
    
    # 分词
    words = jieba.cut(text)
    
    # 过滤停用词和空字符
    filtered_words = [word for word in words if word.strip() and word not in stopwords and len(word) > 1]
    
    return filtered_words


def generate_wordcloud(data, output_path=None, title=None, font_path=None, width=800, height=600, 
                      max_words=200, background_color="white", colormap="viridis", stopwords_file=None):
    """
    生成词云图
    
    参数:
        data: 字符串或字符串列表，需要生成词云的文本
        output_path: 输出文件路径，如果不指定则只显示不保存
        title: 词云图标题
        font_path: 字体文件路径，用于显示中文
        width: 词云图宽度
        height: 词云图高度
        max_words: 最大显示词数
        background_color: 背景颜色
        colormap: 颜色映射
        stopwords_file: 停用词文件路径
    
    返回:
        词频统计字典
    """
    # 加载停用词
    if stopwords_file:
        stopwords = load_stopwords(stopwords_file)
    else:
        stopwords = set()
    
    # 处理输入数据
    if isinstance(data, str):
        text = data
    elif isinstance(data, list):
        text = ' '.join(data)
    else:
        raise TypeError("数据类型必须是字符串或字符串列表")
    
    # 文本预处理
    words = preprocess_text(text, stopwords)
    
    # 词频统计
    word_counts = Counter(words)
    
    # 创建词云对象
    wc = WordCloud(
        font_path=font_path,
        width=width,
        height=height,
        max_words=max_words,
        background_color=background_color,
        colormap=colormap,
        collocations=False
    )
    
    # 生成词云
    wc.generate_from_frequencies(word_counts)
    
    # 创建图形并显示
    plt.figure(figsize=(width/100, height/100), dpi=100)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    
    if title:
        plt.title(title, fontsize=20)
    
    # 保存图片
    if output_path:
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(output_path, bbox_inches='tight')
        print(f"词云图已保存至: {output_path}")
    
    plt.close()
    
    return dict(word_counts)


def generate_group_wordcloud(data_groups, output_path=None, title=None, font_path=None, 
                           stopwords_file=None, width=1000, height=800):
    """
    为多个分组数据生成词云图
    
    参数:
        data_groups: 字典，格式为 {分组名: 文本数据}
        output_path: 输出文件路径
        title: 总标题
        font_path: 字体文件路径
        stopwords_file: 停用词文件路径
        width: 总宽度
        height: 总高度
    """
    # 计算子图行列数
    n_groups = len(data_groups)
    cols = min(3, n_groups)
    rows = (n_groups + cols - 1) // cols
    
    # 创建图形
    fig, axes = plt.subplots(rows, cols, figsize=(width/100, height/100), dpi=100)
    if rows == 1 and cols == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    # 设置标题
    if title:
        fig.suptitle(title, fontsize=20)
    
    # 使用不同的颜色映射
    colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 
                'Pastel1', 'Pastel2', 'Paired', 'Set1', 'Set2']
    
    # 为每个组生成词云
    for i, (group_name, text) in enumerate(data_groups.items()):
        if i < len(axes):
            # 加载停用词
            if stopwords_file:
                stopwords = load_stopwords(stopwords_file)
            else:
                stopwords = set()
            
            # 处理文本
            if isinstance(text, list):
                text = ' '.join(text)
            
            words = preprocess_text(text, stopwords)
            word_counts = Counter(words)
            
            # 创建词云
            wc = WordCloud(
                font_path=font_path,
                width=400,
                height=300,
                max_words=100,
                background_color="white",
                colormap=colormaps[i % len(colormaps)],
                collocations=False
            )
            wc.generate_from_frequencies(word_counts)
            
            # 显示词云
            axes[i].imshow(wc, interpolation='bilinear')
            axes[i].set_title(group_name)
            axes[i].axis('off')
    
    # 隐藏多余的子图
    for j in range(i+1, len(axes)):
        axes[j].axis('off')
    
    plt.tight_layout()
    if title:
        plt.subplots_adjust(top=0.9)
    
    # 保存图片
    if output_path:
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(output_path, bbox_inches='tight')
        print(f"分组词云图已保存至: {output_path}")
    
    plt.close()


if __name__ == "__main__":
    # 示例用法
    test_text = """
    MediaCrawler是一个用于爬取中国各大社交媒体平台的工具，包括小红书、抖音、快手、B站、微博、贴吧和知乎。
    它使用Playwright来维持浏览器上下文，这有助于避免复杂的JS逆向工程来处理加密参数。
    主要功能包括关键词搜索、特定帖子详情获取、评论提取（包括子评论）、创作者资料爬取等。
    它还支持登录状态缓存、IP代理池和评论词云生成功能。
    """
    
    # 测试单个词云生成
    generate_wordcloud(
        test_text, 
        output_path="data/visualization_test/wordcloud_example.png",
        title="MediaCrawler示例词云",
        stopwords_file="./docs/hit_stopwords.txt" if os.path.exists("./docs/hit_stopwords.txt") else None
    )
    
    # 测试分组词云生成
    test_groups = {
        "社交平台": "小红书 抖音 快手 B站 微博 贴吧 知乎 社交媒体 平台",
        "核心功能": "关键词搜索 帖子详情 评论提取 子评论 创作者资料 数据爬取",
        "技术特性": "Playwright 浏览器上下文 登录状态 缓存 IP代理池 词云生成"
    }
    
    generate_group_wordcloud(
        test_groups,
        output_path="data/visualization_test/group_wordcloud_example.png",
        title="MediaCrawler功能分组词云",
        stopwords_file="./docs/hit_stopwords.txt" if os.path.exists("./docs/hit_stopwords.txt") else None
    ) 