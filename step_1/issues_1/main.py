def read_log_file(file_path):
    """로그 파일을 읽고 예외 처리를 수행한다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except FileNotFoundError:
        print('Error: 로그 파일을 찾을 수 없습니다.')
        return []
    except Exception as error:
        print(f'Error: {error}')
        return []

def parse_logs(log_lines):
    """로그 데이터를 파싱하여 리스트 형태로 반환한다."""
    return [
        {'timestamp': parts[0], 'event': parts[1], 'message': parts[2]}
        for line in log_lines
        if (parts := line.strip().split(',', 2)) and len(parts) == 3
    ]

def save_logs(log_entries, output_file, sort=False, reverse=False):
    """로그를 저장한다. 정렬 옵션을 포함한다."""
    if sort:
        log_entries = sorted(log_entries, key=lambda x: x['timestamp'], reverse=reverse)
    with open(output_file, 'w', encoding='utf-8') as file:
        for log in log_entries:
            file.write(f"{log['timestamp']}, {log['event']}, {log['message']}\n")

def extract_logs(log_entries, keyword, context=1):
    """특정 키워드(폭발)와 관련된 로그를 추출한다."""
    indices = [i for i, log in enumerate(log_entries) if keyword in log['message'].lower()]
    return [
        log_entries[i]
        for index in indices
        for i in range(max(0, index - context), min(len(log_entries), index + context + 1))
    ]

def generate_report(log_entries, report_file):
    """사고 원인 분석 결과를 Markdown 파일로 저장한다."""
    with open(report_file, 'w', encoding='utf-8') as file:
        file.write('# 사고 분석 보고서\n\n')
        file.write('## 1. 사고 개요\n')
        file.write('화성 기지 폭발 사고의 원인을 분석한다.\n\n')

        file.write('## 2. 로그 분석\n')
        file.write('| Timestamp | Event | Message |\n')
        file.write('|-----------|-------|---------|\n')

        for log in log_entries:
            if 'explosion' in log['message'].lower():
                file.write(f"| {log['timestamp']} | {log['event']} | {log['message']} |\n")

        file.write('\n## 3. 폭발 전후 로그\n')
        file.write('| Timestamp | Event | Message |\n')
        file.write('|-----------|-------|---------|\n')

        explosion_indices = [i for i, log in enumerate(log_entries) if 'explosion' in log['message'].lower()]
        for index in explosion_indices:
            start = max(0, index - 1)
            end = min(len(log_entries), index + 2)
            for log in log_entries[start:end]:
                file.write(f"| {log['timestamp']} | {log['event']} | {log['message']} |\n")

        file.write('\n## 4. 사고 원인 정리\n')
        file.write('로그 분석 결과, **산소 탱크의 불안정한 상태(Oxygen tank unstable)** 이후 **산소 탱크 폭발(Oxygen tank explosion)** 이 발생한 것으로 확인됨.\n\n')

def main():
    """설치가 잘 되었는지 확인 하기 위해 출력"""
    print("Hello Mars")

    """로그 분석 실행"""
    log_file = 'mission_computer_main.log'
    sorted_log_file = 'sorted_logs.txt'
    critical_log_file = 'critical_logs.txt'
    report_file = 'log_analysis.md'

    logs = read_log_file(log_file)
    if not logs:
        return

    log_entries = parse_logs(logs)
    save_logs(log_entries, sorted_log_file, sort=True, reverse=True)
    critical_logs = extract_logs(log_entries, 'explosion')
    save_logs(critical_logs, critical_log_file)
    generate_report(log_entries, report_file)
    print("로그 분석 완료. 보고서가 작성되었습니다.")

if __name__ == '__main__':
    main()
