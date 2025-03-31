def read_csv(file_path):
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            header_line = file.readline().strip()
            headers = header_line.split(',')

            for line in file:
                values = line.strip().split(',')
                row = {}
                for i in range(len(headers)):
                    key = headers[i]
                    value = values[i]
                    if key == 'Flammability':
                        row[key] = float(value)
                    else:
                        row[key] = value
                data.append(row)

            print('[1] CSV 파일에서 읽은 내용:')
            for item in data:
                print(item)

    except Exception as e:
        print('CSV 파일 읽기 오류:', e)

    return data


def sort_by_flammability(data):
    return sorted(data, key=lambda x: x['Flammability'], reverse=True)


def filter_dangerous_materials(data):
    result = []
    for item in data:
        if item['Flammability'] >= 0.7:
            result.append(item)
    return result


def save_to_csv(file_path, data, headers):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(','.join(headers) + '\n')
            for item in data:
                values = []
                for key in headers:
                    values.append(str(item[key]))
                line = ','.join(values)
                file.write(line + '\n')
    except Exception as e:
        print('CSV 저장 오류:', e)


def save_to_binary(file_path, data):
    try:
        with open(file_path, 'wb') as file:
            for item in data:
                line = ','.join(str(item[key]) for key in item)
                file.write((line + '\n').encode('utf-8'))
    except Exception as e:
        print('이진 파일 저장 오류:', e)


def read_binary_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            print('\n[5] 저장된 이진 파일 내용:')
            content = file.read().decode('utf-8')
            print(content)
    except Exception as e:
        print('이진 파일 읽기 오류:', e)


def main():
    csv_file = 'Mars_Base_Inventory_List.csv'
    danger_csv_file = 'Mars_Base_Inventory_danger.csv'
    binary_file = 'Mars_Base_Inventory_List.bin'

    # 1~2단계: CSV 읽기 + 리스트 변환 + 출력
    inventory = read_csv(csv_file)

    # 3단계: 인화성 높은 순 정렬
    sorted_inventory = sort_by_flammability(inventory)

    # 4단계: 인화성 ≥ 0.7 항목만 필터링하여 출력
    danger_list = filter_dangerous_materials(sorted_inventory)

    print('\n[3] 인화성 0.7 이상 위험 물질 목록:')
    for item in danger_list:
        print(item)

    # 5단계: 위험 물질을 CSV 파일로 저장
    if len(danger_list) > 0:
        save_to_csv(danger_csv_file, danger_list, list(danger_list[0].keys()))

    # 보너스: 이진 파일로 저장 및 출력
    save_to_binary(binary_file, sorted_inventory)
    read_binary_file(binary_file)


if __name__ == '__main__':
    main()
