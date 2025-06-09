#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
키워드 검색 기능 테스트 스크립트
"""

import sys
from pathlib import Path

# 상위 디렉토리의 javis.py를 import하기 위한 경로 추가
sys.path.append(str(Path(__file__).parent.parent / 'issues_7'))

from javis import SpeechToTextConverter

def main():
    print('=== 키워드 검색 기능 테스트 ===')
    
    # STT 변환기 초기화
    stt_converter = SpeechToTextConverter()
    
    # 현재 디렉토리의 csv_outputs에서 검색
    csv_dir = Path(__file__).parent / 'csv_outputs'
    
    print(f'검색 디렉토리: {csv_dir}')
    
    # 테스트할 키워드들
    test_keywords = ['안녕', '가나다', '존재하지않는키워드']
    
    for keyword in test_keywords:
        print(f'\n--- 키워드 "{keyword}" 검색 ---')
        stt_converter.search_in_csv(keyword, csv_dir)

if __name__ == '__main__':
    main() 