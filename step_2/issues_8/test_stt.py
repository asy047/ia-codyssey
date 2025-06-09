#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
문제 8: 음성에서 문자로 변환 테스트 스크립트
issues_8 폴더의 음성 파일들을 STT로 처리하여 CSV로 저장합니다.
"""

import sys
import os
from pathlib import Path

# 상위 디렉토리의 javis.py를 import하기 위한 경로 추가
sys.path.append(str(Path(__file__).parent.parent / 'issues_7'))

from javis import SpeechToTextConverter

def main():
    print('=== 문제 8: 음성에서 문자로 변환 ===')
    
    # 현재 디렉토리 설정
    current_dir = Path(__file__).parent
    
    # STT 변환기 초기화
    stt_converter = SpeechToTextConverter()
    
    print(f'현재 디렉토리: {current_dir}')
    print('음성 파일을 검색하는 중...')
    
    # 현재 디렉토리의 음성 파일들 처리
    stt_converter.process_audio_files_from_directory(current_dir)
    
    print('\n=== 처리 완료 ===')
    print('CSV 파일들이 csv_outputs 폴더에 저장되었습니다.')

if __name__ == '__main__':
    main() 