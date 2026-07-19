#!/usr/bin/env python3
"""번역 수정"""

import sys
import json
import argparse
from utils import load, save, parse_plural_arg, parse_json_arg, collect_plurals, plural_localization


def parse_lang_arg(value):
    """--lang=ko:한국어 형태의 인자를 파싱"""
    if ':' not in value:
        raise argparse.ArgumentTypeError(f"Invalid format '{value}'. Use LANG:VALUE (e.g., ko:한국어)")
    lang, val = value.split(':', 1)
    return (lang.strip(), val)


def main():
    parser = argparse.ArgumentParser(
        description='Update translation',
        epilog='Example: update.py file.xcstrings "KEY" --lang=ko:한국어 --lang=ja:日本語'
    )
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('key', help='Key name')
    parser.add_argument('--lang', action='append', type=parse_lang_arg, metavar='LANG:VALUE',
                        help='Language translation (e.g., --lang=ko:한국어). Can be used multiple times.')
    parser.add_argument('--plural', action='append', type=parse_plural_arg, metavar='LANG:CATEGORY:VALUE',
                        help='Plural variation (e.g., --plural=ru:few:%%lld файла). '
                             'Categories: zero/one/two/few/many/other. Merges into existing plural '
                             'variations of that language. Can be used multiple times.')
    parser.add_argument('--json', action='append', type=parse_json_arg, metavar='LANG:JSON', dest='json_loc',
                        help='Raw localization object as JSON, replaces the whole localization of that '
                             'language. For complex structures like substitutions or device variations.')
    translate_group = parser.add_mutually_exclusive_group()
    translate_group.add_argument('--no-translate', action='store_true',
                                 help='Mark as "should not translate"')
    translate_group.add_argument('--translate', action='store_true',
                                 help='Remove "should not translate" mark')
    args = parser.parse_args()

    has_update = (args.lang or args.plural or args.json_loc
                  or getattr(args, 'no_translate', False) or getattr(args, 'translate', False))
    if not has_update:
        print(json.dumps({'error': 'At least one option required (--lang, --plural, --json, --no-translate, or --translate)'}))
        sys.exit(1)

    data = load(args.file)
    strings = data.get('strings', {})

    if args.key not in strings:
        print(json.dumps({'error': 'Key not found', 'key': args.key}))
        sys.exit(1)

    entry = strings[args.key]
    locs = entry.setdefault('localizations', {})
    updated = {}

    lang_set = {lang for lang, _ in (args.lang or [])}
    plurals = collect_plurals(args.plural or [])
    json_set = {lang for lang, _ in (args.json_loc or [])}
    overlap = (lang_set & set(plurals)) | (lang_set & json_set) | (set(plurals) & json_set)
    if overlap:
        print(json.dumps({'error': f"Language(s) given in multiple options: {', '.join(sorted(overlap))}"}))
        sys.exit(1)

    if args.lang:
        for lang, value in args.lang:
            locs[lang] = {'stringUnit': {'state': 'translated', 'value': value}}
            updated[lang] = value

    for lang, categories in plurals.items():
        existing = locs.get(lang, {})
        plural = existing.get('variations', {}).get('plural', {}) if 'variations' in existing else {}
        for cat, val in categories.items():
            plural[cat] = {'stringUnit': {'state': 'translated', 'value': val}}
        locs[lang] = {'variations': {'plural': plural}}
        updated[lang] = {cat: v['stringUnit']['value'] for cat, v in plural.items()}

    for lang, obj in (args.json_loc or []):
        locs[lang] = obj
        updated[lang] = obj

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
