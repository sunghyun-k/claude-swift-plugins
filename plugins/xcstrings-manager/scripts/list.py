#!/usr/bin/env python3
"""키 목록 조회"""

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
    parser = argparse.ArgumentParser(description='List all keys')
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('--count', action='store_true', help='Show count only')
    parser.add_argument('--missing', metavar='LANG', nargs='?', const='all',
                        help='Show keys missing translation. Use --missing for all languages, --missing=ko for specific language')
    args = parser.parse_args()

    data = load(args.file)
    strings = data.get('strings', {})
    keys = sorted(strings.keys())

    if args.missing:
        all_langs = get_all_languages(data)

        if args.missing == 'all':
            # 모든 언어에 대해 누락된 키 조회
            result = {'languages': {}}
            for lang in all_langs:
                missing = [k for k in keys if not has_translation(strings[k], lang)]
                if missing:
                    result['languages'][lang] = {'count': len(missing), 'keys': missing}
            result['summary'] = {lang: len(result['languages'].get(lang, {}).get('keys', []))
                                for lang in all_langs}
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 특정 언어에 대해 누락된 키 조회
            lang = args.missing
            missing = [k for k in keys if not has_translation(strings[k], lang)]
            print(json.dumps({'language': lang, 'count': len(missing), 'keys': missing},
                           ensure_ascii=False, indent=2))
    elif args.count:
        print(json.dumps({'count': len(keys)}))
    else:
        print(json.dumps({'count': len(keys), 'keys': keys}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
