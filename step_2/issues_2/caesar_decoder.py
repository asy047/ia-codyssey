def load_dictionary(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print('Error: dictionary.txt 파일이 없습니다.')
        return []
    except Exception as e:
        print(f'Error: {e}')
        return []

def caesar_cipher_decode(target_text, dictionary):
    for shift in range(1, 26):
        decoded_text = ''
        for char in target_text:
            if 'a' <= char <= 'z':
                decoded_text += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                decoded_text += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                decoded_text += char
        print(f'[{shift}] {decoded_text}')

        # 사전 키워드 탐색
        for keyword in dictionary:
            if keyword in decoded_text.lower():
                print(f'\n사전 단어 "{keyword}" 발견! 해독 성공 (shift={shift})')
                try:
                    with open('result.txt', 'w') as f:
                        f.write(decoded_text)
                    print('결과가 result.txt에 저장되었습니다.')
                except Exception as e:
                    print(f'Error: {e}')
                return  # 반복 멈춤
    print('사전 단어와 일치하는 해독 결과가 없습니다.')

def main():
    # dictionary.txt 로드
    dictionary = load_dictionary('dictionary.txt')

    # password.txt 읽기
    try:
        with open('password.txt', 'r') as file:
            target_text = file.read().strip()
    except FileNotFoundError:
        print('Error: password.txt 파일이 없습니다.')
        return
    except Exception as e:
        print(f'Error: {e}')
        return

    caesar_cipher_decode(target_text, dictionary)

if __name__ == '__main__':
    main()
