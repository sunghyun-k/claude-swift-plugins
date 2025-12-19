#!/usr/bin/env python3
"""xcstrings 파일 처리 유틸리티"""

import json
import locale

# Xcode와 동일한 정렬을 위해 locale 설정
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

def load(path):
    """xcstrings 파일 로드"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save(data, path):
    """xcstrings 파일 저장 (Xcode 포맷 유지)"""
    def sort_dict(obj):
        if isinstance(obj, dict):
            # Xcode의 localizedStandardCompare와 동일하게 locale-aware 정렬
            return {k: sort_dict(v) for k, v in sorted(obj.items(), key=lambda x: locale.strxfrm(x[0]))}
        elif isinstance(obj, list):
            return [sort_dict(i) for i in obj]
        return obj

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sort_dict(data), f, ensure_ascii=False, indent=2, separators=(',', ' : '))
