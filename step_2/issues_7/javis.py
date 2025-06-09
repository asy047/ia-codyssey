import os
import datetime
import sounddevice as sd
import scipy.io.wavfile as wav
from pathlib import Path
import speech_recognition as sr
import csv
import re
from pydub import AudioSegment
from pydub.silence import split_on_silence

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


class SpeechToTextConverter:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.records_dir = Path('records')
        self.csv_dir = Path('csv_outputs')
        self.csv_dir.mkdir(exist_ok=True)

    def get_audio_files(self, directory=None):
        """디렉토리 내 WAV 파일 목록을 반환합니다."""
        if directory is None:
            directory = self.records_dir
        else:
            directory = Path(directory)
        
        wav_files = list(directory.glob('*.wav'))
        return [file.name for file in wav_files]

    def split_audio_by_silence(self, audio_file_path):
        """음성 파일을 무음 구간으로 나누어 세그먼트별로 분할합니다."""
        audio = AudioSegment.from_wav(audio_file_path)
        
        # 무음 구간을 기준으로 분할 (최소 500ms 무음, -40dBFS 이하)
        chunks = split_on_silence(
            audio,
            min_silence_len=500,
            silence_thresh=-40,
            keep_silence=200
        )
        
        return chunks

    def speech_to_text(self, audio_file):
        """음성 파일에서 텍스트를 추출합니다."""
        audio_path = self.records_dir / audio_file
        
        if not audio_path.exists():
            print(f'파일을 찾을 수 없습니다: {audio_file}')
            return []

        results = []
        
        try:
            # 음성 파일을 세그먼트로 분할
            chunks = self.split_audio_by_silence(str(audio_path))
            
            print(f'{audio_file} 처리 중... ({len(chunks)}개 세그먼트 발견)')
            
            current_time = 0.0
            
            for i, chunk in enumerate(chunks):
                # 임시 WAV 파일로 저장
                temp_file = f'temp_chunk_{i}.wav'
                chunk.export(temp_file, format='wav')
                
                try:
                    # 음성 인식
                    with sr.AudioFile(temp_file) as source:
                        audio_data = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio_data, language='ko-KR')
                        
                        if text.strip():
                            results.append((round(current_time, 1), text))
                            print(f'[{current_time:.1f}s] {text}')
                
                except sr.UnknownValueError:
                    # 인식할 수 없는 음성
                    pass
                except sr.RequestError as e:
                    print(f'Google Speech Recognition 서비스 오류: {e}')
                finally:
                    # 임시 파일 삭제
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                
                # 세그먼트 길이만큼 시간 증가 (밀리초를 초로 변환)
                current_time += len(chunk) / 1000.0
        
        except Exception as e:
            print(f'음성 처리 중 오류 발생: {e}')
        
        return results

    def save_to_csv(self, audio_file, results):
        """인식 결과를 CSV 파일로 저장합니다."""
        if not results:
            print(f'{audio_file}에서 인식된 텍스트가 없습니다.')
            return
        
        # CSV 파일명 생성 (확장자를 .csv로 변경)
        csv_filename = Path(audio_file).stem + '.csv'
        csv_path = self.csv_dir / csv_filename
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # 헤더 작성
                writer.writerow(['시간(초)', '인식된 텍스트'])
                # 데이터 작성
                for time_stamp, text in results:
                    writer.writerow([time_stamp, text])
            
            print(f'CSV 파일로 저장되었습니다: {csv_filename}')
        
        except Exception as e:
            print(f'CSV 저장 중 오류 발생: {e}')

    def process_audio_file(self, audio_file):
        """음성 파일을 처리하여 텍스트 추출 및 CSV 저장을 수행합니다."""
        print(f'\n{audio_file} 처리 시작...')
        results = self.speech_to_text(audio_file)
        
        if results:
            self.save_to_csv(audio_file, results)
        else:
            print(f'{audio_file}에서 텍스트를 추출할 수 없습니다.')

    def process_all_audio_files(self):
        """모든 음성 파일을 처리합니다."""
        audio_files = self.get_audio_files()
        
        if not audio_files:
            print('처리할 음성 파일이 없습니다.')
            return
        
        print(f'{len(audio_files)}개의 음성 파일을 발견했습니다.')
        
        for audio_file in audio_files:
            self.process_audio_file(audio_file)

    def search_in_csv(self, keyword, directory=None):
        """CSV 파일에서 키워드를 검색합니다. (보너스 기능)"""
        if directory is None:
            directory = self.csv_dir
        else:
            directory = Path(directory)
        
        csv_files = list(directory.glob('*.csv'))
        
        if not csv_files:
            print('검색할 CSV 파일이 없습니다.')
            return
        
        found_results = []
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)  # 헤더 스킵
                    
                    for row in reader:
                        if len(row) >= 2:
                            time_stamp, text = row[0], row[1]
                            if keyword.lower() in text.lower():
                                found_results.append((csv_file.name, time_stamp, text))
            
            except Exception as e:
                print(f'{csv_file.name} 읽기 오류: {e}')
        
        if found_results:
            print(f'\n키워드 "{keyword}" 검색 결과:')
            for file_name, time_stamp, text in found_results:
                print(f'[{file_name}] {time_stamp}s: {text}')
        else:
            print(f'키워드 "{keyword}"를 찾을 수 없습니다.')

    def process_audio_files_from_directory(self, directory_path):
        """지정된 디렉토리의 모든 음성 파일을 처리합니다."""
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f'디렉토리를 찾을 수 없습니다: {directory_path}')
            return
        
        audio_files = list(directory.glob('*.wav'))
        
        if not audio_files:
            print(f'{directory_path}에 WAV 파일이 없습니다.')
            return
        
        print(f'{directory_path}에서 {len(audio_files)}개의 음성 파일을 발견했습니다.')
        
        # 처리 결과를 해당 디렉토리에 저장할 CSV 디렉토리 생성
        csv_output_dir = directory / 'csv_outputs'
        csv_output_dir.mkdir(exist_ok=True)
        
        for audio_file in audio_files:
            print(f'\n{audio_file.name} 처리 시작...')
            results = self.speech_to_text_from_path(audio_file)
            
            if results:
                self.save_to_csv_in_directory(audio_file.name, results, csv_output_dir)
            else:
                print(f'{audio_file.name}에서 텍스트를 추출할 수 없습니다.')

    def speech_to_text_from_path(self, audio_file_path):
        """지정된 경로의 음성 파일에서 텍스트를 추출합니다."""
        if not audio_file_path.exists():
            print(f'파일을 찾을 수 없습니다: {audio_file_path}')
            return []

        results = []
        
        try:
            # 음성 파일을 세그먼트로 분할
            chunks = self.split_audio_by_silence(str(audio_file_path))
            
            print(f'{audio_file_path.name} 처리 중... ({len(chunks)}개 세그먼트 발견)')
            
            current_time = 0.0
            
            for i, chunk in enumerate(chunks):
                # 임시 WAV 파일로 저장
                temp_file = f'temp_chunk_{i}.wav'
                chunk.export(temp_file, format='wav')
                
                try:
                    # 음성 인식
                    with sr.AudioFile(temp_file) as source:
                        audio_data = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio_data, language='ko-KR')
                        
                        if text.strip():
                            results.append((round(current_time, 1), text))
                            print(f'[{current_time:.1f}s] {text}')
                
                except sr.UnknownValueError:
                    # 인식할 수 없는 음성
                    pass
                except sr.RequestError as e:
                    print(f'Google Speech Recognition 서비스 오류: {e}')
                finally:
                    # 임시 파일 삭제
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                
                # 세그먼트 길이만큼 시간 증가 (밀리초를 초로 변환)
                current_time += len(chunk) / 1000.0
        
        except Exception as e:
            print(f'음성 처리 중 오류 발생: {e}')
        
        return results

    def save_to_csv_in_directory(self, audio_file, results, csv_directory):
        """인식 결과를 지정된 디렉토리의 CSV 파일로 저장합니다."""
        if not results:
            print(f'{audio_file}에서 인식된 텍스트가 없습니다.')
            return
        
        # CSV 파일명 생성 (확장자를 .csv로 변경)
        csv_filename = Path(audio_file).stem + '.csv'
        csv_path = csv_directory / csv_filename
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # 헤더 작성
                writer.writerow(['시간(초)', '인식된 텍스트'])
                # 데이터 작성
                for time_stamp, text in results:
                    writer.writerow([time_stamp, text])
            
            print(f'CSV 파일로 저장되었습니다: {csv_path}')
        
        except Exception as e:
            print(f'CSV 저장 중 오류 발생: {e}')


def main():
    recorder = VoiceRecorder()
    stt_converter = SpeechToTextConverter()
    
    while True:
        print('\n=== 자비스 음성 녹음 및 STT 시스템 ===')
        print('1. 녹음 시작')
        print('2. 녹음 파일 목록 보기')
        print('3. 특정 기간 녹음 파일 보기')
        print('4. STT - 모든 음성 파일을 텍스트로 변환')
        print('5. STT - 특정 음성 파일을 텍스트로 변환')
        print('6. STT - 다른 디렉토리의 음성 파일들 처리')
        print('7. 키워드 검색 (CSV 파일에서)')
        print('8. 종료')
        
        choice = input('\n원하는 작업을 선택하세요 (1-8): ')
        
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
            print('\n모든 음성 파일을 처리합니다...')
            stt_converter.process_all_audio_files()
        
        elif choice == '5':
            audio_files = stt_converter.get_audio_files()
            if not audio_files:
                print('처리할 음성 파일이 없습니다.')
            else:
                print('\n사용 가능한 음성 파일:')
                for i, file in enumerate(audio_files, 1):
                    print(f'{i}. {file}')
                
                try:
                    choice_idx = int(input('변환할 파일 번호를 선택하세요: ')) - 1
                    if 0 <= choice_idx < len(audio_files):
                        stt_converter.process_audio_file(audio_files[choice_idx])
                    else:
                        print('올바른 번호를 선택해주세요.')
                except ValueError:
                    print('올바른 숫자를 입력해주세요.')
        
        elif choice == '6':
            directory_path = input('처리할 디렉토리 경로를 입력하세요 (예: ../issues_8): ')
            if directory_path.strip():
                stt_converter.process_audio_files_from_directory(directory_path)
            else:
                print('디렉토리 경로를 입력해주세요.')
        
        elif choice == '7':
            keyword = input('검색할 키워드를 입력하세요: ')
            if keyword.strip():
                stt_converter.search_in_csv(keyword)
            else:
                print('키워드를 입력해주세요.')
        
        elif choice == '8':
            print('프로그램을 종료합니다.')
            break
        
        else:
            print('1부터 8 사이의 숫자를 입력해주세요.')

if __name__ == '__main__':
    main() 