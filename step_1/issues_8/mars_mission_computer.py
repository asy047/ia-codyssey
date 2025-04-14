import platform  # 운영체제 정보(OS 이름, 버전 등)를 가져오기 위한 표준 모듈
import os         # CPU 코어 수 등 기본 시스템 정보에 사용
import json       # 결과를 JSON 형식으로 출력하기 위한 모듈
import subprocess # 시스템 명령어를 실행하기 위한 모듈


class MissionComputer:
    def __init__(self):
        # 설정 파일(setting.txt)로부터 어떤 항목을 출력할지 설정값을 불러옴
        self.settings = self._load_settings()

    def _load_settings(self):
        # 기본 출력 설정값 (전부 True로 기본 세팅)
        settings = {
            'os': True,
            'os_version': True,
            'cpu_type': True,
            'cpu_cores': True,
            'memory_total': True,
            'cpu_usage': True,
            'memory_usage': True
        }

        # setting.txt 파일에서 항목별 true/false 설정값을 읽어옴
        try:
            with open('setting.txt', 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        if key in settings:
                            settings[key] = value.lower() == 'true'
        except FileNotFoundError:
            # 설정 파일이 없으면 기본값 그대로 사용
            pass

        return settings

    def get_mission_computer_info(self):
        try:
            info = {}

            # OS 이름
            if self.settings['os']:
                info['Operating System'] = platform.system()

            # OS 버전
            if self.settings['os_version']:
                info['OS Version'] = platform.version()

            # CPU 프로세서 이름
            if self.settings['cpu_type']:
                info['CPU Type'] = platform.processor()

            # CPU 코어 수
            if self.settings['cpu_cores']:
                info['CPU Cores'] = os.cpu_count()

            # 메모리 용량 (MB 단위)
            if self.settings['memory_total']:
                # Windows에서 메모리 총량 가져오기
                if platform.system() == 'Windows':
                    output = subprocess.check_output(
                        ['wmic', 'ComputerSystem', 'get', 'TotalPhysicalMemory'],
                        universal_newlines=True
                    )
                    # 숫자만 필터링해서 추출
                    lines = [line.strip() for line in output.strip().split('\n') if line.strip().isdigit()]
                    if lines:
                        memory_bytes = int(lines[0])
                        info['Total Memory (MB)'] = memory_bytes // (1024 * 1024)
                    else:
                        info['Total Memory (MB)'] = 'Unknown'
                else:
                    # Linux에서 /proc/meminfo에서 총 메모리 읽기
                    with open('/proc/meminfo', 'r') as memfile:
                        for line in memfile:
                            if 'MemTotal' in line:
                                mem_kb = int(line.split()[1])
                                info['Total Memory (MB)'] = mem_kb // 1024
                                break

            # JSON 형식으로 출력
            print('System Information:')
            print(json.dumps(info, indent=4))

        except Exception as e:
            print(f'Error getting system information: {e}')

    def get_mission_computer_load(self):
        try:
            load = {}

            if platform.system() == 'Windows':
                # CPU 사용률 가져오기
                if self.settings['cpu_usage']:
                    output = subprocess.check_output(
                        ['wmic', 'cpu', 'get', 'LoadPercentage'],
                        universal_newlines=True
                    )
                    lines = [line.strip() for line in output.strip().split('\n') if line.strip().isdigit()]
                    if lines:
                        load['CPU Usage (%)'] = int(lines[0])
                    else:
                        load['CPU Usage (%)'] = 'Unknown'

                # 메모리 사용률 계산 = 100 - (사용 가능한 메모리 / 전체 메모리)
                if self.settings['memory_usage']:
                    output = subprocess.check_output(
                        ['wmic', 'OS', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize', '/Value'],
                        universal_newlines=True
                    )
                    values = {}
                    for line in output.strip().split('\n'):
                        if '=' in line:
                            key, val = line.strip().split('=')
                            if val.strip().isdigit():
                                values[key.strip()] = int(val.strip())
                    total = values.get('TotalVisibleMemorySize', 1)
                    free = values.get('FreePhysicalMemory', 0)
                    usage = 100 - int((free / total) * 100)
                    load['Memory Usage (%)'] = usage

            else:
                # Linux에서 top 명령어로 CPU 사용률 파싱
                if self.settings['cpu_usage']:
                    output = subprocess.check_output(['top', '-bn1'], universal_newlines=True)
                    for line in output.split('\n'):
                        if 'Cpu(s)' in line:
                            usage_part = line.split('%')[0]
                            usage = float(usage_part.split()[-1])
                            load['CPU Usage (%)'] = round(100 - usage, 2)
                            break

                # /proc/meminfo를 이용해 메모리 사용률 계산
                if self.settings['memory_usage']:
                    with open('/proc/meminfo', 'r') as memfile:
                        meminfo = {}
                        for line in memfile:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                key = parts[0]
                                value = parts[1].strip().split()[0]
                                meminfo[key] = int(value)

                        total = meminfo['MemTotal']
                        free = meminfo['MemFree'] + meminfo.get('Buffers', 0) + meminfo.get('Cached', 0)
                        usage = 100 - int((free / total) * 100)
                        load['Memory Usage (%)'] = usage

            # JSON 형식으로 출력
            print('System Load:')
            print(json.dumps(load, indent=4))

        except Exception as e:
            print(f'Error getting system load: {e}')


# 프로그램 진입점: 인스턴스를 만들고 두 개의 정보 메서드를 호출
if __name__ == '__main__':
    runComputer = MissionComputer()
    runComputer.get_mission_computer_info()
    runComputer.get_mission_computer_load()
