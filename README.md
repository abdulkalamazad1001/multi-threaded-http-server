# Multi-threaded HTTP Server (Python)

## Project Overview
This project is a multi-threaded HTTP server created using socket programming in Python.  
It can serve several clients at once, send web pages and files, and accept uploads—all while keeping multiple users connected at the same time.

---

## Features Implemented

- **Handles Many Clients:** Uses threads to manage multiple users at once. No one needs to wait!
- **Serves Files:** You can open HTML pages, download images (JPEG) and text files.
- **POST JSON Uploads:** Accepts JSON data from users and saves each upload as a new file in the uploads folder.
- **Connection Persistence:** Keeps connections open using "keep-alive", so users can make many requests without reconnecting each time.
- **Strong Security:**
  - Blocks bad paths like `../something.txt` to keep files safe.
  - Only allows requests with the correct Host header (like `localhost:8080` or `127.0.0.1:8080`).
- **Error Handling:** Sends proper error codes and messages (404 for missing files, 403 for forbidden, 405 for wrong methods, etc.).
- **Logging:** Logs every important action—server starts, every connection, file download/upload, thread status, security checks, and errors—with time.

---

## How It Works

- **GET Requests:** If you open a page or ask for a file, the server sends it (HTML, JPEG, TXT). For files, it sets headers so your browser downloads them.
- **POST Uploads:** If you send JSON data, the server saves it in `resources/uploads/` and gives you a response showing where your data was saved.
- **Thread Pool:** Server creates a bunch of threads (default is 10), so many users can be served together. If too many people connect, new ones wait in a queue.
- **Connection Queue:** If all threads are busy, requests go into a queue and are handled as soon as a thread is free.
- **Timeout & Limits:** If a user stays idle, their connection closes after 30 seconds. Server also limits max requests per connection to 100 for fairness.

---

## How to Run the Server

Open your terminal/command prompt in the project folder.

Run:
```bash
python server.py
```
This starts the server with default settings: `localhost:8080` and 10 threads.

You can use other settings like:
```bash
python server.py 8000 0.0.0.0 20
```
That starts on port 8000, all interfaces, and 20 threads.

---

## How to Test

### Testing GET Requests

Open a browser and go to:
```
http://127.0.0.1:8080/
```
You can also try:
```
http://127.0.0.1:8080/about.html
http://127.0.0.1:8080/contact.html
http://127.0.0.1:8080/photo1.jpg
http://127.0.0.1:8080/sample.txt
```
Images and text files will download; HTML pages will show up in browser.

### Testing POST JSON Uploads

Make a file called `sample.json` with this content:
```json
{
  "name": "Abdul Kalam Azad",
  "email": "ak@gmail.com",
  "message": "This is a test JSON upload for the HTTP serve."
}
```
Upload using this command (in your project folder):
```bash
curl -i -X POST http://127.0.0.1:8080/upload -H "Content-Type: application/json" -d @sample.json
```
The server saves your data in `resources/uploads/` and tells you the file path in its reply.

### Testing Errors and Security

- Try wrong paths like `/../etc/passwd` or missing files like `/missing.png`—should return 403 or 404.
- Try sending a POST with non-JSON content—should return 415.
- Try using a bad Host header—should return 403.

### Concurrency Testing

Open several browsers or run multiple curl commands together. Check the logs: you’ll see all requests handled at the same time.

---

## Project Folder Structure

```
MULTITHREADED_HTTP_SERVER
│
├── server.py
├── README.md
├── sample.json
├── resources/
│   ├── uploads/
│   ├── about.html
│   ├── contact.html
│   ├── index.html
│   ├── photo1.jpg
│   ├── photo2.jpg
│   ├── photo3.jpg
│   ├── photo4.jpg
│   ├── readme.txt
│   └── sample.txt
```

---

## Notes and Known Limits

- Only supports HTML, JPEG, and text files (PNG possible, just add the file).
- No HTTPS (SSL) is used—this is a basic learning server.
- Works best for small demo files—very large files might take longer.
- No user authentication.
- Error logs are printed to console (not saved to file).

---

## My Details

**Name:** T. Abdul Kalam Azad  
**Roll No:** 10053  
**Batch:** B -- 2nd Year


Thank you for checking out my project!  
If you need to test, run, or review any part, just follow the easy instructions above.

*README by T. Abdul Kalam Azad (10053), Batch-B, 2nd Year*
