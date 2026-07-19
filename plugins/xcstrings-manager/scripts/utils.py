#!/usr/bin/env python3
"""xcstrings 파일 처리 유틸리티"""

import json
import locale

# Xcode와 동일한 정렬을 위해 locale 설정
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

PLURAL_CATEGORIES = ('zero', 'one', 'two', 'few', 'many', 'other')


def parse_plural_arg(value):
    """--plural=ru:few:%lld файла 형태의 인자를 파싱"""
    import argparse
    parts = value.split(':', 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"Invalid format '{value}'. Use LANG:CATEGORY:VALUE (e.g., ru:few:%lld файла)")
    lang, category, val = parts[0].strip(), parts[1].strip(), parts[2]
    if category not in PLURAL_CATEGORIES:
        raise argparse.ArgumentTypeError(
            f"Invalid plural category '{category}'. Use one of: {', '.join(PLURAL_CATEGORIES)}")
    return (lang, category, val)


def parse_json_arg(value):
    """--json=ru:{...} 형태의 인자를 파싱 (localization 객체를 그대로 지정)"""
    import argparse
    if ':' not in value:
        raise argparse.ArgumentTypeError(
            f"Invalid format '{value}'. Use LANG:JSON (e.g., ru:{{\"variations\": ...}})")
    lang, raw = value.split(':', 1)
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        raise argparse.ArgumentTypeError(f"Invalid JSON for '{lang.strip()}': {e}")
    if not isinstance(obj, dict):
        raise argparse.ArgumentTypeError(f"JSON for '{lang.strip()}' must be an object")
    return (lang.strip(), obj)


def collect_plurals(plural_args):
    """(lang, category, value) 리스트를 {lang: {category: value}}로 병합"""
    result = {}
    for lang, category, value in plural_args:
        result.setdefault(lang, {})[category] = value
    return result


def plural_localization(categories):
    """{category: value} → xcstrings variations.plural localization 객체"""
    return {
        'variations': {
            'plural': {
                cat: {'stringUnit': {'state': 'translated', 'value': val}}
                for cat, val in categories.items()
            }
        }
    }


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
