#!/usr/bin/env python3
"""번역 키 추가"""

import sys
import json
import argparse
from utils import load, save


def parse_lang_arg(value):
    """--lang=ko:한국어 형태의 인자를 파싱"""
    if ':' not in value:
        raise argparse.ArgumentTypeError(f"Invalid format '{value}'. Use LANG:VALUE (e.g., ja:日本語)")
    lang, val = value.split(':', 1)
    return (lang.strip(), val)


def main():
    parser = argparse.ArgumentParser(
        description='Add translation key',
        epilog='Example: add.py file.xcstrings "KEY" --ko="한국어" --en="English" --lang=ja:日本語 --lang=zh-Hans:中文'
    )
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('key', help='Key name')
    parser.add_argument('--ko', help='Korean translation')
    parser.add_argument('--en', help='English translation')
    parser.add_argument('--lang', action='append', type=parse_lang_arg, metavar='LANG:VALUE',
                        help='Additional language (e.g., --lang=ja:日本語). Can be used multiple times.')
    args = parser.parse_args()

    # 최소 하나의 번역 필요
    has_translation = args.ko or args.en or args.lang
    if not has_translation:
        print(json.dumps({'error': 'At least one translation required (--ko, --en, or --lang)'}))
        sys.exit(1)

    data = load(args.file)
    strings = data.setdefault('strings', {})

    if args.key in strings:
        print(json.dumps({'error': 'Key already exists', 'key': args.key}))
        sys.exit(1)

    localizations = {}

    if args.ko:
        localizations['ko'] = {'stringUnit': {'state': 'translated', 'value': args.ko}}
    if args.en:
        localizations['en'] = {'stringUnit': {'state': 'translated', 'value': args.en}}

    # --lang 옵션 처리
    if args.lang:
        for lang, value in args.lang:
            localizations[lang] = {'stringUnit': {'state': 'translated', 'value': value}}

    strings[args.key] = {
        'extractionState': 'manual',
        'localizations': localizations
    }

    save(data, args.file)

    result = {'status': 'success', 'key': args.key, 'translations': {}}
    for lang, loc in localizations.items():
        result['translations'][lang] = loc['stringUnit']['value']
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
