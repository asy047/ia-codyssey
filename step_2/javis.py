import os
import datetime
import sounddevice as sd
import scipy.io.wavfile as wav
from pathlib import Path

class VoiceRecorder:
    def __init__(self):
        self.records_dir = Path('records')
        self.records_dir.mkdir(exist_ok=True)
        self.sample_rate = 44100
        self.channels = 1

    def get_current_timestamp(self):
        """현재 시간을 파일명 형식으로 반환합니다."""
        now = datetime.datetime.now()
        return now.strftime('%Y%m%d-%H%M%S')

    def record_audio(self, duration=5):
        """음성을 녹음하고 파일로 저장합니다."""
        print(f'{duration}초 동안 녹음을 시작합니다...')
        
        # 녹음 시작
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels
        )
        sd.wait()
        
        # 파일명 생성 및 저장
        filename = f'{self.get_current_timestamp()}.wav'
        filepath = self.records_dir / filename
        
        # WAV 파일로 저장
        wav.write(str(filepath), self.sample_rate, recording)
        print(f'녹음이 저장되었습니다: {filename}')
        return filename

    def list_recordings(self, start_date=None, end_date=None):
        """녹음 파일 목록을 반환합니다. 날짜 범위 지정 가능합니다."""
        files = []
        for file in self.records_dir.glob('*.wav'):
            try:
                # 파일명에서 날짜 추출 (YYYYMMDD-HHMMSS.wav)
                date_str = file.stem.split('-')[0]
                file_date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
                
                if start_date and end_date:
                    if start_date <= file_date <= end_date:
                        files.append(file.name)
                else:
                    files.append(file.name)
            except ValueError:
                continue
        
        return sorted(files)

def main():
    recorder = VoiceRecorder()
    
    while True:
        print('\n=== 자비스 음성 녹음 시스템 ===')
        print('1. 녹음 시작')
        print('2. 녹음 파일 목록 보기')
        print('3. 특정 기간 녹음 파일 보기')
        print('4. 종료')
        
        choice = input('\n원하는 작업을 선택하세요 (1-4): ')
        
        if choice == '1':
            try:
                duration = int(input('녹음 시간(초)을 입력하세요: '))
                recorder.record_audio(duration)
            except ValueError:
                print('올바른 숫자를 입력해주세요.')
        
        elif choice == '2':
            files = recorder.list_recordings()
            if files:
                print('\n저장된 녹음 파일:')
                for file in files:
                    print(f'- {file}')
            else:
                print('저장된 녹음 파일이 없습니다.')
        
        elif choice == '3':
            try:
                start = input('시작 날짜 (YYYYMMDD): ')
                end = input('종료 날짜 (YYYYMMDD): ')
                start_date = datetime.datetime.strptime(start, '%Y%m%d').date()
                end_date = datetime.datetime.strptime(end, '%Y%m%d').date()
                
                files = recorder.list_recordings(start_date, end_date)
                if files:
                    print(f'\n{start}부터 {end}까지의 녹음 파일:')
                    for file in files:
                        print(f'- {file}')
                else:
                    print('해당 기간의 녹음 파일이 없습니다.')
            except ValueError:
                print('올바른 날짜 형식(YYYYMMDD)으로 입력해주세요.')
        
        elif choice == '4':
            print('프로그램을 종료합니다.')
            break
        
        else:
            print('1부터 4 사이의 숫자를 입력해주세요.')

if __name__ == '__main__':
    main() 