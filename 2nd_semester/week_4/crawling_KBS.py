import time
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


NAVER_LOGIN_URL = 'https://nid.naver.com/nidlogin.login'
NAVER_MAIL_URL = 'https://mail.naver.com/'


class NaverCrawler:
    """네이버 로그인 및 메일 제목 크롤러 클래스."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def open_login_page(self):
        """네이버 로그인 페이지 접속."""
        self.driver.get(NAVER_LOGIN_URL)

    def login(self, user_id, user_pw):
        """네이버 계정으로 로그인."""
        try:
            id_input = self.wait.until(
                EC.presence_of_element_located((By.ID, 'id'))
            )
            pw_input = self.wait.until(
                EC.presence_of_element_located((By.ID, 'pw'))
            )
        except TimeoutException:
            raise RuntimeError('로그인 입력 요소(id, pw)를 찾지 못했습니다.')

        id_input.clear()
        id_input.send_keys(user_id)

        pw_input.clear()
        pw_input.send_keys(user_pw)
        pw_input.send_keys(Keys.ENTER)

        # 로그인 처리 시간 대기
        time.sleep(2)

        # 로그인 성공 여부를 단순히 도메인 기준으로 확인 (필요하면 조건 수정)
        if 'nid.naver.com' in self.driver.current_url:
            raise RuntimeError('로그인에 실패한 것으로 보입니다. '
                               '아이디/비밀번호 또는 추가 인증을 확인하세요.')

    def move_to_mail(self):
        """네이버 메일 페이지로 이동."""
        self.driver.get(NAVER_MAIL_URL)
        try:
            # 메일 리스트가 로딩될 때까지 대기
            self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'div.mail_list, div.mailList')
                )
            )
        except TimeoutException:
            raise RuntimeError('메일 리스트 영역을 찾지 못했습니다.')

    def collect_mail_titles(self, limit=20):
        """받은 메일 제목들을 최대 limit개까지 수집해 리스트로 반환."""
        # 네이버 메일의 HTML 구조는 수시로 바뀔 수 있으므로
        # 아래 CSS 선택자는 상황에 맞게 수정해야 할 수 있다.
        possible_selectors = [
            # 예: 새로운 UI 구조
            'div.mailList div.subject strong',
            'div.mailList div.subject span',
            # 예: 예전 UI 구조
            'div.mail_list div.subject strong',
            'div.mail_list div.subject span',
        ]

        mail_titles = []

        for selector in possible_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                text = element.text.strip()
                if text:
                    mail_titles.append(text)

            if mail_titles:
                break

        if not mail_titles:
            print('경고: 메일 제목을 찾지 못했습니다. CSS 선택자를 확인하세요.')

        if limit is not None:
            mail_titles = mail_titles[:limit]

        return mail_titles

    def close(self):
        """드라이버 종료."""
        self.driver.quit()


def create_webdriver():
    """크롬 웹드라이버 생성."""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # 필요하면 헤드리스 모드 사용
    # options.add_argument('--headless')

    # 크롬 드라이버가 PATH에 잡혀 있으면 Service 인자 없이도 동작
    driver = webdriver.Chrome(options=options)
    return driver


def read_credentials():
    """아이디/비밀번호를 콘솔에서 안전하게 입력받기."""
    user_id = input('네이버 아이디를 입력하세요: ').strip()
    user_pw = getpass('네이버 비밀번호를 입력하세요(화면에 표시되지 않습니다): ')
    return user_id, user_pw


def print_titles(titles):
    """메일 제목 리스트를 화면에 출력."""
    print('\n==============================')
    print('   네이버 메일 제목 목록')
    print('==============================')

    if not titles:
        print('표시할 메일 제목이 없습니다.')
        return

    for index, title in enumerate(titles, start=1):
        print(f'{index:02d}. {title}')


def main():
    """프로그램 진입점."""
    user_id, user_pw = read_credentials()
    driver = create_webdriver()
    crawler = NaverCrawler(driver)

    try:
        crawler.open_login_page()
        crawler.login(user_id, user_pw)
        crawler.move_to_mail()

        mail_titles = crawler.collect_mail_titles(limit=50)
        print_titles(mail_titles)

        # 리스트 객체 그대로도 필요하다면 여기서 활용
        # 예: 다른 모듈에서 사용할 수 있도록 반환 등
    finally:
        # 예외 여부와 관계없이 브라우저 닫기
        crawler.close()


if __name__ == '__main__':
    main()
