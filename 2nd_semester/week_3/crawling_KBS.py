import requests
from bs4 import BeautifulSoup


def get_kbs_headlines():
    url = 'https://news.kbs.co.kr/news/pc/main/main.html'
    response = requests.get(url)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print('페이지 요청 실패:', response.status_code)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select('p.title')

    headlines = []
    for idx, item in enumerate(items):
        # 마지막 인덱스는 건너뛰기
        if idx == len(items) - 1:
            continue

        title = item.get_text(strip=True)
        if title:
            headlines.append(title)

    return headlines


def main():
    headlines = get_kbs_headlines()

    if not headlines:
        print('헤드라인 뉴스를 가져오지 못했습니다.')
    else:
        print('KBS 주요 뉴스:')
        for idx, title in enumerate(headlines, start=1):
            print(f'{idx}. {title}')


if __name__ == '__main__':
    main()
