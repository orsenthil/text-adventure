"""Web terminal bridge: runs main.py in a PTY per WebSocket connection."""

import asyncio
import fcntl
import json
import os
import pty
import shutil
import signal
import struct
import subprocess
import tempfile
import termios
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Client control messages (terminal resize) are prefixed with this byte so
# they can be told apart from ordinary keystroke data on the same channel.
RESIZE_PREFIX = "\x01"
DEFAULT_ROWS, DEFAULT_COLS = 24, 80

app = FastAPI()


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


def set_winsize(fd: int, rows: int, cols: int) -> None:
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def parse_resize(msg: str) -> tuple[int, int] | None:
    if not msg.startswith(RESIZE_PREFIX):
        return None
    try:
        data = json.loads(msg[1:])
        return int(data["rows"]), int(data["cols"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def spawn_game(cwd: str, rows: int, cols: int) -> tuple[subprocess.Popen, int]:
    master_fd, slave_fd = pty.openpty()
    set_winsize(slave_fd, rows, cols)
    proc = subprocess.Popen(
        ["python3", str(REPO_ROOT / "main.py")],
        cwd=cwd,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        start_new_session=True,
    )
    os.close(slave_fd)
    return proc, master_fd


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    rows, cols = DEFAULT_ROWS, DEFAULT_COLS
    try:
        first_msg = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
        rows, cols = parse_resize(first_msg) or (rows, cols)
    except asyncio.TimeoutError:
        pass

    session_dir = tempfile.mkdtemp(prefix="odyssey-")
    proc, fd = spawn_game(session_dir, rows, cols)

    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def on_readable():
        try:
            data = os.read(fd, 4096)
        except OSError:
            data = b""
        queue.put_nowait(data)
        if not data:
            loop.remove_reader(fd)

    loop.add_reader(fd, on_readable)

    async def pump_output():
        while True:
            data = await queue.get()
            if not data:
                break
            await websocket.send_bytes(data)

    pump_task = asyncio.create_task(pump_output())

    try:
        while True:
            msg = await websocket.receive_text()
            resize = parse_resize(msg)
            if resize is not None:
                set_winsize(fd, *resize)
                continue
            os.write(fd, msg.encode())
    except WebSocketDisconnect:
        pass
    finally:
        pump_task.cancel()
        try:
            loop.remove_reader(fd)
        except (ValueError, OSError):
            pass
        try:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            pass
        try:
            os.close(fd)
        except OSError:
            pass
        shutil.rmtree(session_dir, ignore_errors=True)
