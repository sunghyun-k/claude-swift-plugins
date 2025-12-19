#!/usr/bin/env python3
"""번역 키 삭제"""

import sys
import json
import argparse
from utils import load, save

def main():
    parser = argparse.ArgumentParser(description='Delete translation key')
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('key', help='Key name')
    args = parser.parse_args()

    data = load(args.file)
    strings = data.get('strings', {})

    if args.key not in strings:
        print(json.dumps({'error': 'Key not found', 'key': args.key}))
        sys.exit(1)

    del strings[args.key]
    save(data, args.file)
    print(json.dumps({'status': 'success', 'deleted': args.key}))

if __name__ == "__main__":
    main()
