#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
from typing import Dict, Tuple

HOST = '0.0.0.0'
PORT = 50007
BACKLOG = 50
ENCODING = 'utf-8'
BUFFER = 4096


class ChatServer:
    """멀티스레드 채팅 서버."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: Dict[socket.socket, str] = {}
        self.lock = threading.Lock()

    def start(self) -> None:
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(BACKLOG)
        print(f'[INFO] Chat server listening on {self.host}:{self.port}')

        try:
            while True:
                conn, addr = self.server_sock.accept()
                threading.Thread(
                    target=self._handle_new_connection,
                    args=(conn, addr),
                    daemon=True
                ).start()
        finally:
            self.server_sock.close()

    def _handle_new_connection(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        try:
            self._send_line(conn, 'NICK?')
            want = self._recv_line(conn)
            if not want:
                conn.close()
                return

            nick = self._ensure_unique_nick(want.strip())
            with self.lock:
                self.clients[conn] = nick

            self._send_line(conn, f'NICK:{nick}')
            self._broadcast_system(f'{nick}님이 입장하셨습니다.')

            self._client_loop(conn, nick)

        except Exception:
            self._safe_disconnect(conn)

    def _client_loop(self, conn: socket.socket, nick: str) -> None:
        try:
            while True:
                msg = self._recv_line(conn)
                if msg is None:
                    break

                text = msg.strip()
                if not text:
                    continue

                if text == '/종료':
                    self._send_line(conn, 'BYE')
                    break

                if text == '/who':
                    with self.lock:
                        names = ', '.join(sorted(self.clients.values()))
                    self._send_to_nick(nick, f'접속자: {names}')
                    continue

                if text.startswith('/w '):
                    self._handle_whisper(nick, text)
                    continue

                self._broadcast_chat(nick, text)
        finally:
            self._safe_disconnect(conn)

    def _handle_whisper(self, sender: str, raw: str) -> None:
        parts = raw.split(' ', 2)
        if len(parts) < 3:
            self._send_to_nick(sender, '[시스템] 형식: /w 대상닉 메시지')
            return

        _, target, body = parts
        target_conn = self._find_conn_by_nick(target)
        if target_conn is None:
            self._send_to_nick(sender, f'[시스템] 대상 \'{target}\'을(를) 찾을 수 없습니다.')
            return

        self._send_to_conn(target_conn, f'(귓속말){sender}> {body}')
        self._send_to_nick(sender, f'(귓속말->{target}){sender}> {body}')

    def _broadcast_chat(self, nick: str, text: str) -> None:
        self._broadcast_line(f'{nick}> {text}')

    def _broadcast_system(self, text: str) -> None:
        self._broadcast_line(f'[시스템] {text}')

    def _broadcast_line(self, line: str) -> None:
        with self.lock:
            targets = list(self.clients.keys())
        for c in targets:
            self._send_to_conn(c, line)

    def _send_to_nick(self, nick: str, line: str) -> None:
        c = self._find_conn_by_nick(nick)
        if c is not None:
            self._send_to_conn(c, line)

    def _find_conn_by_nick(self, nick: str):
        with self.lock:
            for c, n in self.clients.items():
                if n == nick:
                    return c
        return None

    def _ensure_unique_nick(self, want: str) -> str:
        base = want if want else 'guest'
        cand = base
        i = 2
        with self.lock:
            used = set(self.clients.values())
            while cand in used:
                cand = f'{base}_{i}'
                i += 1
        return cand

    @staticmethod
    def _send_line(conn: socket.socket, line: str) -> None:
        data = (line + '\n').encode(ENCODING)
        conn.sendall(data)

    @staticmethod
    def _recv_line(conn: socket.socket) -> str:
        buf = []
        while True:
            chunk = conn.recv(BUFFER)
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

    def _send_to_conn(self, conn: socket.socket, line: str) -> None:
        try:
            self._send_line(conn, line)
        except Exception:
            self._safe_disconnect(conn)

    def _safe_disconnect(self, conn: socket.socket) -> None:
        nick = None
        with self.lock:
            if conn in self.clients:
                nick = self.clients.pop(conn)
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        if nick:
            self._broadcast_system(f'{nick}님이 퇴장하셨습니다.')


def main() -> None:
    server = ChatServer(HOST, PORT)
    server.start()


if __name__ == '__main__':
    main()
