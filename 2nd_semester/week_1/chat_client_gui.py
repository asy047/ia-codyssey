#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
import sys

HOST = '127.0.0.1'
PORT = 50007
ENCODING = 'utf-8'
BUFFER = 4096


class ChatClientGUI:
    """Tkinter 기반 채팅 클라이언트 GUI."""

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title('멀티스레드 채팅 클라이언트')
        self.master.protocol('WM_DELETE_WINDOW', self.on_close)

        self.sock = None  # type: socket.socket | None
        self.alive = False
        self.nick = ''
        self.rx_queue: queue.Queue[str] = queue.Queue()

        top = ttk.Frame(master, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text='서버').pack(side=tk.LEFT)
        self.ent_host = ttk.Entry(top, width=16)
        self.ent_host.insert(0, HOST)
        self.ent_host.pack(side=tk.LEFT, padx=(4, 8))

        ttk.Label(top, text='포트').pack(side=tk.LEFT)
        self.ent_port = ttk.Entry(top, width=6)
        self.ent_port.insert(0, str(PORT))
        self.ent_port.pack(side=tk.LEFT, padx=(4, 8))

        ttk.Label(top, text='닉네임').pack(side=tk.LEFT)
        self.ent_nick = ttk.Entry(top, width=14)
        self.ent_nick.pack(side=tk.LEFT, padx=(4, 8))

        self.btn_connect = ttk.Button(top, text='접속', command=self.connect)
        self.btn_connect.pack(side=tk.LEFT, padx=4)

        self.btn_disconnect = ttk.Button(top, text='종료', command=self.disconnect, state=tk.DISABLED)
        self.btn_disconnect.pack(side=tk.LEFT, padx=4)

        self.btn_who = ttk.Button(top, text='접속자(/who)', command=self.send_who, state=tk.DISABLED)
        self.btn_who.pack(side=tk.LEFT, padx=4)

        body = ttk.Frame(master, padding=(8, 0, 8, 0))
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        msg_frame = ttk.Frame(body)
        msg_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.txt_display = tk.Text(msg_frame, height=20, wrap='word', state=tk.DISABLED)
        self.txt_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(msg_frame, orient='vertical', command=self.txt_display.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.txt_display['yscrollcommand'] = scroll.set

        side = ttk.Frame(body)
        side.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 0))
        ttk.Label(side, text='접속자').pack(anchor='w')
        self.lst_users = tk.Listbox(side, height=20)
        self.lst_users.pack(fill=tk.Y)
        self.lst_users.bind('<Double-Button-1>', self._on_user_dblclick)

        bottom = ttk.Frame(master, padding=8)
        bottom.pack(side=tk.TOP, fill=tk.X)

        self.ent_input = ttk.Entry(bottom)
        self.ent_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ent_input.bind('<Return>', self.on_send)

        self.btn_send = ttk.Button(bottom, text='전송', command=self.on_send)
        self.btn_send.pack(side=tk.LEFT, padx=(8, 0))

        self.master.after(100, self._poll_rx_queue)

    # -------------------- 네트워크 --------------------

    def connect(self) -> None:
        host = self.ent_host.get().strip()
        try:
            port = int(self.ent_port.get().strip())
        except ValueError:
            messagebox.showwarning('안내', '포트는 정수여야 합니다.')
            return

        want_nick = self.ent_nick.get().strip()
        if not want_nick:
            messagebox.showwarning('안내', '닉네임을 입력하세요.')
            return

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))

            if self._recv_line(s) != 'NICK?':
                s.close()
                messagebox.showerror('오류', '서버 프로토콜 불일치')
                return

            self._send_line(s, want_nick)
            assigned = self._recv_line(s)
            if assigned is None:
                s.close()
                messagebox.showerror('오류', '닉네임 배정 응답 없음. 서버 상태를 확인하세요.')
                return
            if not assigned.startswith('NICK:'):
                s.close()
                messagebox.showerror('오류', f'닉네임 할당 실패(수신: {assigned!r})')
                return

            self.sock = s
            self.nick = assigned.split(':', 1)[1]
            self.alive = True

            self._append_text(f'[안내] 접속됨. 닉네임: {self.nick}')
            self._enable_connected_ui(True)

            t = threading.Thread(target=self._recv_loop, daemon=True)
            t.start()

        except Exception as ex:
            messagebox.showerror('연결 실패', f'서버에 접속할 수 없습니다.\n{ex!r}')

    def disconnect(self) -> None:
        if not self.alive:
            return
        try:
            self._send_line(self.sock, '/종료')
        except Exception:
            pass
        self._cleanup()
        self._append_text('[안내] 연결 종료')

    def _cleanup(self) -> None:
        self.alive = False
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = None
        self._enable_connected_ui(False)

    def _recv_loop(self) -> None:
        while self.alive and self.sock is not None:
            msg = self._recv_line(self.sock)
            if msg is None:
                self.rx_queue.put('[안내] 서버와의 연결이 종료되었습니다.')
                self.alive = False
                break
            if msg == 'BYE':
                self.alive = False
                break
            self.rx_queue.put(msg)

    # -------------------- UI 핸들러 --------------------

    def on_send(self, event=None) -> None:
        if not self.alive or self.sock is None:
            return
        text = self.ent_input.get().strip()
        if not text:
            return

        if text.startswith('@'):
            parts = text.split(' ', 1)
            if len(parts) == 2 and parts[0] != '@':
                target = parts[0][1:]
                body = parts[1]
                text = f'/w {target} {body}'

        self._send_line(self.sock, text)
        if text == '/종료':
            self.ent_input.delete(0, tk.END)
            self.ent_input.configure(state=tk.DISABLED)
            self.btn_send.configure(state=tk.DISABLED)
            return

        self.ent_input.delete(0, tk.END)

    def send_who(self) -> None:
        if self.alive and self.sock is not None:
            self._send_line(self.sock, '/who')

    def on_close(self) -> None:
        if self.alive:
            try:
                self._send_line(self.sock, '/종료')
            except Exception:
                pass
        self._cleanup()
        self.master.destroy()

    def _on_user_dblclick(self, event=None) -> None:
        sel = self.lst_users.curselection()
        if not sel:
            return
        name = self.lst_users.get(sel[0])
        cur = self.ent_input.get()
        prefix = f'@{name} '
        if not cur.startswith(prefix):
            self.ent_input.delete(0, tk.END)
            self.ent_input.insert(0, prefix)
        self.ent_input.focus_set()
        self.ent_input.icursor(tk.END)

    # -------------------- 수신 큐 → UI --------------------

    def _poll_rx_queue(self) -> None:
        try:
            while True:
                msg = self.rx_queue.get_nowait()
                self._append_text(msg)
                self._maybe_update_users(msg)
        except queue.Empty:
            pass
        self.master.after(100, self._poll_rx_queue)

    def _append_text(self, line: str) -> None:
        self.txt_display.configure(state=tk.NORMAL)
        self.txt_display.insert(tk.END, line + '\n')
        self.txt_display.see(tk.END)
        self.txt_display.configure(state=tk.DISABLED)

    def _maybe_update_users(self, msg: str) -> None:
        if msg.startswith('접속자:'):
            names_part = msg.split(':', 1)[1].strip()
            names = [n.strip() for n in names_part.split(',') if n.strip()]
            self.lst_users.delete(0, tk.END)
            for n in names:
                self.lst_users.insert(tk.END, n)

    # -------------------- 유틸 --------------------

    def _enable_connected_ui(self, connected: bool) -> None:
        self.btn_connect.configure(state=tk.DISABLED if connected else tk.NORMAL)
        self.btn_disconnect.configure(state=tk.NORMAL if connected else tk.DISABLED)
        self.btn_who.configure(state=tk.NORMAL if connected else tk.DISABLED)
        state_entries = tk.DISABLED if connected else tk.NORMAL
        self.ent_host.configure(state=state_entries)
        self.ent_port.configure(state=state_entries)
        self.ent_nick.configure(state=state_entries)
        self.ent_input.configure(state=tk.NORMAL if connected else tk.DISABLED)
        self.btn_send.configure(state=tk.NORMAL if connected else tk.DISABLED)
        if connected:
            self.ent_input.focus_set()

    @staticmethod
    def _send_line(sock: socket.socket | None, line: str) -> None:
        if sock is None:
            return
        data = (line + '\n').encode(ENCODING)
        sock.sendall(data)

    @staticmethod
    def _recv_line(sock: socket.socket) -> str | None:
        buf = []
        while True:
            try:
                chunk = sock.recv(BUFFER)
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


def main() -> None:
    host = HOST
    port = PORT
    nick = ''
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            pass
    if len(sys.argv) >= 4:
        nick = sys.argv[3]

    root = tk.Tk()
    app = ChatClientGUI(root)
    if host:
        app.ent_host.delete(0, tk.END)
        app.ent_host.insert(0, host)
    if port:
        app.ent_port.delete(0, tk.END)
        app.ent_port.insert(0, str(port))
    if nick:
        app.ent_nick.insert(0, nick)
    root.mainloop()


if __name__ == '__main__':
    main()
