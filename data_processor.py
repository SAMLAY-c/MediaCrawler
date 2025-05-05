#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import glob
from collections import Counter, defaultdict
import jieba
import re
from datetime import datetime

# 设置目录路径
data_dir = 'data/xhs/json/北京财务bp'
output_dir = 'data/xhs/processed'

# 创建输出目录
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def process_data():
    """处理北京财务bp的帖子和评论数据"""
    # 获取所有文件路径
    post_files = glob.glob(os.path.join(data_dir, 'search_contents_*.json'))
    comment_files = glob.glob(os.path.join(data_dir, 'search_comments_*.json'))
    
    # 读取所有帖子
    posts = []
    for post_file in post_files:
        with open(post_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                posts.extend(data)
            except json.JSONDecodeError:
                print(f"文件解析错误: {post_file}")
    
    # 读取所有评论
    comments = []
    for comment_file in comment_files:
        with open(comment_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                comments.extend(data)
            except json.JSONDecodeError:
                print(f"文件解析错误: {comment_file}")
    
    print(f"共处理了 {len(posts)} 个帖子和 {len(comments)} 个评论")
    
    # 提取关键字段
    processed_posts = []
    for post in posts:
        if 'note_id' not in post:
            continue
            
        processed_post = {
            'note_id': post.get('note_id', ''),
            'title': post.get('title', ''),
            'desc': post.get('desc', ''),
            'time': post.get('time', 0),
            'time_str': datetime.fromtimestamp(post.get('time', 0)/1000).strftime('%Y-%m-%d') if post.get('time', 0) else '',
            'user_id': post.get('user_id', ''),
            'nickname': post.get('nickname', ''),
            'liked_count': post.get('liked_count', '0'),
            'collected_count': post.get('collected_count', '0'),
            'comment_count': post.get('comment_count', '0'),
            'share_count': post.get('share_count', '0'),
            'ip_location': post.get('ip_location', ''),
            'tag_list': post.get('tag_list', ''),
            'note_url': post.get('note_url', '')
        }
        processed_posts.append(processed_post)
    
    # 提取评论关键字段
    processed_comments = []
    for comment in comments:
        if 'comment_id' not in comment:
            continue
            
        processed_comment = {
            'comment_id': comment.get('comment_id', ''),
            'note_id': comment.get('note_id', ''),
            'content': comment.get('content', ''),
            'create_time': comment.get('create_time', 0),
            'time_str': datetime.fromtimestamp(comment.get('create_time', 0)/1000).strftime('%Y-%m-%d') if comment.get('create_time', 0) else '',
            'user_id': comment.get('user_id', ''),
            'nickname': comment.get('nickname', ''),
            'like_count': comment.get('like_count', '0'),
            'sub_comment_count': comment.get('sub_comment_count', 0),
        }
        processed_comments.append(processed_comment)
    
    # 保存处理后的数据
    with open(os.path.join(output_dir, '北京财务bp_帖子.json'), 'w', encoding='utf-8') as f:
        json.dump(processed_posts, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(output_dir, '北京财务bp_评论.json'), 'w', encoding='utf-8') as f:
        json.dump(processed_comments, f, ensure_ascii=False, indent=2)
    
    # 生成统计数据
    generate_stats(processed_posts, processed_comments)
    
def generate_stats(posts, comments):
    """生成统计数据"""
    
    # 按时间统计帖子数量
    post_by_date = defaultdict(int)
    for post in posts:
        if post['time_str']:
            post_by_date[post['time_str']] += 1
    
    # 按时间统计评论数量  
    comment_by_date = defaultdict(int)
    for comment in comments:
        if comment['time_str']:
            comment_by_date[comment['time_str']] += 1
    
    # 提取所有帖子和评论文本
    all_post_text = ' '.join([post['title'] + ' ' + post['desc'] for post in posts])
    all_comment_text = ' '.join([comment['content'] for comment in comments])
    
    # 分词（去除停用词）
    jieba.setLogLevel(20)  # 设置jieba日志级别
    stopwords = ['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '过', '吧', '被', '比', '这个', '可以', '个', '能', '对', '而', '使', '但是', '但']
    
    def tokenize(text):
        return [word for word in jieba.cut(text) if word not in stopwords and len(word) > 1]
    
    post_words = tokenize(all_post_text)
    comment_words = tokenize(all_comment_text)
    
    # 词频统计
    post_word_freq = Counter(post_words).most_common(50)
    comment_word_freq = Counter(comment_words).most_common(50)
    
    # 统计平均点赞数、收藏数等
    def parse_count(count_str):
        if not isinstance(count_str, str):
            return 0
        count_str = count_str.replace('+', '')
        if '万' in count_str:
            return float(count_str.replace('万', '')) * 10000
        if '千' in count_str:
            return float(count_str.replace('千', '')) * 1000
        try:
            return float(count_str)
        except ValueError:
            return 0
    
    avg_likes = sum(parse_count(post['liked_count']) for post in posts) / len(posts) if posts else 0
    avg_collects = sum(parse_count(post['collected_count']) for post in posts) / len(posts) if posts else 0
    avg_comments = sum(parse_count(post['comment_count']) for post in posts) / len(posts) if posts else 0
    
    # 统计发文地点
    locations = Counter([post['ip_location'] for post in posts if post['ip_location']])
    
    # 合并统计数据
    stats = {
        "post_count": len(posts),
        "comment_count": len(comments),
        "post_by_date": dict(post_by_date),
        "comment_by_date": dict(comment_by_date),
        "post_word_freq": dict(post_word_freq),
        "comment_word_freq": dict(comment_word_freq),
        "avg_stats": {
            "likes": avg_likes,
            "collects": avg_collects,
            "comments": avg_comments
        },
        "locations": dict(locations)
    }
    
    with open(os.path.join(output_dir, '北京财务bp_统计.json'), 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print("数据处理完成!")

if __name__ == "__main__":
    process_data() 