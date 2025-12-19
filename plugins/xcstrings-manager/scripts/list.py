#!/usr/bin/env python3
"""키 목록 조회"""

import json
import argparse
from utils import load


def main():
    parser = argparse.ArgumentParser(description='List all keys')
    parser.add_argument('file', help='Path to .xcstrings file')
    parser.add_argument('--count', action='store_true', help='Show count only')
    args = parser.parse_args()

    data = load(args.file)
    strings = data.get('strings', {})
    keys = sorted(strings.keys())

    if args.count:
        print(json.dumps({'count': len(keys)}))
    else:
        print(json.dumps({'count': len(keys), 'keys': keys}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
