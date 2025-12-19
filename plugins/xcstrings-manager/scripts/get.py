#!/usr/bin/env python3
"""번역 조회"""

import sys
import json
import argparse
from utils import load

def get_value(entry, lang):
    """언어별 번역값 추출"""
    locs = entry.get('localizations', {})
    if lang not in locs:
        return None
    loc = locs[lang]
    if 'stringUnit' in loc:
        return loc['stringUnit'].get('value')
    if 'variations' in loc and 'plural' in loc['variations']:
        return {k: v.get('stringUnit', {}).get('value')
                for k, v in loc['variations']['plural'].items()}
    return None

def main():
    parser = argparse.ArgumentParser(description='Get translation')
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('key', help='Key name')
    args = parser.parse_args()

    data = load(args.file)
    strings = data.get('strings', {})

    if args.key not in strings:
        print(json.dumps({'error': 'Key not found', 'key': args.key}))
        sys.exit(1)

    entry = strings[args.key]
    result = {
        'key': args.key,
        'ko': get_value(entry, 'ko'),
        'en': get_value(entry, 'en')
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
