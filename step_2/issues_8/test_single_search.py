#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'issues_7'))

from javis import SpeechToTextConverter

def main():
    print('=== 단일 키워드 검색 테스트 ===')
    
    stt_converter = SpeechToTextConverter()
    csv_dir = Path(__file__).parent / 'csv_outputs'
    
    print(f'검색 디렉토리: {csv_dir}')
    print(f'CSV 파일들: {list(csv_dir.glob("*.csv"))}')
    
    keyword = '가나다'
    print(f'\n키워드 "{keyword}" 검색:')
    stt_converter.search_in_csv(keyword, csv_dir)

if __name__ == '__main__':
    main() 