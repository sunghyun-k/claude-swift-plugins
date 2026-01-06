#!/usr/bin/env python3
"""번역 수정"""

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
        description='Update translation',
        epilog='Example: update.py file.xcstrings "KEY" --ko="한국어" --lang=ja:日本語'
    )
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('key', help='Key name')
    parser.add_argument('--ko', help='Korean translation')
    parser.add_argument('--en', help='English translation')
    parser.add_argument('--lang', action='append', type=parse_lang_arg, metavar='LANG:VALUE',
                        help='Additional language (e.g., --lang=ja:日本語). Can be used multiple times.')
    translate_group = parser.add_mutually_exclusive_group()
    translate_group.add_argument('--no-translate', action='store_true',
                                 help='Mark as "should not translate"')
    translate_group.add_argument('--translate', action='store_true',
                                 help='Remove "should not translate" mark')
    args = parser.parse_args()

    has_update = args.ko or args.en or args.lang or getattr(args, 'no_translate', False) or getattr(args, 'translate', False)
    if not has_update:
        print(json.dumps({'error': 'At least one option required (--ko, --en, --lang, --no-translate, or --translate)'}))
        sys.exit(1)

    data = load(args.file)
    strings = data.get('strings', {})

    if args.key not in strings:
        print(json.dumps({'error': 'Key not found', 'key': args.key}))
        sys.exit(1)

    entry = strings[args.key]
    locs = entry.setdefault('localizations', {})
    updated = {}

    if args.ko:
        locs['ko'] = {'stringUnit': {'state': 'translated', 'value': args.ko}}
        updated['ko'] = args.ko
    if args.en:
        locs['en'] = {'stringUnit': {'state': 'translated', 'value': args.en}}
        updated['en'] = args.en

    # --lang 옵션 처리
    if args.lang:
        for lang, value in args.lang:
            locs[lang] = {'stringUnit': {'state': 'translated', 'value': value}}
            updated[lang] = value

    # shouldTranslate 처리
    result = {'status': 'success', 'key': args.key}
    if updated:
        result['updated'] = updated

    if getattr(args, 'no_translate', False):
        entry['shouldTranslate'] = False
        result['shouldTranslate'] = False
    elif getattr(args, 'translate', False):
        entry.pop('shouldTranslate', None)
        result['shouldTranslate'] = True

    save(data, args.file)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
