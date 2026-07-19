#!/usr/bin/env python3
"""번역 키 추가"""

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
        description='Add translation key',
        epilog='Example: add.py file.xcstrings "KEY" --lang=ko:한국어 --lang=en:English --lang=ja:日本語'
    )
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('key', help='Key name')
    parser.add_argument('--lang', action='append', type=parse_lang_arg, metavar='LANG:VALUE',
                        help='Language translation (e.g., --lang=ko:한국어). Can be used multiple times.')
    parser.add_argument('--plural', action='append', type=parse_plural_arg, metavar='LANG:CATEGORY:VALUE',
                        help='Plural variation (e.g., --plural=ru:few:%%lld файла). '
                             'Categories: zero/one/two/few/many/other. Can be used multiple times.')
    parser.add_argument('--json', action='append', type=parse_json_arg, metavar='LANG:JSON', dest='json_loc',
                        help='Raw localization object as JSON, for complex structures like '
                             'substitutions or device variations (e.g., --json=en:\'{"stringUnit": ...}\')')
    parser.add_argument('--no-translate', action='store_true',
                        help='Mark as "should not translate" (e.g., for proper nouns like "App Store")')
    args = parser.parse_args()

    if not (args.lang or args.plural or args.json_loc):
        print(json.dumps({'error': 'At least one of --lang, --plural, or --json required'}))
        sys.exit(1)

    data = load(args.file)
    strings = data.setdefault('strings', {})

    if args.key in strings:
        print(json.dumps({'error': 'Key already exists', 'key': args.key}))
        sys.exit(1)

    localizations = {}
    for lang, value in (args.lang or []):
        localizations[lang] = {'stringUnit': {'state': 'translated', 'value': value}}
    for lang, categories in collect_plurals(args.plural or []).items():
        if lang in localizations:
            print(json.dumps({'error': f"Language '{lang}' given in both --lang and --plural"}))
            sys.exit(1)
        localizations[lang] = plural_localization(categories)
    for lang, obj in (args.json_loc or []):
        if lang in localizations:
            print(json.dumps({'error': f"Language '{lang}' given more than once (--json overlaps --lang/--plural)"}))
            sys.exit(1)
        localizations[lang] = obj

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
        if 'stringUnit' in loc:
            result['translations'][lang] = loc['stringUnit']['value']
        elif 'variations' in loc and 'plural' in loc['variations']:
            result['translations'][lang] = {
                cat: v.get('stringUnit', {}).get('value')
                for cat, v in loc['variations']['plural'].items()
            }
        else:
            result['translations'][lang] = loc
    if getattr(args, 'no_translate', False):
        result['shouldTranslate'] = False
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
