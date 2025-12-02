import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


CSV_FILE_NAME = 'mail_target_list.csv'


def read_mail_targets(csv_file_name):
    """CSV 파일에서 (이름, 이메일) 목록을 읽어서 리턴한다."""
    targets = []

    with open(csv_file_name, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        is_first_row = True

        for row in reader:
            # 첫 줄은 헤더: '이름, 이메일'
            if is_first_row:
                is_first_row = False
                continue

            if len(row) < 2:
                continue

            name = row[0].strip()
            email = row[1].strip()

            if not name or not email:
                continue

            targets.append((name, email))

    return targets


def get_smtp_config(service_name):
    """메일 서비스 이름에 따른 SMTP 서버 설정을 리턴한다."""
    service = service_name.lower()

    if service == 'gmail':
        return 'smtp.gmail.com', 587
    if service == 'naver':
        return 'smtp.naver.com', 587

    raise ValueError('지원하지 않는 메일 서비스입니다. gmail 또는 naver 를 사용하십시오.')


def build_html_body(sender_name, receiver_name):
    """수신자 이름을 포함한 HTML 본문을 생성한다."""
    html_body = f"""
    <html>
      <body>
        <p>Dear {receiver_name},</p>

        <p>
          Dr. Han!!, we received your message, but we couldn't understand the situation,
          so we all froze, and we don't even know how much we cried after hugging each other.
          We are so grateful that you are alive, and we will do our best too.
          Just in case your condition is not good, we are sending this message in English.
        </p>

        <p>
          Across the silence of Mars, your message reached us and gave us hope.<br/>
          We are doing everything we can to support you from Earth.
        </p>

        <p>
          Best regards,<br/>
          {sender_name}
        </p>
      </body>
    </html>
    """
    return html_body


def create_html_message(sender_email, sender_name, receiver_email, receiver_name, subject):
    """HTML 형식 메일 객체(MIME)를 생성한다."""
    message = MIMEMultipart('alternative')
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    html_body = build_html_body(sender_name, receiver_name)

    html_part = MIMEText(html_body, 'html', 'utf-8')
    message.attach(html_part)

    return message


def send_mail_one_by_one(
    smtp_server,
    smtp_port,
    sender_email,
    sender_password,
    sender_name,
    targets,
    subject
):
    """
    수신자마다 메일 한 통씩 개별 발송한다.
    - 장점: 수신자 이름을 본문에 넣는 등 개인화가 가능하다.
    - 장점: 다른 사람의 이메일 주소가 공개되지 않는다.
    """
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)

        for name, email in targets:
            message = create_html_message(
                sender_email=sender_email,
                sender_name=sender_name,
                receiver_email=email,
                receiver_name=name,
                subject=subject
            )

            server.sendmail(
                from_addr=sender_email,
                to_addrs=[email],
                msg=message.as_string()
            )
            print(f'개별 발송 완료: {name} <{email}>')


def send_mail_in_bulk(
    smtp_server,
    smtp_port,
    sender_email,
    sender_password,
    sender_name,
    targets,
    subject
):
    """
    한 번에 여러 수신자에게 동일한 메일을 발송한다.
    - To 헤더에 여러 이메일을 나열하는 방식.
    - 이 예시는 과제 요구사항 중
      "받는 사람에 여러명을 열거하는 방법"을 위한 참고용 함수이다.
    """
    all_emails = [email for _, email in targets]

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)

        # 수신자 이름은 첫 번째 사람 기준으로만 사용 (단순 예시)
        first_name = targets[0][0] if targets else ''
        message = MIMEMultipart('alternative')
        message['From'] = sender_email
        message['To'] = ', '.join(all_emails)
        message['Subject'] = subject

        html_body = build_html_body(sender_name, first_name)
        html_part = MIMEText(html_body, 'html', 'utf-8')
        message.attach(html_part)

        server.sendmail(
            from_addr=sender_email,
            to_addrs=all_emails,
            msg=message.as_string()
        )
        print('일괄 발송 완료 (To 헤더에 여러 명 열거)')


def main():
    print('====== HTML 메일 발송 프로그램 (문제2 감동의 메시지) ======')

    service_name = input('메일 서비스(gmail/naver)를 입력하세요: ').strip()
    smtp_server, smtp_port = get_smtp_config(service_name)

    sender_email = input('발신자 이메일 주소를 입력하세요: ').strip()
    sender_password = input('발신자 이메일 비밀번호(또는 앱 비밀번호)를 입력하세요: ').strip()
    sender_name = input('발신자 이름(예: Dr. Han)을 입력하세요: ').strip()

    subject = 'Message from Mars - Dr. Han'

    targets = read_mail_targets(CSV_FILE_NAME)

    if not targets:
        print('메일 대상 목록이 비어 있습니다. CSV 파일을 확인하십시오.')
        return

    print(f'총 {len(targets)}명에게 메일을 발송합니다.')

    # 과제 요구사항:
    # 1) 여러 명을 한 번에 나열해서 보내는 방법
    # 2) 한 명씩 반복해서 보내는 방법
    #
    # 둘 다 구현했으며, 실제 발송에서는
    # 보안과 개인 정보 보호, 개인화 측면에서
    # "한 번에 한 명씩 보내는 방식(send_mail_one_by_one)"을 선택한다.

    send_mode = input('발송 방식 선택 (1: 한 명씩, 2: 여러 명 한 번에) 를 입력하세요: ').strip()

    if send_mode == '2':
        # 여러 명을 한 번에 보내는 방식
        send_mail_in_bulk(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            sender_email=sender_email,
            sender_password=sender_password,
            sender_name=sender_name,
            targets=targets,
            subject=subject
        )
    else:
        # 기본값: 한 명씩 개별 발송
        send_mail_one_by_one(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            sender_email=sender_email,
            sender_password=sender_password,
            sender_name=sender_name,
            targets=targets,
            subject=subject
        )

    print('모든 메일 발송 작업이 종료되었습니다.')


if __name__ == '__main__':
    main()
