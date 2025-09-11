#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import sys

HOST = '127.0.0.1'   # 서버 주소
PORT = 50007
ENCODING = 'utf-8'
BUFFER = 4096


class ChatClient:
    """간단한 콘솔 채팅 클라이언트."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nick = ''
        self.alive = True

    def start(self) -> None:
        self.sock.connect((self.host, self.port))

        # 닉네임 협상
        prompt = self._recv_line()
        if prompt != 'NICK?':
            print('[오류] 서버 프로토콜 불일치')
            self.sock.close()
            return

        self.nick = self._input_nick()
        self._send_line(self.nick)

        assigned = self._recv_line()
        if not assigned.startswith('NICK:'):
            print('[오류] 닉네임 할당 실패')
            self.sock.close()
            return

        self.nick = assigned.split(':', 1)[1]
        print(f'[안내] 접속 닉네임: {self.nick}')
        print('[안내] 종료하려면 /종료 를 입력하세요. 귓속말은 "/w 대상닉 메시지".')

        # 수신 스레드
        t = threading.Thread(target=self._recv_loop, daemon=True)
        t.start()

        # 송신 루프 (메인 스레드)
        try:
            while self.alive:
                try:
                    line = input()
                except EOFError:
                    line = '/종료'
                if not line:
                    continue
                self._send_line(line)
                if line.strip() == '/종료':
                    break
        finally:
            self._cleanup()

    def _recv_loop(self) -> None:
        """서버 메시지 수신 및 출력."""
        while self.alive:
            msg = self._recv_line()
            if msg is None:
                print('[안내] 서버와의 연결이 종료되었습니다.')
                self.alive = False
                break
            if msg == 'BYE':
                self.alive = False
                break
            print(msg)

    def _send_line(self, line: str) -> None:
        data = (line + '\n').encode(ENCODING)
        try:
            self.sock.sendall(data)
        except Exception:
            self.alive = False

    def _recv_line(self) -> str:
        """개행 기준으로 한 줄 수신. 연결 종료 시 None."""
        buf = []
        while True:
            try:
                chunk = self.sock.recv(BUFFER)
            except Exception:
                return None
            if not chunk:
                return None
            try:
                text = chunk.decode(ENCODING)
            except UnicodeDecodeError:
                text = chunk.decode(ENCODING, errors='ignore')
            buf.append(text)
            if '\n' in text:
                break
        return ''.join(buf).split('\n', 1)[0]

    @staticmethod
    def _input_nick() -> str:
        nick = ''
        while not nick:
            nick = input('닉네임을 입력하세요: ').strip()
        return nick

    def _cleanup(self) -> None:
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass


def main() -> None:
    host = HOST
    port = PORT
    # 인자 제공 시 서버 주소/포트 지정 가능
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            pass
    client = ChatClient(host, port)
    client.start()


if __name__ == '__main__':
    main()
