#!/usr/bin/env python3
"""번역 키 추가"""

import sys
import json
import argparse
from utils import load, save


def parse_lang_arg(value):
    """--lang=ko:한국어 형태의 인자를 파싱"""
    if ':' not in value:
        raise argparse.ArgumentTypeError(f"Invalid format '{value}'. Use LANG:VALUE (e.g., ko:한국어)")
    lang, val = value.split(':', 1)
    return (lang.strip(), val)


def main():
    parser = argparse.ArgumentParser(
        description='Add translation key',
        epilog='Example: add.py file.xcstrings "KEY" --lang=ko:한국어 --lang=en:English --lang=ja:日本語'
    )
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('key', help='Key name')
    parser.add_argument('--lang', action='append', type=parse_lang_arg, metavar='LANG:VALUE',
                        help='Language translation (e.g., --lang=ko:한국어). Can be used multiple times.')
    parser.add_argument('--no-translate', action='store_true',
                        help='Mark as "should not translate" (e.g., for proper nouns like "App Store")')
    args = parser.parse_args()

    if not args.lang:
        print(json.dumps({'error': 'At least one --lang required (e.g., --lang=ko:한국어)'}))
        sys.exit(1)

    data = load(args.file)
    strings = data.setdefault('strings', {})

    if args.key in strings:
        print(json.dumps({'error': 'Key already exists', 'key': args.key}))
        sys.exit(1)

    localizations = {}
    for lang, value in args.lang:
        localizations[lang] = {'stringUnit': {'state': 'translated', 'value': value}}

    entry = {
        'extractionState': 'manual',
        'localizations': localizations
    }

    if getattr(args, 'no_translate', False):
        entry['shouldTranslate'] = False

    strings[args.key] = entry

    save(data, args.file)

    result = {'status': 'success', 'key': args.key, 'translations': {}}
    for lang, loc in localizations.items():
        result['translations'][lang] = loc['stringUnit']['value']
    if getattr(args, 'no_translate', False):
        result['shouldTranslate'] = False
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
