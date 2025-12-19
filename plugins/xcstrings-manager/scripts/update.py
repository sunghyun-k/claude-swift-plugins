#!/usr/bin/env python3
"""번역 수정"""

import sys
import json
import argparse
from utils import load, save

def main():
    parser = argparse.ArgumentParser(description='Update translation')
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('key', help='Key name')
    parser.add_argument('--ko', help='Korean translation')
    parser.add_argument('--en', help='English translation')
    args = parser.parse_args()

    if not args.ko and not args.en:
        print(json.dumps({'error': 'At least --ko or --en required'}))
        sys.exit(1)

    data = load(args.file)
    strings = data.get('strings', {})

    if args.key not in strings:
        print(json.dumps({'error': 'Key not found', 'key': args.key}))
        sys.exit(1)

    entry = strings[args.key]
    locs = entry.setdefault('localizations', {})

    if args.ko:
        locs['ko'] = {'stringUnit': {'state': 'translated', 'value': args.ko}}
    if args.en:
        locs['en'] = {'stringUnit': {'state': 'translated', 'value': args.en}}

    save(data, args.file)
    print(json.dumps({'status': 'success', 'key': args.key, 'ko': args.ko, 'en': args.en}))

if __name__ == "__main__":
    main()
