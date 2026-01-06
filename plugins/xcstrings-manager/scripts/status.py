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

    # 번역 제외 키 분리
    no_translate_keys = [k for k, v in strings.items() if v.get('shouldTranslate') is False]
    translatable_strings = {k: v for k, v in strings.items() if v.get('shouldTranslate') is not False}
    translatable_count = len(translatable_strings)

    languages = get_all_languages(data)
    status = {}

    for lang in languages:
        # 번역 대상 키에서만 번역 완료율 계산
        translated = sum(1 for entry in translatable_strings.values() if has_translation(entry, lang))
        percentage = round(translated / translatable_count * 100, 1) if translatable_count > 0 else 0
        status[lang] = {
            'translated': translated,
            'total': translatable_count,
            'missing': translatable_count - translated,
            'percentage': percentage
        }

    if args.json:
        result = {
            'total_keys': total_keys,
            'translatable_keys': translatable_count,
            'no_translate_keys': len(no_translate_keys),
            'languages': status
        }
        if no_translate_keys:
            result['no_translate_list'] = sorted(no_translate_keys)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 읽기 쉬운 형식 출력
        print(f"Total keys: {total_keys}")
        if no_translate_keys:
            print(f"  - Translatable: {translatable_count}")
            print(f"  - No translate: {len(no_translate_keys)} ({', '.join(sorted(no_translate_keys))})")
        print("-" * 50)

        # 완료율 순으로 정렬
        sorted_langs = sorted(status.items(), key=lambda x: x[1]['percentage'], reverse=True)

        for lang, info in sorted_langs:
            bar_len = 20
            filled = int(info['percentage'] / 100 * bar_len)
            bar = '=' * filled + '-' * (bar_len - filled)
            print(f"{lang:8} [{bar}] {info['percentage']:5.1f}% ({info['translated']}/{info['total']})")


if __name__ == "__main__":
    main()
