#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Description：本地代理池实现
@Author: Dragon
@Date: 2024-05-04
"""

import json
import random
import time
import requests
import logging
import asyncio
from urllib.parse import urlparse
from typing import List
from proxy import ProxyProvider, IpInfoModel

logger = logging.getLogger('MediaCrawler')


class PPoolProxy(ProxyProvider):

    def __init__(self, **kwargs):
        super().__init__()
        self.proxy_pool_url = 'http://localhost:5010/get'
        self.proxy_count_url = 'http://localhost:5010/count'
        self.proxy_all_url = 'http://localhost:5010/all'

    async def get_proxies(self, num: int) -> List[IpInfoModel]:
        """
        获取IP的方法，实现抽象方法
        """
        try:
            logger.info(f"[PPoolProxy.get_proxies] 尝试获取{num}个代理IP")
            ip_list = []
            for _ in range(num):
                try:
                    response = requests.get(self.proxy_pool_url, timeout=10)
                    if response.status_code != 200:
                        logger.error(f"[PPoolProxy.get_proxies] 状态码不是200，响应内容: {response.text}")
                        continue
                    
                    data = response.json()
                    if 'code' in data and data['code'] == 1 and 'proxy' in data:
                        proxy_str = data['proxy']
                        
                        # 解析代理地址，可能是"http://ip:port"或者"ip:port"格式
                        if proxy_str.startswith('http'):
                            parsed = urlparse(proxy_str)
                            host_port = parsed.netloc
                            protocol = parsed.scheme
                        else:
                            host_port = proxy_str
                            protocol = 'http'
                        
                        if ':' in host_port:
                            host, port = host_port.split(':')
                            ip_info = IpInfoModel(
                                ip=host,
                                port=int(port),
                                user="",  # 免费代理无用户名
                                password="",  # 免费代理无密码
                                protocol=protocol,
                                expired_time_ts=int(time.time()) + 60*10  # 10分钟过期
                            )
                            ip_list.append(ip_info)
                    
                    # 加入延迟，避免请求过快
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"[PPoolProxy.get_proxies] 获取单个代理出错: {e}")
                    continue
            
            logger.info(f"[PPoolProxy.get_proxies] 成功获取到 {len(ip_list)} 个代理IP")
            return ip_list
        except Exception as e:
            logger.error(f"[PPoolProxy.get_proxies] 获取代理出错: {e}")
            return []

    def get_proxies_count(self):
        """
        获取代理IP数量
        """
        try:
            response = requests.get(self.proxy_count_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'count' in data:
                    return data['count']
            return 0
        except Exception as e:
            logger.error(f"[PPoolProxy.get_proxies_count] 获取代理数量出错: {e}")
            return 0 