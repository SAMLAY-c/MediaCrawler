#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/5
# @Author  : MediaCrawler Project
# @Description : 数据整理工具

import os
import sys
import shutil
import json
import csv
import time
import argparse
from datetime import datetime


def create_platform_timestamp_folder(platform, keywords, base_dir="data"):
    """
    创建平台+时间戳+关键字的文件夹
    
    参数:
        platform: 平台名称（xhs, dy, ks, bili, wb, tieba, zhihu）
        keywords: 搜索关键词
        base_dir: 基础目录
    
    返回:
        创建的文件夹路径
    """
    # 获取当前时间戳（格式：YYYYMMDD）
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # 处理关键词（替换特殊字符，限制长度）
    if isinstance(keywords, list):
        keywords = "_".join(keywords)
    
    # 替换非法字符
    keywords = keywords.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
    
    # 限制关键词长度，避免文件名过长
    if len(keywords) > 50:
        keywords = keywords[:47] + "..."
    
    # 构建文件夹名
    folder_name = f"{platform}_{timestamp}_{keywords}"
    
    # 构建完整路径
    full_path = os.path.join(base_dir, platform, folder_name)
    
    # 创建文件夹
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    
    # 在文件夹下创建子目录
    os.makedirs(os.path.join(full_path, "json"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "processed"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "visualization"), exist_ok=True)
    
    print(f"创建目录: {full_path}")
    
    return full_path


def organize_existing_data(source_dir, platform, keywords=None, base_dir="data"):
    """
    整理现有数据到平台文件夹结构
    
    参数:
        source_dir: 源数据目录
        platform: 平台名称
        keywords: 搜索关键词（如果为None，则从文件名或内容推断）
        base_dir: 基础目录
    """
    if not os.path.exists(source_dir):
        print(f"源目录不存在: {source_dir}")
        return
    
    # 如果keywords为None，尝试从文件名或内容推断
    if keywords is None:
        keywords = "unknown"
        
        # 尝试从文件名推断
        for filename in os.listdir(source_dir):
            if filename.endswith(".json"):
                # 从文件名提取关键词
                name_parts = filename.split("_")
                if len(name_parts) > 1:
                    keywords = name_parts[0]
                    break
    
    # 创建目标文件夹
    target_dir = create_platform_timestamp_folder(platform, keywords, base_dir)
    
    # 移动文件
    for filename in os.listdir(source_dir):
        source_file = os.path.join(source_dir, filename)
        
        # 跳过目录
        if os.path.isdir(source_file):
            continue
        
        # 根据文件类型决定目标子目录
        if filename.endswith(".json"):
            target_subdir = "json"
        elif filename.endswith(".csv"):
            target_subdir = "processed"
        elif filename.endswith((".png", ".jpg", ".jpeg", ".svg")):
            target_subdir = "visualization"
        else:
            target_subdir = ""
        
        # 构建目标路径
        if target_subdir:
            target_file = os.path.join(target_dir, target_subdir, filename)
        else:
            target_file = os.path.join(target_dir, filename)
        
        # 复制文件
        shutil.copy2(source_file, target_file)
        print(f"复制: {source_file} -> {target_file}")
    
    print(f"数据已整理到: {target_dir}")


def main():
    parser = argparse.ArgumentParser(description="MediaCrawler数据整理工具")
    
    # 命令子解析器
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 创建新文件夹的子命令
    create_parser = subparsers.add_parser("create", help="创建平台+时间戳+关键字的文件夹")
    create_parser.add_argument("-p", "--platform", required=True, 
                             choices=["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"],
                             help="平台名称")
    create_parser.add_argument("-k", "--keywords", required=True, help="搜索关键词")
    create_parser.add_argument("-d", "--base-dir", default="data", help="基础目录(默认: data)")
    
    # 整理现有数据的子命令
    organize_parser = subparsers.add_parser("organize", help="整理现有数据到平台文件夹结构")
    organize_parser.add_argument("-s", "--source", required=True, help="源数据目录")
    organize_parser.add_argument("-p", "--platform", required=True,
                               choices=["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"],
                               help="平台名称")
    organize_parser.add_argument("-k", "--keywords", help="搜索关键词(如果不提供，将尝试从文件名推断)")
    organize_parser.add_argument("-d", "--base-dir", default="data", help="基础目录(默认: data)")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_platform_timestamp_folder(args.platform, args.keywords, args.base_dir)
    elif args.command == "organize":
        organize_existing_data(args.source, args.platform, args.keywords, args.base_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 