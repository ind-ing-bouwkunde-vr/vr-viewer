# -*- coding: utf-8 -*-
"""
VR-viewer starter
-----------------
Kies een map met je VR-pagina's (HTML) en klik op Start.
De app start zelf een lokale webserver en een ngrok-tunnel en toont
de https-link en een QR-code die je met de Meta Quest scant.

Werkt als gewone app (GitHub-download) en als Microsoft Store-app (MSIX).
Gebruikt enkel de standaardbibliotheek van Python.
"""

import base64
import csv
import email.utils
import gzip
import hashlib
import html as html_lib
import json
import random
import socket
import struct
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
import zipfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

APP_NAME = "VR-viewer starter"
APP_VERSION = "3.2.1"

# Alles wat de app bewaart, staat in de gebruikersmap (AppData\Local).
# Een Store-app (MSIX) mag niet in zijn eigen installatiemap schrijven.
DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "VRViewerStarter")
SETTINGS_FILE = os.path.join(DATA_DIR, "instellingen.json")
NGROK_CONFIG = os.path.join(DATA_DIR, "ngrok.yml")

NGROK_ZIP_URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
NGROK_DOWNLOAD_PAGE = "https://ngrok.com/download"
NGROK_TOKEN_PAGE = "https://dashboard.ngrok.com/get-started/your-authtoken"
NGROK_SIGNUP_PAGE = "https://dashboard.ngrok.com/signup"
NGROK_DOMAIN_PAGE = "https://dashboard.ngrok.com/domains"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
QR_SMALL = 150  # px, QR-code in het hoofdvenster

HTML_EXT = (".html", ".htm")
MODEL_EXT = (".glb", ".gltf")
MAX_DEPTH = 3  # hoe diep de app in submappen zoekt

# kleuren
BG = "#eef0f3"
CARD = "#ffffff"
INK = "#1c2330"
MUTED = "#5b6475"
LINE = "#dde1e7"
YELLOW = "#f2b705"
YELLOW_SOFT = "#fff4cc"
GREEN = "#2f7d4f"
RED = "#b3261e"

LOGO_PNG = (
    "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"
)


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_dir():
    # PyInstaller zet meegeleverde bestanden (zoals 'voorbeeld') in _MEIPASS
    return getattr(sys, "_MEIPASS", app_dir())


def example_dir():
    for base in (resource_dir(), app_dir()):
        p = os.path.join(base, "voorbeeld")
        if os.path.isdir(p):
            return p
    return None


def load_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(data):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def scan_folder(folder):
    """Geeft (html-bestanden, 3D-modellen) terug als relatieve paden, ook uit submappen."""
    html, models = [], []
    folder = os.path.abspath(folder)
    base_depth = folder.rstrip(os.sep).count(os.sep)
    for root, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if not d.startswith((".", "_")) and d.lower() != "node_modules")
        if root.rstrip(os.sep).count(os.sep) - base_depth >= MAX_DEPTH:
            dirs[:] = []
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(root, f), folder).replace(os.sep, "/")
            low = f.lower()
            if low.endswith(HTML_EXT):
                html.append(rel)
            elif low.endswith(MODEL_EXT):
                models.append(rel)
    html.sort(key=lambda p: (p.count("/"), p.lower()))
    return html, models


# ======================================================================== QR-CODE (zonder extra bibliotheken)
# Gebaseerd op het algoritme van Project Nayuki (MIT). Bytemodus, foutcorrectie M of L, versie 1-40.

_QR_ECC = {  # codewoorden foutcorrectie per blok, per versie (index 0 ongebruikt)
    "L": (-1, 7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28, 28, 28, 28, 30, 30, 26, 28,
          30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
    "M": (-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28, 28, 28,
          28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28),
}
_QR_BLOCKS = {
    "L": (-1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 4, 6, 6, 6, 6, 7, 8, 8, 9, 9, 10, 12, 12, 12, 13, 14, 15, 16, 17,
          18, 19, 19, 20, 21, 22, 24, 25),
    "M": (-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29,
          31, 33, 35, 37, 38, 40, 43, 45, 47, 49),
}
_QR_FORMAT = {"L": 1, "M": 0}


def _gf_mul(x, y):
    z = 0
    for i in range(7, -1, -1):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z


def _rs_divisor(degree):
    res = [0] * (degree - 1) + [1]
    root = 1
    for _ in range(degree):
        for j in range(degree):
            res[j] = _gf_mul(res[j], root)
            if j + 1 < degree:
                res[j] ^= res[j + 1]
        root = _gf_mul(root, 0x02)
    return res


def _rs_remainder(data, divisor):
    res = [0] * len(divisor)
    for b in data:
        factor = b ^ res.pop(0)
        res.append(0)
        for i, coef in enumerate(divisor):
            res[i] ^= _gf_mul(coef, factor)
    return res


def _raw_modules(ver):
    n = (16 * ver + 128) * ver + 64
    if ver >= 2:
        na = ver // 7 + 2
        n -= (25 * na - 10) * na - 55
        if ver >= 7:
            n -= 36
    return n


def _data_codewords(ver, ecl):
    return _raw_modules(ver) // 8 - _QR_ECC[ecl][ver] * _QR_BLOCKS[ecl][ver]


def qr_matrix(text, ecl="M"):
    """Geeft een vierkante lijst van lijsten met True (zwart) / False (wit) terug, zonder witte rand."""
    data = text.encode("utf-8")
    for ver in range(1, 41):
        cc = 8 if ver <= 9 else 16
        if 4 + cc + 8 * len(data) <= _data_codewords(ver, ecl) * 8:
            break
    else:
        raise ValueError("Tekst te lang voor een QR-code")
    bits = []

    def put(val, n):
        bits.extend((val >> i) & 1 for i in range(n - 1, -1, -1))

    put(4, 4)
    put(len(data), cc)
    for b in data:
        put(b, 8)
    cap = _data_codewords(ver, ecl) * 8
    put(0, min(4, cap - len(bits)))
    put(0, (-len(bits)) % 8)
    pad = 0xEC
    while len(bits) < cap:
        put(pad, 8)
        pad ^= 0xEC ^ 0x11
    words = [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]

    # foutcorrectie en verweven
    nblocks, ecclen = _QR_BLOCKS[ecl][ver], _QR_ECC[ecl][ver]
    raw = _raw_modules(ver) // 8
    nshort = nblocks - raw % nblocks
    shortlen = raw // nblocks
    div = _rs_divisor(ecclen)
    blocks, k = [], 0
    for i in range(nblocks):
        dat = words[k:k + shortlen - ecclen + (0 if i < nshort else 1)]
        k += len(dat)
        ecc = _rs_remainder(dat, div)
        if i < nshort:
            dat = dat + [0]
        blocks.append(dat + ecc)
    final = []
    for i in range(len(blocks[0])):
        for j, blk in enumerate(blocks):
            if i != shortlen - ecclen or j >= nshort:
                final.append(blk[i])

    size = ver * 4 + 17
    mod = [[False] * size for _ in range(size)]
    fun = [[False] * size for _ in range(size)]

    def setf(x, y, dark):
        mod[y][x] = dark
        fun[y][x] = True

    for i in range(size):
        setf(6, i, i % 2 == 0)
        setf(i, 6, i % 2 == 0)
    for cx, cy in ((3, 3), (size - 4, 3), (3, size - 4)):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = cx + dx, cy + dy
                if 0 <= x < size and 0 <= y < size:
                    setf(x, y, max(abs(dx), abs(dy)) not in (2, 4))
    if ver > 1:
        na = ver // 7 + 2
        step = (ver * 8 + na * 3 + 5) // (na * 4 - 4) * 2
        pos = [6] + sorted(size - 7 - i * step for i in range(na - 1))
        last = len(pos) - 1
        for i in range(len(pos)):
            for j in range(len(pos)):
                if (i == 0 and j == 0) or (i == 0 and j == last) or (i == last and j == 0):
                    continue
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        setf(pos[i] + dx, pos[j] + dy, max(abs(dx), abs(dy)) != 1)

    def draw_format(mask):
        d = _QR_FORMAT[ecl] << 3 | mask
        rem = d
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        b = (d << 10 | rem) ^ 0x5412
        bit = lambda i: (b >> i) & 1 == 1  # noqa: E731
        for i in range(6):
            setf(8, i, bit(i))
        setf(8, 7, bit(6))
        setf(8, 8, bit(7))
        setf(7, 8, bit(8))
        for i in range(9, 15):
            setf(14 - i, 8, bit(i))
        for i in range(8):
            setf(size - 1 - i, 8, bit(i))
        for i in range(8, 15):
            setf(8, size - 15 + i, bit(i))
        setf(8, size - 8, True)

    draw_format(0)
    if ver >= 7:
        rem = ver
        for _ in range(12):
            rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
        b = ver << 12 | rem
        for i in range(18):
            dark = (b >> i) & 1 == 1
            a, c = size - 11 + i % 3, i // 3
            setf(a, c, dark)
            setf(c, a, dark)

    # datamodules in zigzag plaatsen
    i, right = 0, size - 1
    total = len(final) * 8
    while right >= 1:
        if right == 6:
            right = 5
        for vert in range(size):
            for j in range(2):
                x = right - j
                y = size - 1 - vert if ((right + 1) & 2) == 0 else vert
                if not fun[y][x] and i < total:
                    mod[y][x] = (final[i >> 3] >> (7 - (i & 7))) & 1 == 1
                    i += 1
        right -= 2

    masks = (
        lambda x, y: (x + y) % 2 == 0, lambda x, y: y % 2 == 0, lambda x, y: x % 3 == 0,
        lambda x, y: (x + y) % 3 == 0, lambda x, y: (x // 3 + y // 2) % 2 == 0,
        lambda x, y: x * y % 2 + x * y % 3 == 0, lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0,
        lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0,
    )

    def apply(m):
        f = masks[m]
        for y in range(size):
            for x in range(size):
                if not fun[y][x] and f(x, y):
                    mod[y][x] = not mod[y][x]

    def penalty():
        p = 0
        lines = [mod[y] for y in range(size)] + [[mod[y][x] for y in range(size)] for x in range(size)]
        for line in lines:
            run, prev = 0, None
            for v in line:
                if v == prev:
                    run += 1
                else:
                    if run >= 5:
                        p += run - 2
                    run, prev = 1, v
            if run >= 5:
                p += run - 2
            s = "".join("1" if v else "0" for v in line)
            p += 40 * (s.count("10111010000") + s.count("00001011101"))
        for y in range(size - 1):
            for x in range(size - 1):
                c = mod[y][x]
                if c == mod[y][x + 1] == mod[y + 1][x] == mod[y + 1][x + 1]:
                    p += 3
        dark = sum(sum(r) for r in mod)
        p += abs(dark * 100 // (size * size) - 50) // 5 * 10
        return p

    best, best_p = 0, None
    for m in range(8):
        apply(m)
        draw_format(m)
        pen = penalty()
        if best_p is None or pen < best_p:
            best, best_p = m, pen
        apply(m)          # terugdraaien (xor)
    apply(best)
    draw_format(best)
    return mod


def qr_png(matrix, path, scale=12, border=4):
    """Bewaart de QR-code als PNG (zwart-wit), met enkel de standaardbibliotheek."""
    import zlib
    n = len(matrix)
    side = (n + 2 * border) * scale
    rows = []
    for y in range(side):
        my = y // scale - border
        line = bytearray([0])
        for x in range(side):
            mx = x // scale - border
            dark = 0 <= mx < n and 0 <= my < n and matrix[my][mx]
            line.append(0 if dark else 255)
        rows.append(bytes(line))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", side, side, 8, 0, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ======================================================================== SAMEN (gedeeld)
# Dit blok staat identiek in server.py (Ponte_VR). Pas het op beide plaatsen aan.

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
GZIP_EXT = {".html", ".htm", ".js", ".mjs", ".css", ".json", ".glb", ".gltf", ".svg", ".txt", ".csv", ".obj", ".bin"}
LOG_FIELDS = ["duur_s", "gevoel", "voorinstelling", "beweeg", "draai", "snelheid", "vignet", "zweef", "ring", "samen", "pagina", "toestel"]
_GZ_CACHE = {}
_GZ_LOCK = threading.Lock()
_LOG_LOCK = threading.Lock()


def is_websocket(handler):
    return "websocket" in handler.headers.get("Upgrade", "").lower()


class WSConn:
    """Minimale WebSocket-verbinding (RFC 6455), enkel tekstberichten."""

    def __init__(self, handler):
        self.rfile = handler.rfile
        self.sock = handler.connection
        self.wlock = threading.Lock()
        self.closed = False
        self.sock.settimeout(90)          # de viewer stuurt elke 25 s een teken van leven

    def _read(self, n):
        data = self.rfile.read(n)
        if data is None or len(data) < n:
            raise EOFError
        return data

    def recv(self):
        """Volgend tekstbericht, of None als de verbinding dicht is."""
        parts = bytearray()
        try:
            while True:
                b0, b1 = self._read(2)
                fin, op = b0 & 0x80, b0 & 0x0F
                n = b1 & 0x7F
                if n == 126:
                    n = struct.unpack(">H", self._read(2))[0]
                elif n == 127:
                    n = struct.unpack(">Q", self._read(8))[0]
                if n > (1 << 20):
                    return None
                mask = self._read(4) if b1 & 0x80 else b"\0\0\0\0"
                data = bytearray(self._read(n)) if n else bytearray()
                for i in range(n):
                    data[i] ^= mask[i & 3]
                if op == 0x8:                 # sluiten
                    return None
                if op == 0x9:                 # ping -> pong
                    self._frame(0xA, bytes(data))
                    continue
                if op == 0xA:
                    continue
                parts += data
                if fin:
                    return parts.decode("utf-8", "replace")
        except (EOFError, OSError, ValueError):
            return None

    def _frame(self, op, payload):
        n = len(payload)
        if n < 126:
            head = struct.pack(">BB", 0x80 | op, n)
        elif n < 65536:
            head = struct.pack(">BBH", 0x80 | op, 126, n)
        else:
            head = struct.pack(">BBQ", 0x80 | op, 127, n)
        with self.wlock:
            if self.closed:
                return
            try:
                self.sock.sendall(head + payload)
            except OSError:
                self.closed = True

    def send(self, obj):
        self._frame(0x1, json.dumps(obj, separators=(",", ":")).encode("utf-8"))

    def close(self):
        if not self.closed:
            self._frame(0x8, b"")
            self.closed = True


class SamenRelay:
    """Eén klas per server. De docent stuurt de toestand en zijn positie; de studenten volgen."""

    def __init__(self, pin=None):
        self.pin = pin or "%04d" % random.SystemRandom().randint(0, 9999)
        self.lock = threading.Lock()
        self.clients = {}      # WSConn -> {"id", "rol", "naam"}
        self.state = None      # laatste toestand van de docent
        self.pose = None       # laatste positie en aanwijsstraal van de docent
        self.nr = 0

    # ---- verbinding
    def handle(self, handler):
        key = handler.headers.get("Sec-WebSocket-Key")
        if not key:
            handler.send_error(400, "WebSocket verwacht")
            return
        accept = base64.b64encode(hashlib.sha1((key + WS_GUID).encode()).digest()).decode()
        handler.send_response(101, "Switching Protocols")
        handler.send_header("Upgrade", "websocket")
        handler.send_header("Connection", "Upgrade")
        handler.send_header("Sec-WebSocket-Accept", accept)
        handler.end_headers()
        handler.close_connection = True
        conn, info = WSConn(handler), None
        try:
            while True:
                txt = conn.recv()
                if txt is None:
                    break
                try:
                    msg = json.loads(txt)
                except ValueError:
                    continue
                if not isinstance(msg, dict):
                    continue
                if info is None:
                    if msg.get("t") == "hallo":
                        info = self._join(conn, msg)
                    continue
                self._on_message(conn, info, msg)
        finally:
            conn.close()
            if info:
                self._leave(conn, info)

    def _join(self, conn, msg):
        reden = ""
        with self.lock:
            self.nr += 1
            rol = msg.get("rol") if msg.get("rol") in ("docent", "student") else "student"
            if rol == "docent" and str(msg.get("pin", "")).strip() != self.pin:
                rol, reden = "student", "Verkeerde PIN: je bent verbonden als student."
            naam = str(msg.get("naam") or "").strip()[:24]
            if not naam:
                naam = "Docent" if rol == "docent" else "Student %d" % self.nr
            info = {"id": self.nr, "rol": rol, "naam": naam}
            self.clients[conn] = info
            state, pose = self.state, self.pose
        conn.send({"t": "welkom", "id": info["id"], "rol": rol, "naam": naam, "reden": reden})
        if rol == "student":
            if state is not None:
                conn.send({"t": "toestand", "s": state})
            if pose is not None:
                conn.send(pose)
        self._send_list()
        return info

    def _leave(self, conn, info):
        with self.lock:
            self.clients.pop(conn, None)
            if not any(i["rol"] == "docent" for i in self.clients.values()):
                self.pose = None
        if info["rol"] == "student":
            self._send_to("docent", {"t": "weg", "id": info["id"]})
        self._send_list()

    def _on_message(self, conn, info, msg):
        t = msg.get("t")
        if info["rol"] == "docent":
            if t == "toestand" and isinstance(msg.get("s"), dict):
                with self.lock:
                    self.state = msg["s"]
                self._send_to("student", {"t": "toestand", "s": msg["s"]})
            elif t == "pose":
                pose = {"t": "pose", "p": msg.get("p"), "y": msg.get("y"), "h": msg.get("h"),
                        "e": msg.get("e"), "hit": bool(msg.get("hit"))}
                with self.lock:
                    self.pose = pose
                self._send_to("student", pose)
            elif t == "roep":
                self._send_to("student", {"t": "roep"})
        elif t == "pose":
            self._send_to("docent", {"t": "spose", "id": info["id"], "naam": info["naam"],
                                     "p": msg.get("p"), "y": msg.get("y")})

    # ---- versturen
    def _send_to(self, rol, obj):
        with self.lock:
            targets = [c for c, i in self.clients.items() if i["rol"] == rol]
        for c in targets:
            c.send(obj)

    def _send_list(self):
        with self.lock:
            studenten = [{"id": i["id"], "naam": i["naam"]} for i in self.clients.values() if i["rol"] == "student"]
            docent = any(i["rol"] == "docent" for i in self.clients.values())
            targets = list(self.clients)
        for c in targets:
            c.send({"t": "lijst", "studenten": studenten, "docent": docent})

    def counts(self):
        with self.lock:
            rollen = [i["rol"] for i in self.clients.values()]
        return rollen.count("docent"), rollen.count("student")


def _cors(handler):
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "ngrok-skip-browser-warning, content-type")
    handler.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")


def send_ping(handler, relay):
    """GET /ping: laat het startportaal (GitHub Pages) zien dat deze server aan staat."""
    docent, studenten = relay.counts()
    body = json.dumps({"ok": True, "samen": {"docent": docent > 0, "studenten": studenten}}).encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    _cors(handler)
    handler.end_headers()
    handler.wfile.write(body)


def send_preflight(handler):
    """OPTIONS: toestemming voor het portaal om /ping op te vragen."""
    handler.send_response(204)
    _cors(handler)
    handler.send_header("Access-Control-Max-Age", "86400")
    handler.end_headers()


def send_gzip(handler):
    """Stuurt een bestand gecomprimeerd. Geeft False terug als de gewone weg moet."""
    if "gzip" not in handler.headers.get("Accept-Encoding", ""):
        return False
    path = handler.translate_path(handler.path)
    if os.path.isdir(path):
        if not handler.path.split("?", 1)[0].endswith("/"):
            return False
        path = os.path.join(path, "index.html")
    if not os.path.isfile(path) or os.path.splitext(path)[1].lower() not in GZIP_EXT:
        return False
    st = os.stat(path)
    ims = handler.headers.get("If-Modified-Since")
    if ims:
        try:
            if email.utils.parsedate_to_datetime(ims).timestamp() >= int(st.st_mtime):
                handler.send_response(304)
                handler.send_header("Last-Modified", handler.date_time_string(st.st_mtime))
                handler.end_headers()
                return True
        except (TypeError, ValueError, OverflowError, IndexError):
            pass
    key = (path, st.st_mtime_ns, st.st_size)
    with _GZ_LOCK:
        data = _GZ_CACHE.get(key)
    if data is None:
        with open(path, "rb") as f:
            data = gzip.compress(f.read(), 6)
        with _GZ_LOCK:
            if len(_GZ_CACHE) > 24:
                _GZ_CACHE.clear()
            _GZ_CACHE[key] = data
    handler.send_response(200)
    handler.send_header("Content-Type", handler.guess_type(path))
    handler.send_header("Content-Encoding", "gzip")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Last-Modified", handler.date_time_string(st.st_mtime))
    handler.send_header("Vary", "Accept-Encoding")
    handler.end_headers()
    if handler.command != "HEAD":
        handler.wfile.write(data)
    return True


def write_log(handler, folder):
    """POST /log: een regel per VR-sessie in vr_log.csv (puntkomma's, opent rechtstreeks in Excel)."""
    try:
        n = int(handler.headers.get("Content-Length") or 0)
        if n > 8000:
            handler.send_error(413)
            return
        data = json.loads(handler.rfile.read(n) or b"{}")
        if not isinstance(data, dict):
            raise ValueError
    except ValueError:
        handler.send_error(400)
        return
    row = [time.strftime("%Y-%m-%d %H:%M:%S")] + [str(data.get(k, ""))[:80].replace("\n", " ") for k in LOG_FIELDS]
    path = os.path.join(folder, "vr_log.csv")
    try:
        with _LOG_LOCK:
            new = not os.path.exists(path)
            with open(path, "a", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f, delimiter=";")
                if new:
                    w.writerow(["tijd"] + LOG_FIELDS)
                w.writerow(row)
    except OSError:
        handler.send_error(500)
        return
    handler.send_response(204)
    handler.end_headers()

# ======================================================================== einde SAMEN

# Eén Samen-relais voor de hele app: de docent-PIN blijft gelijk zolang de app open is.
RELAY = SamenRelay()


def pretty(rel):
    return rel.replace("/", " › ")


class QuietHandler(SimpleHTTPRequestHandler):
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({
        ".glb": "model/gltf-binary",
        ".gltf": "model/gltf+json",
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".wasm": "application/wasm",
    })

    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        # Altijd de nieuwste versie tonen, maar een ongewijzigd bestand niet opnieuw versturen
        # (304). Samen met gzip spaart dat veel van het gratis ngrok-dataverkeer.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    # Het hoofdadres toont een startpagina met alle modellen (grote knoppen voor de Quest).
    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path == "/":
            return self.send_start_page()
        if path == "/samen":                       # Samen-modus: docent leidt, studenten kijken mee
            if is_websocket(self):
                return RELAY.handle(self)
            self.send_error(426, "Gebruik een WebSocket")
            return None
        if path == "/ping":                        # startportaal: staat deze server aan?
            return send_ping(self, RELAY)
        if send_gzip(self):
            return None
        return super().do_GET()

    def do_OPTIONS(self):
        return send_preflight(self)

    def do_POST(self):
        # /log: na elke VR-sessie een regel in vr_log.csv in je modellenmap (comfort en misselijkheid)
        if urllib.parse.urlsplit(self.path).path == "/log":
            return write_log(self, self.directory)
        self.send_error(404)
        return None

    def do_HEAD(self):
        if urllib.parse.urlsplit(self.path).path == "/":
            return self.send_start_page(head_only=True)
        return super().do_HEAD()

    def list_directory(self, path):
        # geen lijst van alle bestanden in je map tonen aan wie de link heeft
        self.send_error(404, "Niet gevonden")
        return None

    def send_start_page(self, head_only=False):
        body = start_page_html(self.directory).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)


def page_title(folder, rel):
    """Titel van een VR-pagina: de <title> uit het bestand, anders een nette bestandsnaam."""
    try:
        with open(os.path.join(folder, rel), "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(6000)
        low = head.lower()
        a = low.find("<title>")
        b = low.find("</title>", a)
        if a != -1 and b != -1:
            t = html_lib.unescape(head[a + 7:b]).strip()
            if t:
                return t
    except Exception:
        pass
    name = os.path.splitext(rel.split("/")[-1])[0]
    for suffix in ("-vr", "_vr", " vr"):
        if name.lower().endswith(suffix):
            name = name[:-len(suffix)]
    name = name.replace("-", " ").replace("_", " ").strip() or rel
    return name[:1].upper() + name[1:]


def start_page_html(folder):
    pages, _ = scan_folder(folder)
    items = []
    for rel in pages:
        sub = rel.rsplit("/", 1)[0].replace("/", " › ") if "/" in rel else ""
        title = page_title(folder, rel)
        if sub.replace("-", " ").replace("_", " ").lower() == title.lower():
            sub = ""
        items.append(
            '<a class="m" href="/{href}"><span class="t">{title}</span>{sub}</a>'.format(
                href=urllib.parse.quote(rel),
                title=html_lib.escape(title),
                sub='<span class="s">{}</span>'.format(html_lib.escape(sub)) if sub else ""))
    if not items:
        items.append('<p class="e">Er staan nog geen VR-pagina’s in deze map.</p>')
    return """<!doctype html>
<html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VR-modellen</title>
<style>
 body{{margin:0;background:#1c2330;color:#fff;font-family:system-ui,"Segoe UI",sans-serif}}
 header{{padding:28px 32px 18px;border-bottom:5px solid #f2b705}}
 h1{{margin:0;font-size:34px}} header p{{margin:6px 0 0;color:#b8c0cc;font-size:18px}}
 main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px;padding:28px 32px}}
 a.m{{display:block;background:#2a3344;border:2px solid #3a4558;border-radius:16px;padding:26px 24px;
      color:#fff;text-decoration:none;min-height:80px}}
 a.m:hover,a.m:focus{{border-color:#f2b705;background:#323d52;outline:none}}
 .t{{display:block;font-size:26px;font-weight:600}} .s{{display:block;margin-top:6px;color:#b8c0cc;font-size:17px}}
 .e{{font-size:20px;color:#b8c0cc}}
</style></head><body>
<header><h1>Kies een model</h1><p>Open een model en druk daarna op ‘Start VR’.</p></header>
<main>{items}</main>
</body></html>""".format(items="\n".join(items))


HELP_TEXT = [
    ("h", "Wat doet deze app?"),
    ("p", "De app maakt je VR-pagina’s bereikbaar voor de browser van je Meta Quest. "
          "Ze start een webserver op je computer en een beveiligde https-link via ngrok. "
          "De Quest heeft die https-link nodig om VR te mogen starten."),
    ("h", "De eerste keer"),
    ("b", "Maak een gratis account op ngrok.com (knop ‘Gratis account maken’)."),
    ("b", "Klik op ‘Download ngrok’. Of download ngrok zelf en kies het met ‘Kies ngrok.exe…’."),
    ("b", "Klik op ‘Authtoken invullen…’ en plak de code van je ngrok-dashboard."),
    ("b", "Aangeraden: klik op ‘Vast adres instellen…’. Je gratis vaste adres staat in je "
          "ngrok-dashboard bij ‘Domains’. Dan blijft je link altijd dezelfde."),
    ("h", "Een VR-pagina maken"),
    ("p", "Exporteer je model als .glb-bestand (bv. vanuit Revit, SketchUp of Blender). "
          "Vraag daarna aan Claude: ‘Maak een WebXR-pagina die mijn model <naam>.glb toont "
          "op een Meta Quest.’ Je krijgt een .html-bestand."),
    ("h", "Je map organiseren"),
    ("p", "Maak één hoofdmap, bv. C:\\VR-modellen, met een submap per model:"),
    ("c", "VR-modellen\n  vakwerkbrug\n    vakwerkbrug-vr.html\n    vakwerkbrug.glb\n"
          "  kantoorgebouw\n    kantoorgebouw-vr.html\n    kantoorgebouw.glb"),
    ("p", "Kies in stap 1 de hoofdmap. Nieuw model toegevoegd? Klik op ‘Vernieuwen’. "
          "Gebruik bij voorkeur geen spaties in bestandsnamen."),
    ("h", "Op de Quest"),
    ("b", "Klik op Start en open de Browser op je Quest."),
    ("b", "Typ het adres uit het gele vak. Je komt op een startpagina met alle modellen."),
    ("b", "Klik op ‘Visit Site’ als ngrok dat vraagt, kies een model en druk op ‘Start VR’."),
    ("b", "Maak een bladwijzer van de startpagina (werkt het best met een vast adres)."),
    ("b", "Laat de app open zolang je de Quest gebruikt."),
    ("h", "QR-code scannen"),
    ("p", "Na Start toont de app een QR-code van het gekozen model (of van de startpagina). Studenten scannen "
          "die met hun Quest en hoeven niets te typen."),
    ("b", "Klik op ‘QR groot tonen’ om de code op de beamer te tonen."),
    ("b", "Op de Quest 3 en 3S heb je een QR-scanner nodig, bv. de gratis app ‘QR Scanner’ uit de Meta Store. "
          "Die installeer je één keer per bril."),
    ("b", "Vink ‘meteen in Samen’ aan: dan komen studenten via de code meteen in de Samen-modus en volgen ze de docent."),
    ("b", "Met een vast adres (stap 2) blijft de code altijd dezelfde. Bewaar hem dan met ‘QR opslaan…’ "
          "en hang hem afgedrukt op in het lokaal."),
    ("h", "Samen kijken met de klas"),
    ("p", "Viewers met een Samen-knop (zoals de Ponte-viewer) laten de docent leiden: de studenten zien "
          "dezelfde studiemodus, de docent als gele figuur en zijn aanwijsstraal. Iedereen beweegt zelf."),
    ("b", "Docent: Samen > Ik ben de docent, en typ de Docent-PIN die in stap 3 naast de Start-knop staat."),
    ("b", "Studenten: Samen > Ik ben student. Er is geen code nodig."),
    ("b", "Elke bril gebruikt één verbinding, dus het gratis ngrok-account volstaat ook voor een klas."),
    ("h", "Comfort en vr_log.csv"),
    ("p", "Met de knop Comfort kies je teleport, tunnelzicht en draaien in stappen tegen misselijkheid. "
          "Na elke VR-sessie vraagt de viewer anoniem hoe je je voelde. Dat komt in vr_log.csv in je "
          "modellenmap: bruikbaar voor onderzoek naar misselijkheid."),
    ("h", "Problemen"),
    ("b", "‘ngrok draait nog ergens anders’: kies Ja om de oude ngrok te stoppen. "
          "Gebruik je hetzelfde account op een andere computer, stop het dan daar."),
    ("b", "De pagina blijft leeg of grijs op de Quest: klik op ‘Test op deze computer’, druk op F12, "
          "kopieer de rode foutmelding en vraag Claude om het .html-bestand te verbeteren."),
    ("b", "‘Visit Site’ verschijnt elke keer: dat is normaal bij een gratis ngrok-account."),
    ("b", "Zonder Quest testen kan ook: ‘Voorbeeld proberen’ en dan ‘Test op deze computer’."),
]


class App:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        self.server = None
        self.ngrok_proc = None
        self.ngrok_output = []
        self.port = None
        self.public_url = None
        self.running = False
        self.link_targets = []

        root.title(APP_NAME)
        root.configure(bg=BG)
        root.minsize(740, 560)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        try:
            self.logo = tk.PhotoImage(data=LOGO_PNG)
            root.iconphoto(True, self.logo)
        except Exception:
            self.logo = None

        self.build_styles()
        self.build_ui()

        folder = self.settings.get("map", "")
        if folder and os.path.isdir(folder):
            self.folder_var.set(folder)
        self.refresh_files()
        self.refresh_ngrok_status()
        self.set_pill("Gestopt", "#4a5468")
        self.draw_qr()

    # ---------- UI ----------
    def build_styles(self):
        st = ttk.Style()
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure(".", background=BG, foreground=INK, font=("Segoe UI", 10))
        st.configure("Card.TFrame", background=CARD)
        st.configure("Card.TLabel", background=CARD, foreground=INK)
        st.configure("Muted.TLabel", background=CARD, foreground=MUTED)
        st.configure("Foot.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        st.configure("H2.TLabel", background=CARD, foreground=INK, font=("Segoe UI Semibold", 12))
        st.configure("TButton", padding=(10, 5), background="#f4f5f7", bordercolor=LINE,
                     lightcolor="#f4f5f7", darkcolor="#f4f5f7", relief="flat")
        st.map("TButton", background=[("active", "#e6e9ee"), ("disabled", "#f4f5f7")])
        st.configure("Big.TButton", font=("Segoe UI Semibold", 13), padding=(22, 9),
                     background=YELLOW, bordercolor=YELLOW, lightcolor=YELLOW, darkcolor=YELLOW)
        st.map("Big.TButton", background=[("active", "#ffc933"), ("disabled", "#e3e5ea")])
        st.configure("TEntry", fieldbackground="#f7f8fa", bordercolor=LINE, lightcolor=LINE, darkcolor=LINE)

    def card(self, parent, title, step):
        outer = tk.Frame(parent, bg=CARD, highlightbackground=LINE, highlightthickness=1)
        outer.pack(fill="x", pady=(0, 10))
        inner = ttk.Frame(outer, style="Card.TFrame", padding=(14, 12))
        inner.pack(fill="both", expand=True)
        head = ttk.Frame(inner, style="Card.TFrame")
        head.pack(fill="x", pady=(0, 8))
        badge = tk.Label(head, text=str(step), bg=INK, fg=CARD, width=2,
                         font=("Segoe UI Semibold", 11))
        badge.pack(side="left", padx=(0, 10))
        badge.step = step
        ttk.Label(head, text=title, style="H2.TLabel").pack(side="left")
        body = ttk.Frame(inner, style="Card.TFrame")
        body.pack(fill="x")
        return body, badge

    def set_done(self, badge, done):
        if done:
            badge.configure(text="✓", bg=GREEN)
        else:
            badge.configure(text=str(badge.step), bg=INK)

    def build_ui(self):
        # donkere kopbalk
        header = tk.Frame(self.root, bg=INK)
        header.pack(fill="x")
        hin = tk.Frame(header, bg=INK)
        hin.pack(fill="x", padx=16, pady=12)
        if self.logo:
            tk.Label(hin, image=self.logo, bg=INK).pack(side="left", padx=(0, 12))
        titles = tk.Frame(hin, bg=INK)
        titles.pack(side="left")
        tk.Label(titles, text=APP_NAME, bg=INK, fg="#ffffff",
                 font=("Segoe UI Semibold", 16)).pack(anchor="w")
        tk.Label(titles, text="Je constructie in VR op de Meta Quest", bg=INK, fg="#b8c0cc",
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.pill = tk.Label(hin, text="", fg="#ffffff", font=("Segoe UI Semibold", 9), padx=10, pady=3)
        tk.Button(hin, text="Hulp", command=self.show_help, bg="#2f3a4d", fg="#ffffff",
                  activebackground="#3d4a61", activeforeground="#ffffff", relief="flat", bd=0,
                  font=("Segoe UI Semibold", 9), padx=12, pady=3, cursor="hand2").pack(side="right", padx=(8, 0))
        self.pill.pack(side="right")
        tk.Frame(self.root, bg=YELLOW, height=4).pack(fill="x")

        # inhoud scrollt als het scherm te klein is (laptops met 125-150% schaal)
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)
        self.page = tk.Canvas(outer, bg=BG, highlightthickness=0, borderwidth=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.page.yview)
        self.page.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.page.pack(side="left", fill="both", expand=True)
        wrap = ttk.Frame(self.page, padding=16)
        win = self.page.create_window(0, 0, window=wrap, anchor="nw")
        wrap.bind("<Configure>", lambda e: self.page.configure(scrollregion=self.page.bbox("all")))
        self.page.bind("<Configure>", lambda e: self.page.itemconfigure(win, width=e.width))

        def _wheel(e):
            if isinstance(e.widget, tk.Listbox):
                return                      # de lijst met links scrollt zelf
            try:
                if str(e.widget.winfo_toplevel()) != str(self.root):
                    return                  # hulpvenster en groot QR-venster niet
            except Exception:
                return
            if self.page.yview() != (0.0, 1.0):
                self.page.yview_scroll(int(-e.delta / 120) or (-1 if e.delta > 0 else 1), "units")
        self.root.bind_all("<MouseWheel>", _wheel)

        # Stap 1: map
        b1, self.badge1 = self.card(wrap, "Kies je map met VR-modellen", 1)
        row = ttk.Frame(b1, style="Card.TFrame")
        row.pack(fill="x")
        self.folder_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.folder_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Kies map…", command=self.choose_folder).pack(side="left", padx=(8, 0))
        if example_dir():
            ttk.Button(row, text="Voorbeeld proberen", command=self.use_example).pack(side="left", padx=(8, 0))
        frow = ttk.Frame(b1, style="Card.TFrame")
        frow.pack(fill="x", pady=(8, 0))
        ttk.Button(frow, text="↻ Vernieuwen", command=self.refresh_all).pack(side="right", anchor="n", padx=(8, 0))
        self.files_label = ttk.Label(frow, text="", style="Muted.TLabel", wraplength=520, justify="left")
        self.files_label.pack(side="left", anchor="w", fill="x", expand=True)

        # Stap 2: ngrok
        b2, self.badge2 = self.card(wrap, "ngrok (voor de beveiligde link)", 2)
        self.ngrok_label = ttk.Label(b2, text="", style="Card.TLabel", wraplength=600, justify="left")
        self.ngrok_label.pack(anchor="w")
        nrow = ttk.Frame(b2, style="Card.TFrame")
        nrow.pack(anchor="w", pady=(8, 0))
        self.dl_btn = ttk.Button(nrow, text="Download ngrok", command=self.download_ngrok)
        self.dl_btn.pack(side="left")
        ttk.Button(nrow, text="Kies ngrok.exe…", command=self.choose_ngrok).pack(side="left", padx=(8, 0))
        ttk.Button(nrow, text="Authtoken invullen…", command=self.ask_token).pack(side="left", padx=(8, 0))
        nrow2 = ttk.Frame(b2, style="Card.TFrame")
        nrow2.pack(anchor="w", pady=(6, 0))
        ttk.Button(nrow2, text="Vast adres instellen…", command=self.ask_domain).pack(side="left")
        ttk.Button(nrow2, text="Gratis account maken",
                   command=lambda: webbrowser.open(NGROK_SIGNUP_PAGE)).pack(side="left", padx=(8, 0))

        # Stap 3: start
        b3, self.badge3 = self.card(wrap, "Start en open op de Quest", 3)
        srow = ttk.Frame(b3, style="Card.TFrame")
        srow.pack(fill="x")
        self.start_btn = ttk.Button(srow, text="Start", style="Big.TButton", command=self.toggle)
        self.start_btn.pack(side="left")
        self.status_label = ttk.Label(srow, text="Nog niet gestart.", style="Muted.TLabel",
                                      wraplength=440, justify="left")
        self.status_label.pack(side="left", padx=(14, 0))
        pinbox = tk.Frame(srow, bg=INK, padx=12, pady=6)
        pinbox.pack(side="right")
        tk.Label(pinbox, text="Docent-PIN voor Samen", bg=INK, fg="#b8c0cc",
                 font=("Segoe UI", 9)).pack(anchor="e")
        tk.Label(pinbox, text=RELAY.pin, bg=INK, fg=YELLOW,
                 font=("Consolas", 20, "bold")).pack(anchor="e")

        ttk.Label(b3, text="Links:", style="Card.TLabel").pack(anchor="w", pady=(12, 4))
        lb_frame = tk.Frame(b3, bg=LINE, padx=1, pady=1)
        lb_frame.pack(fill="both", expand=True)
        self.links = tk.Listbox(lb_frame, height=4, font=("Segoe UI", 10), activestyle="none",
                                bg="#f7f8fa", fg=INK, relief="flat", highlightthickness=0,
                                selectbackground=YELLOW, selectforeground=INK, borderwidth=6)
        self.links.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(lb_frame, orient="vertical", command=self.links.yview)
        sb.pack(side="left", fill="y")
        self.links.configure(yscrollcommand=sb.set)
        self.links.bind("<<ListboxSelect>>", lambda e: self.show_selected())

        qrow = tk.Frame(b3, bg=CARD)
        qrow.pack(fill="x", pady=(10, 8))
        qbox = tk.Frame(qrow, bg="#ffffff", highlightbackground=LINE, highlightthickness=1)
        qbox.pack(side="right", padx=(10, 0))
        self.qr_canvas = tk.Canvas(qbox, width=QR_SMALL, height=QR_SMALL, bg="#ffffff", highlightthickness=0,
                                   cursor="hand2")
        self.qr_canvas.pack(padx=4, pady=4)
        self.qr_canvas.bind("<Button-1>", lambda e: self.show_qr_big())
        box = tk.Frame(qrow, bg=YELLOW_SOFT, highlightbackground=YELLOW, highlightthickness=2)
        box.pack(side="left", fill="both", expand=True)
        tk.Label(box, text="Scan de QR-code met de Quest, of typ dit in de browser van je Quest:", bg=YELLOW_SOFT,
                 fg=MUTED, font=("Segoe UI", 9), wraplength=420, justify="left").pack(anchor="w", padx=12, pady=(8, 0))
        self.big_link = tk.Label(box, text="—", bg=YELLOW_SOFT, fg=INK, font=("Consolas", 13, "bold"),
                                 wraplength=440, justify="left")
        self.big_link.pack(anchor="w", padx=12, pady=(2, 10))
        box.bind("<Configure>", lambda e: self.big_link.configure(wraplength=max(200, e.width - 30)))

        self.samen_var = tk.BooleanVar(value=bool(self.settings.get("qr_samen")))
        tk.Checkbutton(b3, text="Studenten komen via de link meteen in Samen (ze volgen de docent)",
                       variable=self.samen_var, command=self.on_samen_toggle, bg=CARD, fg=INK,
                       activebackground=CARD, selectcolor="#ffffff", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))

        brow = ttk.Frame(b3, style="Card.TFrame")
        brow.pack(anchor="w")
        ttk.Button(brow, text="QR groot tonen", command=self.show_qr_big).pack(side="left")
        ttk.Button(brow, text="QR opslaan…", command=self.save_qr).pack(side="left", padx=(8, 0))
        ttk.Button(brow, text="Kopieer link", command=self.copy_link).pack(side="left", padx=(8, 0))
        ttk.Button(brow, text="Test op deze computer", command=self.open_local).pack(side="left", padx=(8, 0))

        tip = ("Tip: toon de QR-code op de beamer, dan hoeft niemand te typen. Klik op ‘Visit Site’ als ngrok dat "
               "vraagt en druk op ‘Start VR’. Laat dit venster open zolang je de Quest gebruikt.")
        ttk.Label(wrap, text=tip, style="Foot.TLabel", wraplength=620, justify="left").pack(anchor="w", pady=(2, 0))
        ttk.Label(wrap, text="Versie " + APP_VERSION, style="Foot.TLabel").pack(anchor="e", pady=(6, 0))

    def set_pill(self, text, color):
        self.pill.configure(text="● " + text, bg=color)

    # ---------- map ----------
    def choose_folder(self):
        start = self.folder_var.get() or os.path.expanduser("~")
        d = filedialog.askdirectory(initialdir=start, title="Kies je map met VR-modellen")
        if d:
            self.folder_var.set(os.path.normpath(d))
            self.settings["map"] = self.folder_var.get()
            save_settings(self.settings)
            if not self.running:
                self.stop_server()
            self.refresh_files()

    def use_example(self):
        if self.running:
            messagebox.showinfo(APP_NAME, "Klik eerst op Stop.")
            return
        # niet bewaren: na een update van de app verandert de installatiemap
        self.folder_var.set(example_dir())
        self.stop_server()
        self.refresh_files()

    def html_files(self):
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            return []
        return scan_folder(folder)[0]

    def refresh_files(self):
        folder = self.folder_var.get()
        ok = False
        if not folder:
            txt = "Nog geen map gekozen. Geen modellen bij de hand? Klik op ‘Voorbeeld proberen’."
        elif not os.path.isdir(folder):
            txt = "Deze map bestaat niet (meer). Kies een andere map."
        else:
            html, models = scan_folder(folder)
            if not html:
                txt = ("Geen VR-pagina’s (HTML) gevonden. Zet het bestand dat Claude voor je maakte "
                       "in deze map, eventueel in een eigen submap per model.")
            else:
                ok = True
                shown = [pretty(h) for h in html[:6]]
                txt = "{} VR-pagina{} gevonden: {}".format(len(html), "" if len(html) == 1 else "’s",
                                                             ", ".join(shown))
                if len(html) > 6:
                    txt += " …"
                if models:
                    txt += "   ·   {} 3D-model{}".format(len(models), "" if len(models) == 1 else "len")
        self.files_label.configure(text=txt)
        self.set_done(self.badge1, ok)

    # ---------- ngrok ----------
    def find_ngrok(self):
        candidates = [
            self.settings.get("ngrok_pad", ""),
            os.path.join(DATA_DIR, "ngrok.exe"),
            os.path.join(app_dir(), "ngrok.exe"),
        ]
        for c in candidates:
            if c and os.path.isfile(c):
                return c
        return shutil.which("ngrok")

    def ngrok_cmd(self, exe, *args):
        cmd = [exe] + list(args)
        # eigen config in de datamap; een eerder ingestelde (standaard) config blijft ook werken
        if os.path.isfile(NGROK_CONFIG):
            cmd += ["--config", NGROK_CONFIG]
        return cmd

    def refresh_ngrok_status(self):
        exe = self.find_ngrok()
        token = bool(self.settings.get("token_ingesteld"))
        if exe:
            txt = "✓ ngrok gevonden."
            txt += " Authtoken is ingesteld." if token else " Vul nu één keer je authtoken in (van je gratis ngrok-account)."
            domain = self.settings.get("vast_adres")
            if domain:
                txt += "\nVast adres: " + domain
            elif token:
                txt += ("\nTip: stel een vast adres in. Dan blijft je link altijd dezelfde en werkt een "
                        "bladwijzer op de Quest ook de volgende keer.")
            self.dl_btn.state(["disabled"])
        else:
            txt = ("ngrok is een apart, gratis programma dat de beveiligde link maakt. "
                   "Klik op ‘Download ngrok’ (±10 MB), of download het zelf via ngrok.com en kies het met ‘Kies ngrok.exe…’.")
            self.dl_btn.state(["!disabled"])
        self.ngrok_label.configure(text=txt)
        self.set_done(self.badge2, bool(exe and token))

    def ask_domain(self):
        if messagebox.askyesno(APP_NAME,
                               "Met een gratis ngrok-account krijg je één vast adres "
                               "(bv. jouw-naam.ngrok-free.app). Je vindt het in je ngrok-dashboard "
                               "bij ‘Domains’. Staat er nog geen, klik daar dan op ‘+ New Domain’.\n\n"
                               "Wil je die pagina nu openen?"):
            webbrowser.open(NGROK_DOMAIN_PAGE)
        current = self.settings.get("vast_adres", "")
        value = simpledialog.askstring(APP_NAME, "Plak hier je vaste ngrok-adres.\n"
                                                 "Laat leeg om geen vast adres te gebruiken.",
                                       initialvalue=current, parent=self.root)
        if value is None:
            return
        value = value.strip()
        for prefix in ("https://", "http://"):
            if value.lower().startswith(prefix):
                value = value[len(prefix):]
        value = value.split("/")[0].strip().lower()
        if value and ("." not in value or " " in value):
            messagebox.showerror(APP_NAME, "Dat lijkt geen geldig adres. Het ziet er ongeveer zo uit:\n"
                                           "jouw-naam.ngrok-free.app")
            return
        if value:
            self.settings["vast_adres"] = value
        else:
            self.settings.pop("vast_adres", None)
        save_settings(self.settings)
        self.refresh_ngrok_status()
        if self.running:
            messagebox.showinfo(APP_NAME, "Klik op Stop en daarna opnieuw op Start om het nieuwe adres te gebruiken.")

    def kill_other_ngrok(self):
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/IM", "ngrok.exe", "/F"], capture_output=True,
                               creationflags=NO_WINDOW, timeout=15)
            else:
                subprocess.run(["pkill", "-x", "ngrok"], capture_output=True, timeout=15)
        except Exception:
            pass

    def download_ngrok(self):
        if not messagebox.askyesno(APP_NAME,
                                   "De app downloadt nu ngrok.exe van de officiële website van ngrok "
                                   "en bewaart het in je gebruikersmap.\n\nDoorgaan?"):
            return
        self.dl_btn.state(["disabled"])
        self.ngrok_label.configure(text="ngrok wordt gedownload…")

        def work():
            try:
                os.makedirs(DATA_DIR, exist_ok=True)
                zpath = os.path.join(DATA_DIR, "ngrok.zip")
                urllib.request.urlretrieve(NGROK_ZIP_URL, zpath)
                with zipfile.ZipFile(zpath) as z:
                    z.extract("ngrok.exe", DATA_DIR)
                os.remove(zpath)
                self.root.after(0, self.refresh_ngrok_status)
            except Exception as e:
                msg = ("Download mislukt: {}\n\nDownload ngrok zelf via ngrok.com en kies het bestand "
                       "met ‘Kies ngrok.exe…’.").format(e)
                self.root.after(0, lambda: (messagebox.showerror(APP_NAME, msg), self.refresh_ngrok_status()))

        threading.Thread(target=work, daemon=True).start()

    def choose_ngrok(self):
        if messagebox.askyesno(APP_NAME, "Heb je ngrok nog niet gedownload?\n\n"
                                         "Klik op Ja om de downloadpagina van ngrok te openen, "
                                         "of op Nee als je ngrok.exe al hebt."):
            webbrowser.open(NGROK_DOWNLOAD_PAGE)
            return
        p = filedialog.askopenfilename(title="Kies ngrok.exe",
                                       filetypes=[("ngrok", "ngrok.exe"), ("Programma's", "*.exe")])
        if p:
            self.settings["ngrok_pad"] = os.path.normpath(p)
            save_settings(self.settings)
            self.refresh_ngrok_status()

    def ask_token(self):
        exe = self.find_ngrok()
        if not exe:
            messagebox.showinfo(APP_NAME, "Download of kies eerst ngrok.")
            return
        if messagebox.askyesno(APP_NAME, "Je authtoken staat op je ngrok-dashboard.\n\n"
                                         "Wil je die pagina nu openen?"):
            webbrowser.open(NGROK_TOKEN_PAGE)
        token = simpledialog.askstring(APP_NAME, "Plak hier je ngrok-authtoken:", parent=self.root)
        if not token:
            return
        token = token.strip().split()[-1]  # werkt ook als je het hele commando plakt
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            r = subprocess.run([exe, "config", "add-authtoken", token, "--config", NGROK_CONFIG],
                               capture_output=True, text=True, creationflags=NO_WINDOW, timeout=30)
            if r.returncode == 0:
                self.settings["token_ingesteld"] = True
                save_settings(self.settings)
                messagebox.showinfo(APP_NAME, "Authtoken opgeslagen. Je hoeft dit niet opnieuw te doen.")
            else:
                messagebox.showerror(APP_NAME, "Dat lukte niet:\n\n" + (r.stderr or r.stdout))
        except Exception as e:
            messagebox.showerror(APP_NAME, "Dat lukte niet: {}".format(e))
        self.refresh_ngrok_status()

    # ---------- start / stop ----------
    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def set_status(self, text, color=MUTED):
        self.status_label.configure(text=text, foreground=color)

    def start(self):
        folder = self.folder_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning(APP_NAME, "Kies eerst een map (stap 1).")
            return
        exe = self.find_ngrok()
        if not exe:
            messagebox.showwarning(APP_NAME, "Download of kies eerst ngrok (stap 2).")
            return
        if folder != example_dir():
            self.settings["map"] = folder
            save_settings(self.settings)
        self.refresh_files()

        if self.server:  # draaide al voor 'Test op deze computer'
            self.stop_server()
        if not self.start_server(folder):
            return

        self.ngrok_output = []
        try:
            self.ngrok_proc = subprocess.Popen(
                self.ngrok_cmd(exe, *self.tunnel_args()),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
        except Exception as e:
            self.stop()
            messagebox.showerror(APP_NAME, "ngrok kon niet starten: {}".format(e))
            return
        threading.Thread(target=self.read_ngrok, daemon=True).start()

        self.running = True
        self.start_btn.configure(text="Stop")
        self.set_status("Bezig met opstarten…")
        self.set_pill("Opstarten", "#a77d00")
        threading.Thread(target=self.wait_for_url, daemon=True).start()

    def tunnel_args(self):
        args = ["http", str(self.port), "--log", "stdout"]
        domain = self.settings.get("vast_adres")
        if domain:
            if self.settings.get("ngrok_oude_vlag"):
                args += ["--domain", domain]  # oudere ngrok-versies
            else:
                args += ["--url", "https://" + domain]
        return args

    def start_server(self, folder):
        # webserver: alleen op deze computer bereikbaar, ngrok maakt de rest
        handler = partial(QuietHandler, directory=folder)
        self.server = None
        for port in range(8000, 8020):
            try:
                self.server = ThreadingHTTPServer(("127.0.0.1", port), handler)
                self.port = port
                break
            except OSError:
                continue
        if not self.server:
            messagebox.showerror(APP_NAME, "Geen vrije poort gevonden (8000–8019).")
            return False
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return True

    def stop_server(self):
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
            self.server = None

    def read_ngrok(self):
        proc = self.ngrok_proc
        try:
            for line in proc.stdout:
                self.ngrok_output.append(line.strip())
                if len(self.ngrok_output) > 200:
                    self.ngrok_output.pop(0)
        except Exception:
            pass

    def url_from_log(self):
        # ngrok schrijft zelf de link in zijn meldingen: ... msg="started tunnel" ... url=https://...
        for line in list(self.ngrok_output):
            if "started tunnel" in line and "url=https://" in line:
                return line.split("url=", 1)[1].split()[0].strip('"')
        return None

    def api_addr_from_log(self):
        # het adres van ngrok's eigen webpagina (4040, of 4041/4042 als 4040 bezet is)
        for line in list(self.ngrok_output):
            if "starting web service" in line and "addr=" in line:
                return line.split("addr=", 1)[1].split()[0].strip('"')
        return None

    def wait_for_url(self):
        deadline = time.time() + 25
        while time.time() < deadline and self.running:
            url = self.url_from_log()
            if url:
                self.root.after(0, lambda u=url: self.on_url(u))
                return
            if self.ngrok_proc and self.ngrok_proc.poll() is not None:
                break
            addr = self.api_addr_from_log()
            if addr:
                try:
                    with urllib.request.urlopen("http://{}/api/tunnels".format(addr), timeout=2) as r:
                        data = json.loads(r.read().decode("utf-8"))
                    for t in data.get("tunnels", []):
                        if t.get("public_url", "").startswith("https://"):
                            url = t["public_url"]
                            self.root.after(0, lambda u=url: self.on_url(u))
                            return
                except Exception:
                    pass
            time.sleep(0.5)
        if self.running:
            self.root.after(0, self.on_ngrok_failed)

    def on_url(self, url):
        self.public_url = url.rstrip("/")
        self.set_status("✓ Actief. Typ het adres in je Quest: je ziet daar alle modellen.", GREEN)
        self.set_pill("Actief", GREEN)
        self.set_done(self.badge3, True)
        self.fill_links()

    def fill_links(self, keep=None):
        self.links.delete(0, "end")
        self.link_targets = []
        self.links.insert("end", "  ★ Startpagina met alle modellen")
        self.link_targets.append(self.public_url + "/")
        for f in self.html_files():
            self.links.insert("end", "  " + pretty(f))
            self.link_targets.append("{}/{}".format(self.public_url, urllib.parse.quote(f)))
        idx = self.link_targets.index(keep) if keep in self.link_targets else 0
        self.links.selection_set(idx)
        self.links.see(idx)
        self.show_selected()

    def refresh_all(self):
        self.refresh_files()
        if self.running and self.public_url:
            self.fill_links(keep=self.selected_link())

    def on_ngrok_failed(self):
        out = "\n".join(self.ngrok_output[-15:])
        low = out.lower()
        self.stop()
        if "unknown flag" in low and "--url" in low and not self.settings.get("ngrok_oude_vlag"):
            # oudere ngrok kent --url nog niet: opnieuw proberen met --domain
            self.settings["ngrok_oude_vlag"] = True
            save_settings(self.settings)
            self.start()
        elif "ERR_NGROK_4018" in out or "authtoken" in low:
            self.settings["token_ingesteld"] = False
            save_settings(self.settings)
            self.refresh_ngrok_status()
            messagebox.showwarning(APP_NAME, "ngrok vraagt om je authtoken.\n\n"
                                             "Klik op ‘Authtoken invullen…’ in stap 2 en probeer opnieuw.")
        elif "ERR_NGROK_108" in out or "ERR_NGROK_334" in out or "already online" in low or "simultaneous" in low:
            if messagebox.askyesno(APP_NAME,
                                   "ngrok draait nog ergens anders, bijvoorbeeld van een vorige keer of in een "
                                   "terminalvenster.\n\nWil je die andere ngrok op deze computer stoppen en "
                                   "opnieuw starten?\n\n(Gebruik je hetzelfde ngrok-account op een andere "
                                   "computer, stop het dan daar.)"):
                self.kill_other_ngrok()
                self.root.after(1500, self.start)
        elif self.settings.get("vast_adres") and "domain" in low:
            messagebox.showwarning(APP_NAME, "ngrok aanvaardt het vaste adres ‘{}’ niet.\n\n"
                                             "Controleer het adres in je ngrok-dashboard (Domains) en pas het aan "
                                             "met ‘Vast adres instellen…’.\n\nMelding van ngrok:\n{}".format(
                                                 self.settings.get("vast_adres"), out[-600:]))
        else:
            messagebox.showerror(APP_NAME, "ngrok gaf geen link.\n\nLaatste meldingen:\n" + (out or "(geen)"))

    def stop(self):
        self.running = False
        if self.ngrok_proc:
            try:
                self.ngrok_proc.terminate()
                self.ngrok_proc.wait(timeout=5)
            except Exception:
                try:
                    self.ngrok_proc.kill()
                except Exception:
                    pass
            self.ngrok_proc = None
        self.stop_server()
        self.public_url = None
        self.start_btn.configure(text="Start")
        self.set_status("Gestopt.")
        self.set_pill("Gestopt", "#4a5468")
        self.set_done(self.badge3, False)
        self.links.delete(0, "end")
        self.link_targets = []
        self.big_link.configure(text="—")
        self.draw_qr()
        if getattr(self, "qr_win", None) and self.qr_win.winfo_exists():
            self.qr_win.destroy()

    # ---------- links ----------
    def selected_link(self):
        sel = self.links.curselection()
        if not sel or sel[0] >= len(self.link_targets):
            return None
        return self.link_targets[sel[0]]

    def qr_target(self):
        """De link voor de studenten: het gekozen model, eventueel meteen in Samen."""
        link = self.selected_link()
        if link and self.samen_var.get() and not link.endswith("/"):
            link += ("&" if "?" in link else "?") + "samen=student"
        return link

    def show_selected(self):
        link = self.qr_target()
        # zonder https:// – dat hoef je op de Quest niet te typen
        self.big_link.configure(text=link.split("://", 1)[-1].rstrip("/") if link else "—")
        self.draw_qr()

    def on_samen_toggle(self):
        self.settings["qr_samen"] = self.samen_var.get()
        save_settings(self.settings)
        self.show_selected()

    @staticmethod
    def qr_image(matrix, size_px, border=4):
        n = len(matrix) + 2 * border
        scale = max(1, size_px // n)
        img = tk.PhotoImage(width=n * scale, height=n * scale)
        img.put("#ffffff", to=(0, 0, n * scale, n * scale))
        for y, row in enumerate(matrix):
            for x, dark in enumerate(row):
                if dark:
                    x0, y0 = (x + border) * scale, (y + border) * scale
                    img.put("#000000", to=(x0, y0, x0 + scale, y0 + scale))
        return img

    def draw_qr(self):
        c = self.qr_canvas
        c.delete("all")
        link = self.qr_target()
        if not link:
            c.create_text(QR_SMALL // 2, QR_SMALL // 2, text="QR-code\nverschijnt\nna Start", fill=MUTED,
                          font=("Segoe UI", 9), justify="center")
            self.qr_small = None
            return
        self.qr_small = self.qr_image(qr_matrix(link), QR_SMALL)
        c.create_image(QR_SMALL // 2, QR_SMALL // 2, image=self.qr_small)

    def show_qr_big(self):
        link = self.qr_target()
        if not link:
            messagebox.showinfo(APP_NAME, "Klik eerst op Start. Daarna verschijnt de QR-code.")
            return
        if getattr(self, "qr_win", None) and self.qr_win.winfo_exists():
            self.qr_win.destroy()
        w = tk.Toplevel(self.root, bg="#ffffff")
        self.qr_win = w
        w.title(APP_NAME + " – QR-code")
        try:
            w.iconphoto(False, self.logo)
        except Exception:
            pass
        side = max(320, min(640, self.root.winfo_screenheight() - 330))
        w.qr_img = self.qr_image(qr_matrix(link), side)
        tk.Label(w, text="Scan deze code met je Meta Quest", bg="#ffffff", fg=INK,
                 font=("Segoe UI Semibold", 22)).pack(pady=(22, 4))
        tk.Label(w, text="Open de QR-scanner op de bril, kijk naar de code en open de link. "
                         "Klik op ‘Visit Site’ en druk op ‘Start VR’.", bg="#ffffff", fg=MUTED,
                 font=("Segoe UI", 12), wraplength=side + 120).pack(padx=30)
        tk.Label(w, image=w.qr_img, bg="#ffffff").pack(pady=14)
        tk.Label(w, text="of typ:  " + link.split("://", 1)[-1].rstrip("/"), bg="#ffffff", fg=INK,
                 font=("Consolas", 14, "bold"), wraplength=side + 120).pack(padx=30)
        tk.Button(w, text="Sluiten", command=w.destroy, bg="#f4f5f7", fg=INK, relief="flat",
                  font=("Segoe UI Semibold", 11), padx=18, pady=4).pack(pady=(14, 20))
        w.bind("<Escape>", lambda e: w.destroy())
        w.lift()
        w.focus_force()

    def save_qr(self):
        link = self.qr_target()
        if not link:
            messagebox.showinfo(APP_NAME, "Klik eerst op Start. Daarna verschijnt de QR-code.")
            return
        name = "qr-" + (link.rstrip("/").rsplit("/", 1)[-1].split("?")[0].rsplit(".", 1)[0] or "startpagina")
        if link.endswith("/"):
            name = "qr-startpagina"
        path = filedialog.asksaveasfilename(title="QR-code bewaren", defaultextension=".png",
                                            initialfile=name + ".png", filetypes=[("PNG-afbeelding", "*.png")])
        if not path:
            return
        try:
            qr_png(qr_matrix(link), path, scale=16)
        except OSError as e:
            messagebox.showerror(APP_NAME, "Bewaren lukte niet: {}".format(e))
            return
        tip = ("Je gebruikt een vast adres: deze code blijft geldig. Je kunt hem afdrukken en ophangen."
               if self.settings.get("vast_adres") else
               "Let op: zonder vast adres verandert de link bij elke start. Stel een vast adres in (stap 2) "
               "als je de code wilt afdrukken.")
        messagebox.showinfo(APP_NAME, "QR-code bewaard.\n\n" + tip)

    def copy_link(self):
        link = self.qr_target()
        if not link:
            messagebox.showinfo(APP_NAME, "Start eerst en kies een model.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(link)
        self.set_status("Link gekopieerd.", GREEN)

    def open_local(self):
        # werkt ook zonder ngrok: dan start enkel de webserver op deze computer
        if not self.server:
            folder = self.folder_var.get()
            if not folder or not os.path.isdir(folder):
                messagebox.showinfo(APP_NAME, "Kies eerst een map (stap 1).")
                return
            if not self.start_server(folder):
                return
            self.set_status("Enkel op deze computer actief (zonder Quest-link).")
        link = self.selected_link() or ""
        path = link.split(self.public_url, 1)[-1] if (self.public_url and link) else ""
        if not path:
            html = self.html_files()
            path = "/" + urllib.parse.quote(html[0]) if html else "/"
        webbrowser.open("http://localhost:{}{}".format(self.port, path))

    def show_help(self):
        if getattr(self, "help_win", None) and self.help_win.winfo_exists():
            self.help_win.lift()
            return
        w = tk.Toplevel(self.root)
        self.help_win = w
        w.title(APP_NAME + " – Hulp")
        w.configure(bg=CARD)
        w.geometry("620x640")
        try:
            w.iconphoto(False, self.logo)
        except Exception:
            pass
        frame = tk.Frame(w, bg=CARD)
        frame.pack(fill="both", expand=True)
        t = tk.Text(frame, wrap="word", bg=CARD, fg=INK, relief="flat", padx=20, pady=16,
                    font=("Segoe UI", 10), spacing1=2, spacing3=4, cursor="arrow")
        sb = ttk.Scrollbar(frame, orient="vertical", command=t.yview)
        t.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        t.pack(side="left", fill="both", expand=True)
        t.tag_configure("h", font=("Segoe UI Semibold", 12), spacing1=14, spacing3=4)
        t.tag_configure("b", lmargin1=8, lmargin2=24)
        t.tag_configure("c", font=("Consolas", 10), background="#f4f5f7", lmargin1=16, lmargin2=16)
        for kind, text in HELP_TEXT:
            if kind == "h":
                t.insert("end", text + "\n", "h")
            elif kind == "b":
                t.insert("end", "•  " + text + "\n", "b")
            else:
                t.insert("end", text + "\n", kind if kind == "c" else ())
        t.insert("end", "\nVersie " + APP_VERSION + " · Ontwikkeld in het kader van de masterproef "
                        "‘VR als leerhulpmiddel in bouwkundig onderwijs’ (UGent).", ())
        t.configure(state="disabled")
        ttk.Button(w, text="Sluiten", command=w.destroy).pack(anchor="e", padx=16, pady=10)

    def on_close(self):
        self.stop()
        self.root.destroy()


def main():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # scherpe tekst op hoge-resolutieschermen
    except Exception:
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
