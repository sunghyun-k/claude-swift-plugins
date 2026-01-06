#!/usr/bin/env python3
"""번역 상태 확인"""

import json
import argparse
from utils import load


def get_all_languages(data):
    """파일에 사용된 모든 언어 코드 추출"""
    languages = set()
    for entry in data.get('strings', {}).values():
        locs = entry.get('localizations', {})
        languages.update(locs.keys())
    return sorted(languages)


def has_translation(entry, lang):
    """해당 언어의 번역이 있는지 확인"""
    locs = entry.get('localizations', {})
    if lang not in locs:
        return False
    loc = locs[lang]
    if 'stringUnit' in loc:
        value = loc['stringUnit'].get('value')
        return value is not None and value != ''
    if 'variations' in loc:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description='Show translation status')
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    data = load(args.file)
    strings = data.get('strings', {})
    total_keys = len(strings)

    if total_keys == 0:
        if args.json:
            print(json.dumps({'error': 'No keys found'}))
        else:
            print("No keys found")
        return

    languages = get_all_languages(data)
    status = {}

    for lang in languages:
        translated = sum(1 for entry in strings.values() if has_translation(entry, lang))
        percentage = round(translated / total_keys * 100, 1)
        status[lang] = {
            'translated': translated,
            'total': total_keys,
            'missing': total_keys - translated,
            'percentage': percentage
        }

    if args.json:
        print(json.dumps({'total_keys': total_keys, 'languages': status}, ensure_ascii=False, indent=2))
    else:
        # 읽기 쉬운 형식 출력
        print(f"Total keys: {total_keys}")
        print("-" * 40)

        # 완료율 순으로 정렬
        sorted_langs = sorted(status.items(), key=lambda x: x[1]['percentage'], reverse=True)

        for lang, info in sorted_langs:
            bar_len = 20
            filled = int(info['percentage'] / 100 * bar_len)
            bar = '=' * filled + '-' * (bar_len - filled)
            print(f"{lang:8} [{bar}] {info['percentage']:5.1f}% ({info['translated']}/{info['total']})")


if __name__ == "__main__":
    main()
