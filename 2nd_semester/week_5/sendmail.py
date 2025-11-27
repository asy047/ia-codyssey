import os
import mimetypes
from getpass import getpass
from email.message import EmailMessage
import smtplib


SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587  # TLS 기본 포트


class MailSender:
    """Gmail SMTP를 이용해 메일을 전송하는 클래스."""

    def __init__(self, smtp_server, smtp_port, user_email, user_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.user_email = user_email
        self.user_password = user_password

    def create_message(self, to_email, subject, body, attachment_path=None):
        """메일 메시지(텍스트 + 첨부 파일)를 생성한다."""
        message = EmailMessage()
        message['From'] = self.user_email
        message['To'] = to_email
        message['Subject'] = subject
        message.set_content(body)

        if attachment_path:
            self._add_attachment(message, attachment_path)

        return message

    def _add_attachment(self, message, attachment_path):
        """첨부 파일을 메시지에 추가한다."""
        if not os.path.isfile(attachment_path):
            print(f'경고: 첨부 파일을 찾을 수 없습니다: {attachment_path}')
            return

        file_name = os.path.basename(attachment_path)
        ctype, encoding = mimetypes.guess_type(attachment_path)

        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'

        main_type, sub_type = ctype.split('/', 1)

        with open(attachment_path, 'rb') as file:
            file_data = file.read()

        message.add_attachment(
            file_data,
            maintype=main_type,
            subtype=sub_type,
            filename=file_name,
        )

    def send_mail(self, message):
        """SMTP 서버에 접속해 메일을 전송한다."""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.user_email, self.user_password)
                server.send_message(message)
        except smtplib.SMTPAuthenticationError as error:
            print('인증 실패: 아이디/비밀번호 또는 앱 비밀번호를 확인하세요.')
            print(f'상세 코드: {error.smtp_code}, 메시지: {error.smtp_error}')
        except smtplib.SMTPConnectError as error:
            print('SMTP 서버에 연결할 수 없습니다.')
            print(f'상세 코드: {error.smtp_code}, 메시지: {error.smtp_error}')
        except smtplib.SMTPRecipientsRefused as error:
            print('수신자가 메일을 거부했습니다.')
            print(f'상세 정보: {error.recipients}')
        except smtplib.SMTPException as error:
            print('SMTP 통신 중 알 수 없는 오류가 발생했습니다.')
            print(f'상세 정보: {error}')
        except OSError as error:
            print('네트워크 또는 파일 시스템 오류가 발생했습니다.')
            print(f'상세 정보: {error}')
        else:
            print('메일 전송을 완료했습니다.')


def read_user_input():
    """콘솔로부터 메일 전송에 필요한 정보를 입력받는다."""
    print('=== Gmail SMTP 메일 전송 설정 ===')
    user_email = input('보내는 사람 Gmail 주소를 입력하세요: ').strip()
    user_password = getpass('보내는 사람 Gmail 비밀번호 또는 앱 비밀번호를 입력하세요: ')

    print('\n=== 메일 내용 설정 ===')
    to_email = input('받는 사람 이메일 주소를 입력하세요: ').strip()
    subject = input('메일 제목을 입력하세요: ').strip()

    print('메일 본문 내용을 입력하세요. 입력을 종료하려면 빈 줄에서 Enter를 두 번 누르세요.')
    body_lines = []
    while True:
        line = input()
        if line == '':
            break
        body_lines.append(line)
    body = '\n'.join(body_lines) if body_lines else '내용 없음'

    attach_answer = input('첨부 파일을 추가하시겠습니까? (y/N): ').strip().lower()
    attachment_path = None

    if attach_answer == 'y':
        attachment_path = input('첨부 파일의 경로를 입력하세요: ').strip()
        if attachment_path == '':
            attachment_path = None

    return user_email, user_password, to_email, subject, body, attachment_path


def main():
    """프로그램 진입점 함수."""
    (
        user_email,
        user_password,
        to_email,
        subject,
        body,
        attachment_path,
    ) = read_user_input()

    mail_sender = MailSender(
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        user_email=user_email,
        user_password=user_password,
    )

    message = mail_sender.create_message(
        to_email=to_email,
        subject=subject,
        body=body,
        attachment_path=attachment_path,
    )

    mail_sender.send_mail(message)


if __name__ == '__main__':
    main()
