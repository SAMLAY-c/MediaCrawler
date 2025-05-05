# MediaCrawler 可视化组件

本目录包含MediaCrawler项目的可视化组件和工具，用于将爬取的数据转换为可视化结果。

## 目录结构

- `wordcloud/` - 词云生成组件和工具
- `charts/` - 图表生成组件（柱状图、饼图、折线图等）
- `graphs/` - 网络关系图和其他复杂图形组件

## 使用方法

可视化组件可以单独使用，也可以在爬虫执行完成后自动调用。在`config/base_config.py`中可以配置自动生成可视化结果的选项。

### 词云生成示例

```python
from visualization.wordcloud.generator import generate_wordcloud

# 从评论数据生成词云
generate_wordcloud(comments_data, output_path="data/xhs/visualization/wordcloud_result.png")
```

### 图表生成示例

```python
from visualization.charts.bar_chart import generate_bar_chart

# 生成互动数据柱状图
generate_bar_chart(interaction_data, title="互动数据分析", output_path="data/xhs/visualization/interaction.png")
```

## 自定义组件

您可以在各子目录中添加自定义的可视化组件，建议遵循以下命名规范：

- 文件名使用小写字母和下划线
- 类名使用驼峰命名法
- 函数名使用小写字母和下划线

## 依赖库

可视化组件依赖以下Python库：
- matplotlib
- wordcloud
- pandas
- seaborn
- networkx (用于关系图) 