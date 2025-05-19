import zipfile
import itertools
import time
import string
from datetime import datetime
import multiprocessing
from multiprocessing import Pool, Manager
import os

def generate_mars_patterns():
    """
    'mars' 관련 패턴을 생성하는 제너레이터
    """
    # mars + 숫자 조합
    for i in range(100):
        yield f'mars{i:02d}'  # mars00, mars01, ..., mars99
    
    # mars 변형 + 숫자
    variations = ['mars', 'Mars', 'MARS']
    for var in variations:
        for i in range(100):
            yield f'{var}{i:02d}'
    
    # mars + 특수 숫자
    special_numbers = ['06', '69', '96', '00', '01', '02', '03', '04', '05', '07', '08', '09']
    for num in special_numbers:
        yield f'mars{num}'

def generate_password_chunk(start_idx, chunk_size):
    """
    특정 범위의 비밀번호 조합을 생성하는 제너레이터 함수
    
    Args:
        start_idx (int): 시작 인덱스
        chunk_size (int): 생성할 비밀번호 개수
    """
    # 알파벳과 숫자 분리
    letters = string.ascii_lowercase
    digits = string.digits
    chars = letters + digits
    total_chars = len(chars)
    
    # 체계적인 조합 생성
    for i in range(start_idx, start_idx + chunk_size):
        # 6자리 비밀번호 생성
        password = []
        temp = i
        for _ in range(6):
            password.append(chars[temp % total_chars])
            temp //= total_chars
        yield ''.join(reversed(password))

def test_password(zip_path, password):
    """
    주어진 비밀번호로 ZIP 파일을 열 수 있는지 테스트
    
    Args:
        zip_path (str): ZIP 파일 경로
        password (str): 테스트할 비밀번호
        
    Returns:
        bool: 비밀번호가 맞으면 True, 아니면 False
    """
    try:
        with zipfile.ZipFile(zip_path) as zf:
            first_file = zf.namelist()[0]
            zf.read(first_file, pwd=password.encode())
            return True
    except:
        return False

def process_chunk(args):
    """
    비밀번호 청크를 처리하는 함수
    
    Args:
        args (tuple): (시작 인덱스, 청크 크기, ZIP 파일 경로, 공유 변수들)
    """
    start_idx, chunk_size, zip_path, shared_vars = args
    attempts = 0
    chunk_start_time = time.time()
    last_update_time = time.time()
    
    for password in generate_password_chunk(start_idx, chunk_size):
        attempts += 1
        
        if shared_vars['found'].value:
            return
        
        current_time = time.time()
        if current_time - last_update_time >= 5:  # 5초마다 진행상황 업데이트
            with shared_vars['lock']:
                shared_vars['total_attempts'].value += attempts
                current_attempts = shared_vars['total_attempts'].value
                elapsed_time = current_time - shared_vars['start_time'].value
                attempts_per_second = current_attempts / elapsed_time
                remaining_combinations = 36 ** 6 - current_attempts
                estimated_time = remaining_combinations / (attempts_per_second * shared_vars['num_processes'].value)
                
                print(f'\n현재 진행상황:')
                print(f'시도 횟수: {current_attempts:,}')
                print(f'경과 시간: {elapsed_time:.2f}초')
                print(f'초당 시도 횟수: {attempts_per_second:.2f}')
                print(f'예상 남은 시간: {estimated_time/60:.2f}분')
                print(f'현재 시도 중인 비밀번호: {password}')
            
            attempts = 0
            last_update_time = current_time
        
        if test_password(zip_path, password):
            with shared_vars['lock']:
                if not shared_vars['found'].value:
                    shared_vars['found'].value = True
                    shared_vars['password'].value = password
                    shared_vars['end_time'].value = time.time()
                    return password
    
    return None

def unlock_zip(zip_path='emergency_storage_key.zip'):
    """
    ZIP 파일의 비밀번호를 찾는 함수 (최적화된 브루트포스 버전)
    
    Args:
        zip_path (str): ZIP 파일 경로
        
    Returns:
        str: 찾은 비밀번호 또는 None
    """
    if not os.path.exists(zip_path):
        print(f'오류: {zip_path} 파일을 찾을 수 없습니다.')
        return None
    
    try:
        with zipfile.ZipFile(zip_path) as zf:
            print(f'ZIP 파일 내 파일 목록: {zf.namelist()}')
    except zipfile.BadZipFile:
        print(f'오류: {zip_path} 파일이 유효한 ZIP 파일이 아닙니다.')
        return None
    
    # 멀티프로세싱 설정
    num_processes = multiprocessing.cpu_count()
    total_combinations = 36 ** 6
    chunk_size = total_combinations // (num_processes * 20)  # 더 작은 청크로 분할
    
    # 공유 변수 설정
    manager = Manager()
    shared_vars = {
        'found': manager.Value('b', False),
        'password': manager.Value('c', ''),
        'start_time': manager.Value('d', time.time()),
        'end_time': manager.Value('d', 0),
        'total_attempts': manager.Value('i', 0),
        'num_processes': manager.Value('i', num_processes),
        'lock': manager.Lock()
    }
    
    print(f'비밀번호 찾기 시작: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'CPU 코어 수: {num_processes}')
    print(f'프로세스 수: {num_processes}')
    print(f'청크 크기: {chunk_size:,}')
    print(f'총 조합 수: {total_combinations:,}')
    
    # 작업 청크 생성
    chunks = [(i * chunk_size, chunk_size, zip_path, shared_vars) 
             for i in range(num_processes * 20)]
    
    # 병렬 처리 실행
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_chunk, chunks)
    
    # 결과 확인
    if shared_vars['found'].value:
        password = shared_vars['password'].value
        total_time = shared_vars['end_time'].value - shared_vars['start_time'].value
        
        print(f'\n비밀번호 발견!')
        print(f'시도 횟수: {shared_vars["total_attempts"].value:,}')
        print(f'총 소요 시간: {total_time:.2f}초')
        
        # 비밀번호를 파일에 저장
        with open('password.txt', 'w') as f:
            f.write(password)
        
        return password
    
    print('\n비밀번호를 찾지 못했습니다.')
    return None

if __name__ == '__main__':
    multiprocessing.freeze_support()  # Windows에서 실행 시 필요
    unlock_zip() 