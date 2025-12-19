#!/usr/bin/env python3
"""번역 키 추가"""

import sys
import json
import argparse
from utils import load, save

def main():
    parser = argparse.ArgumentParser(description='Add translation key')
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('key', help='Key name')
    parser.add_argument('--ko', required=True, help='Korean translation')
    parser.add_argument('--en', required=True, help='English translation')
    args = parser.parse_args()

    data = load(args.file)
    strings = data.setdefault('strings', {})

    if args.key in strings:
        print(json.dumps({'error': 'Key already exists', 'key': args.key}))
        sys.exit(1)

    strings[args.key] = {
        'extractionState': 'manual',
        'localizations': {
            'ko': {'stringUnit': {'state': 'translated', 'value': args.ko}},
            'en': {'stringUnit': {'state': 'translated', 'value': args.en}}
        }
    }

    save(data, args.file)
    print(json.dumps({'status': 'success', 'key': args.key, 'ko': args.ko, 'en': args.en}))

if __name__ == "__main__":
    main()
