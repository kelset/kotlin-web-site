import re
from typing import List, Dict

from flask import request


class NavItem:
    def __init__(self, config):
        if 'url' in config:
            url = config['url']
            if not url.startswith("http") and not url.startswith('/'):
                url = '/' + url
            self.url = url
        else:
            self.url = None
        self.urlPattern = re.compile(config['urlPattern']) if 'urlPattern' in config else None
        self.items = []
        if 'items' in config:
            self.items = [NavItem(item_config) for item_config in config['items']]
        self._config = config

    def get_active_item(self):
        for item in self.items:
            if item.is_active():
                return item
        else:
            return None

    def is_active(self):
        for item in self.items:
            if item.is_active():
                return True
        if self.urlPattern is not None:
            return self.urlPattern.match(request.path)
        if self.url is not None:
            return request.path.startswith(self.url)
        else:
            return False

    def is_external(self):
        if hasattr(self, 'url'):
            return self.url.startswith("http://") or self.url.startswith("https://")
        else:
            return False

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, item):
        return self._config[item]


class Nav:
    def __init__(self, config):
        self._nav = {}
        for nav_id in config:
            self._nav[nav_id] = NavItem(config[nav_id])

    def __getitem__(self, item):
        return self._nav[item]


def process_video_nav(data: List[Dict]) -> List[Dict]:
    for item in data:
        process_video_nav_item(item)
    return data


def process_video_nav_item(data: Dict) -> Dict:
    if 'content' in data:
        for item in data['content']:
            process_video_nav_item(item)
    else:
        data['class'] = 'video-item'
        data['title_class'] = 'video-item-title'
        if is_external(data['url']):
            data['title_class'] += ' is_external'
        if 'description' in data:
            data['title_arguments'] = {
                'data-description': data['description']
            }
            del data['description']
    return data


def is_external(link: str):
    return 'www.youtube.com' not in link
