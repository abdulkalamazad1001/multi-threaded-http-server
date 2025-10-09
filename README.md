# Multi-threaded HTTP Server (Python)

## Project Overview
This project is a multi-threaded HTTP server created using socket programming in Python.
It can serve several clients at once, send web pages and files, and accept uploads—all while keeping multiple users connected at the same time.

---

## Features Implemented
**Handles Many Clients:** Uses threads to manage multiple users at once. No one needs to wait!

**Serves Files:** You can open HTML pages, download images (JPEG) and text files.

**POST JSON Uploads:** Accepts JSON data from users and saves each upload as a new file in the uploads folder.

**Connection Persistence:** Keeps connections open using "keep-alive", so users can make many requests without reconnecting each time.

**Strong Security:**
- Blocks bad paths like ../something.txt to keep files safe.
- Only allows requests with the correct Host header (like localhost:8080 or 127.0.0.1:8080).

**Error Handling:** Sends proper error codes and messages (404 for missing files, 403 for forbidden, 405 for wrong methods, etc.).

**Logging:** Logs every important action—server starts, every connection, file download/upload, thread status, security checks, and errors—with time.

---

## How It Works
**GET Requests:** If you open a page or ask for a file, the server sends it (HTML, JPEG, TXT). For files, it sets headers so your browser downloads them.

**POST Uploads:** If you send JSON data, the server saves it in resources/uploads/ and gives you a response showing where your data was saved.

**Thread Pool:** Server creates a bunch of threads (default is 10), so many users can be served together. If too many people connect, new ones wait in a queue.

**Connection Queue:** If all threads are busy, requests go into a queue and are handled as soon as a thread is free.

**Timeout & Limits:** If a user stays idle, their connection closes after 30 seconds. Server also limits max requests per connection to 100 for fairness.

---

## How to Run the Server
Open your terminal/command prompt in the project folder.

Run:
```bash
python server.py
