#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/5
# @Author  : MediaCrawler Project
# @Description : 柱状图生成器

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def generate_bar_chart(data, x_col=None, y_col=None, title=None, xlabel=None, ylabel=None, 
                      figsize=(10, 6), color=None, output_path=None, sort_by=None, 
                      ascending=False, limit=None, horizontal=False, rotation=0):
    """
    生成柱状图
    
    参数:
        data: DataFrame或字典数据
        x_col: x轴列名(如果data是DataFrame)
        y_col: y轴列名(如果data是DataFrame)
        title: 图表标题
        xlabel: x轴标签
        ylabel: y轴标签
        figsize: 图表大小元组(宽,高)
        color: 柱状图颜色
        output_path: 输出文件路径
        sort_by: 排序依据
        ascending: 是否升序排序
        limit: 显示的最大数据点数量
        horizontal: 是否为水平柱状图
        rotation: x轴标签旋转角度
    """
    # 处理输入数据格式
    if isinstance(data, dict):
        df = pd.DataFrame({
            'key': list(data.keys()),
            'value': list(data.values())
        })
        x_col = 'key'
        y_col = 'value'
    elif isinstance(data, pd.DataFrame):
        if x_col is None or y_col is None:
            raise ValueError("当输入为DataFrame时，必须指定x_col和y_col")
        df = data.copy()
    else:
        raise TypeError("数据类型必须是字典或DataFrame")
    
    # 排序
    if sort_by:
        df = df.sort_values(by=sort_by, ascending=ascending)
    elif sort_by is None and isinstance(data, dict):
        # 默认对字典值排序
        df = df.sort_values(by='value', ascending=ascending)
    
    # 限制数据点数量
    if limit and len(df) > limit:
        if sort_by or (sort_by is None and isinstance(data, dict)):
            # 如果已排序，则保留排序后的前limit个
            df = df.iloc[:limit]
        else:
            # 否则保留前limit个
            df = df.head(limit)
    
    # 创建图形
    plt.figure(figsize=figsize)
    
    # 生成柱状图
    if horizontal:
        bars = plt.barh(df[x_col], df[y_col], color=color)
    else:
        bars = plt.bar(df[x_col], df[y_col], color=color)
    
    # 设置标题和标签
    if title:
        plt.title(title, fontsize=16)
    if xlabel:
        plt.xlabel(xlabel, fontsize=12)
    if ylabel:
        plt.ylabel(ylabel, fontsize=12)
    
    # 设置x轴标签旋转
    plt.xticks(rotation=rotation)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    if output_path:
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(output_path, bbox_inches='tight')
        print(f"柱状图已保存至: {output_path}")
    
    plt.close()
    
    return df


def generate_grouped_bar_chart(data, x_col, y_col, group_col, title=None, xlabel=None, ylabel=None,
                              figsize=(12, 7), output_path=None, sort_by=None, 
                              ascending=False, limit=None, rotation=0):
    """
    生成分组柱状图
    
    参数:
        data: DataFrame
        x_col: x轴列名
        y_col: y轴列名(数值)
        group_col: 分组列名
        title: 图表标题
        xlabel: x轴标签
        ylabel: y轴标签
        figsize: 图表大小元组(宽,高)
        output_path: 输出文件路径
        sort_by: 排序依据
        ascending: 是否升序排序
        limit: 显示的最大x类别数量
        rotation: x轴标签旋转角度
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("数据类型必须是DataFrame")
    
    df = data.copy()
    
    # 排序
    if sort_by:
        df = df.sort_values(by=sort_by, ascending=ascending)
    
    # 获取唯一的x值和group值
    x_values = df[x_col].unique()
    group_values = df[group_col].unique()
    
    # 限制x类别数量
    if limit and len(x_values) > limit:
        # 如果已经排序，取前limit个，否则随机取limit个
        if sort_by:
            keep_x = x_values[:limit]
        else:
            keep_x = x_values[:limit]
        df = df[df[x_col].isin(keep_x)]
        x_values = keep_x
    
    # 创建图形
    plt.figure(figsize=figsize)
    
    # 设置组间距
    bar_width = 0.8 / len(group_values)
    
    # 生成分组柱状图
    for i, group in enumerate(group_values):
        group_data = df[df[group_col] == group]
        x_positions = np.arange(len(x_values)) + i * bar_width - (len(group_values) - 1) * bar_width / 2
        
        # 对于每个x值，找到相应的y值
        y_values = []
        for x in x_values:
            val = group_data[group_data[x_col] == x][y_col].values
            y_values.append(val[0] if len(val) > 0 else 0)
        
        plt.bar(x_positions, y_values, width=bar_width, label=group)
    
    # 设置x轴刻度
    plt.xticks(np.arange(len(x_values)), x_values, rotation=rotation)
    
    # 设置标题和标签
    if title:
        plt.title(title, fontsize=16)
    if xlabel:
        plt.xlabel(xlabel, fontsize=12)
    if ylabel:
        plt.ylabel(ylabel, fontsize=12)
    
    # 添加图例
    plt.legend()
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    if output_path:
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(output_path, bbox_inches='tight')
        print(f"分组柱状图已保存至: {output_path}")
    
    plt.close()
    
    return df


def generate_stacked_bar_chart(data, x_col, y_cols, title=None, xlabel=None, ylabel=None,
                              figsize=(12, 7), output_path=None, sort_by=None,
                              ascending=False, limit=None, rotation=0, colors=None):
    """
    生成堆叠柱状图
    
    参数:
        data: DataFrame
        x_col: x轴列名
        y_cols: 要堆叠的列名列表
        title: 图表标题
        xlabel: x轴标签
        ylabel: y轴标签
        figsize: 图表大小元组(宽,高)
        output_path: 输出文件路径
        sort_by: 排序依据
        ascending: 是否升序排序
        limit: 显示的最大x类别数量
        rotation: x轴标签旋转角度
        colors: 每个堆叠部分的颜色列表
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("数据类型必须是DataFrame")
    
    df = data.copy()
    
    # 排序
    if sort_by:
        df = df.sort_values(by=sort_by, ascending=ascending)
    
    # 限制数据点数量
    if limit and len(df) > limit:
        if sort_by:
            # 如果已排序，则保留排序后的前limit个
            df = df.iloc[:limit]
        else:
            # 否则保留前limit个
            df = df.head(limit)
    
    # 创建图形
    plt.figure(figsize=figsize)
    
    # 获取x值
    x_values = df[x_col].values
    
    # 先创建底部的柱子
    bottom = np.zeros(len(df))
    
    # 依次堆叠每一层
    for i, col in enumerate(y_cols):
        color = colors[i] if colors and i < len(colors) else None
        plt.bar(x_values, df[col], bottom=bottom, label=col, color=color)
        bottom += df[col].values
    
    # 设置标题和标签
    if title:
        plt.title(title, fontsize=16)
    if xlabel:
        plt.xlabel(xlabel, fontsize=12)
    if ylabel:
        plt.ylabel(ylabel, fontsize=12)
    
    # 设置x轴标签旋转
    plt.xticks(rotation=rotation)
    
    # 添加图例
    plt.legend()
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    if output_path:
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(output_path, bbox_inches='tight')
        print(f"堆叠柱状图已保存至: {output_path}")
    
    plt.close()
    
    return df


if __name__ == "__main__":
    # 示例数据
    sample_data = {
        "小红书": 356,
        "抖音": 420,
        "B站": 310,
        "微博": 380,
        "知乎": 240,
        "贴吧": 180,
        "快手": 290
    }
    
    # 测试基本柱状图
    generate_bar_chart(
        sample_data,
        title="各平台爬取数据量",
        xlabel="平台",
        ylabel="数据量",
        sort_by="value",
        ascending=False,
        output_path="data/visualization_test/bar_chart_example.png"
    )
    
    # 测试分组柱状图
    # 创建示例DataFrame
    platforms = ["小红书", "抖音", "B站", "微博", "知乎"]
    content_types = ["帖子", "评论", "用户"]
    
    data_list = []
    for platform in platforms:
        for content_type in content_types:
            # 生成随机数据
            count = np.random.randint(100, 500)
            data_list.append({"平台": platform, "内容类型": content_type, "数量": count})
    
    df = pd.DataFrame(data_list)
    
    # 生成分组柱状图
    generate_grouped_bar_chart(
        df,
        x_col="平台",
        y_col="数量",
        group_col="内容类型",
        title="各平台不同内容类型数据量",
        xlabel="平台",
        ylabel="数据量",
        output_path="data/visualization_test/grouped_bar_chart_example.png"
    ) 