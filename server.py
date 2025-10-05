import os
import socket
import threading
import queue
import sys
import json
import random
import string
import time
import hashlib
from datetime import datetime
from urllib.parse import unquote, urlparse

# Function to get current date string in HTTP format
def get_current_date():
    return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

# Simple function to print log messages with timestamp
def log_event(message):
    print(f"[{get_current_date()}] {message}")

# Default server configs
HOST = '127.0.0.1'
PORT = 8080
MAX_THREADS = 10
BASE_DIR = os.path.join(os.getcwd(), 'resources')

# Mime types for serving files correctly
MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.txt': 'application/octet-stream',
    '.png': 'application/octet-stream',
    '.jpg': 'application/octet-stream',
    '.jpeg': 'application/octet-stream',
}

connection_queue = queue.Queue()

# Variables and lock to track active threads
active_threads_lock = threading.Lock()
active_threads_count = 0

def increment_active():
    global active_threads_count
    with active_threads_lock:
        active_threads_count += 1

def decrement_active():
    global active_threads_count
    with active_threads_lock:
        active_threads_count -= 1

def log_thread_pool_status():
    while True:
        with active_threads_lock:
            count = active_threads_count
        log_event(f"Thread pool status: {count}/{MAX_THREADS} active")
        time.sleep(30)

# Start logging thread pool status in background
status_logger_thread = threading.Thread(target=log_thread_pool_status, daemon=True)
status_logger_thread.start()

def build_response_header(status_code, content_type, content_length, connection='close', extra_headers=None):
    reason_phrases = {
        200: 'OK',
        201: 'Created',
        400: 'Bad Request',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        415: 'Unsupported Media Type',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        503: 'Service Unavailable',
    }
    response = f"HTTP/1.1 {status_code} {reason_phrases.get(status_code, '')}\r\n"
    response += f"Date: {get_current_date()}\r\n"
    response += "Server: Multi-threaded HTTP Server\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += f"Content-Length: {content_length}\r\n"
    response += f"Connection: {connection}\r\n"
    if extra_headers:
        for k, v in extra_headers.items():
            response += f"{k}: {v}\r\n"
    response += "\r\n"
    return response

def parse_http_request(request_data):
    try:
        lines = request_data.split('\r\n')
        request_line = lines[0]
        method, path, version = request_line.split()
        headers = {}
        for line in lines[1:]:
            if not line:
                break
            if ':' in line:
                k, v = line.split(':', 1)
                headers[k.strip()] = v.strip()
        return method, path, version, headers
    except:
        return None, None, None, None

def is_path_safe(base_dir, path):
    requested_path = os.path.normpath(os.path.join(base_dir, path.lstrip('/')))
    return requested_path.startswith(base_dir), requested_path

def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

def generate_random_id(length=4):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def handle_client(conn, addr):
    conn.settimeout(30)  # timeout for idle connections
    keep_alive = True
    request_count = 0
    MAX_REQUESTS = 100

    try:
        while keep_alive and request_count < MAX_REQUESTS:
            data = b''
            while b'\r\n\r\n' not in data:
                chunk = conn.recv(8192)
                if not chunk:
                    break
                data += chunk
            if not data:
                break
            header_end = data.find(b'\r\n\r\n')
            if header_end == -1:
                break

            header_data = data[:header_end].decode(errors='ignore')
            body = data[header_end + 4:]

            method, path, version, headers = parse_http_request(header_data)
            if None in (method, path, version):
                send_response(conn, 400, 'text/plain', '400 Bad Request')
                break

            # Check Host header
            host = headers.get('Host')
            if not host:
                send_response(conn, 400, 'text/plain', '400 Bad Request - Missing Host header')
                break

            expected_hosts = [f"{HOST}:{PORT}", f"localhost:{PORT}", f"127.0.0.1:{PORT}"]
            if host not in expected_hosts:
                log_event(f"Host validation failed from {addr}: {host}")
                send_response(conn, 403, 'text/plain', '403 Forbidden - Host mismatch')
                break
            else:
                log_event(f"Host validation passed from {addr}: {host}")

            # Check Connection header to decide keep-alive
            connection_header = headers.get('Connection', '').lower()
            if connection_header == 'close':
                keep_alive = False
            elif connection_header == 'keep-alive':
                keep_alive = True
            else:
                keep_alive = (version == 'HTTP/1.1')

            if method == 'GET':
                process_get_request(conn, path, headers, keep_alive)
            elif method == 'POST':
                process_post_request(conn, headers, body, keep_alive)
            else:
                send_response(conn, 405, 'text/plain', '405 Method Not Allowed', keep_alive)
                break

            request_count += 1

    except socket.timeout:
        log_event(f"Connection timeout for {addr}")
    except Exception as e:
        log_event(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        log_event(f"Connection from {addr} closed")

def send_response(conn, status_code, content_type, message, keep_alive=False, extra_headers=None):
    connection = 'keep-alive' if keep_alive else 'close'
    header = build_response_header(status_code, content_type, len(message), connection=connection, extra_headers=extra_headers)
    try:
        conn.sendall(header.encode() + message.encode())
    except:
        pass

def process_get_request(conn, path, headers, keep_alive):
    requested_path = unquote(urlparse(path).path)
    if requested_path == '/':
        requested_path = '/index.html'

    safe, abs_path = is_path_safe(BASE_DIR, requested_path)
    if not safe or '..' in requested_path or requested_path.startswith('/../') or requested_path.startswith('//'):
        send_response(conn, 403, 'text/plain', '403 Forbidden', keep_alive)
        return

    if not os.path.isfile(abs_path):
        send_response(conn, 404, 'text/plain', '404 Not Found', keep_alive)
        return

    ext = get_file_extension(abs_path)
    if ext not in MIME_TYPES:
        send_response(conn, 415, 'text/plain', '415 Unsupported Media Type', keep_alive)
        return

    if ext == '.html':
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read().encode('utf-8')
        header = build_response_header(200, MIME_TYPES[ext], len(content), connection='keep-alive' if keep_alive else 'close')
        conn.sendall(header.encode() + content)
        log_event(f"Sent HTML file: {os.path.basename(abs_path)} ({len(content)} bytes)")
    else:
        with open(abs_path, 'rb') as f:
            content = f.read()
        checksum = hashlib.sha256(content).hexdigest()
        log_event(f"Sent binary file: {os.path.basename(abs_path)} ({len(content)} bytes), SHA256: {checksum}")
        extra_headers = {
            'Content-Disposition': f'attachment; filename="{os.path.basename(abs_path)}"'
        }
        header = build_response_header(200, MIME_TYPES[ext], len(content), connection='keep-alive' if keep_alive else 'close', extra_headers=extra_headers)
        conn.sendall(header.encode() + content)

def process_post_request(conn, headers, body, keep_alive):
    try:
        content_type = headers.get('Content-Type', '')
        content_length = int(headers.get('Content-Length', '0'))
        body_bytes = body

        while len(body_bytes) < content_length:
            chunk = conn.recv(8192)
            if not chunk:
                break
            body_bytes += chunk

        if content_type != 'application/json':
            send_response(conn, 415, 'text/plain', '415 Unsupported Media Type', keep_alive)
            return

        json_data = json.loads(body_bytes.decode('utf-8'))
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        rand_id = generate_random_id()
        filename = f"upload_{timestamp}_{rand_id}.json"
        upload_dir = os.path.join(BASE_DIR, 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)

        log_event(f"Saved JSON upload: {filename}")

        response_body = json.dumps({
            "status": "success",
            "message": "File created successfully",
            "filepath": f"/uploads/{filename}"
        })
        header = build_response_header(201, 'application/json', len(response_body), connection='keep-alive' if keep_alive else 'close')
        conn.sendall(header.encode() + response_body.encode())

    except json.JSONDecodeError:
        send_response(conn, 400, 'text/plain', '400 Bad Request - Invalid JSON', keep_alive)
    except Exception as e:
        log_event(f"Error saving JSON upload: {e}")
        send_response(conn, 500, 'text/plain', '500 Internal Server Error', keep_alive)

def worker(thread_id):
    thread_name = f"Thread-{thread_id}"
    threading.current_thread().name = thread_name
    while True:
        item = connection_queue.get()
        if item is None:
            break
        conn, addr = item
        log_event(f"[{thread_name}] Connection from {addr}")
        increment_active()
        try:
            handle_client(conn, addr)
        except Exception as e:
            log_event(f"[{thread_name}] Exception: {e}")
        finally:
            decrement_active()
            conn.close()
            log_event(f"[{thread_name}] Connection from {addr} closed")
        connection_queue.task_done()

def main():
    global HOST, PORT, MAX_THREADS, BASE_DIR
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])
    if len(sys.argv) > 2:
        HOST = sys.argv[2]
    if len(sys.argv) > 3:
        MAX_THREADS = int(sys.argv[3])

    log_event(f"Server started on http://{HOST}:{PORT}")
    log_event(f"Thread pool size: {MAX_THREADS}")
    log_event(f"Serving files from '{BASE_DIR}'")
    log_event("Press Ctrl+C to stop server")

    threads = []
    for i in range(MAX_THREADS):
        t = threading.Thread(target=worker, args=(i + 1,), daemon=True)
        t.start()
        threads.append(t)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen(50)
            while True:
                conn, addr = server_socket.accept()
                with active_threads_lock:
                    current_active = active_threads_count

                if current_active >= MAX_THREADS:
                    retry_seconds = 30
                    res_hdr = build_response_header(503, 'text/plain', len("503 Service Unavailable"), connection='close', extra_headers={'Retry-After': str(retry_seconds)})
                    try:
                        conn.sendall(res_hdr.encode() + b"503 Service Unavailable\nPlease retry after 30 seconds.")
                    except:
                        pass
                    conn.close()
                    log_event(f"503 sent to {addr} due to thread pool saturation")
                    continue

                log_event(f"Assigning connection from {addr} to thread")
                connection_queue.put((conn, addr))

    except KeyboardInterrupt:
        log_event("Server shutting down")

    for _ in threads:
        connection_queue.put(None)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
