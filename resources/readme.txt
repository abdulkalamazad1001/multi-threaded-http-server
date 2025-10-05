Multi-threaded HTTP Server:-

Project Description:-

This project is a simple multi-threaded HTTP server built using low-level socket programming in Python. The server:

Serves static files like HTML pages, JPEG images, and text files on GET requests.
Accepts POST requests with JSON data, saves the JSON as files.
Handles multiple clients concurrently using a thread pool.
Supports persistent HTTP connections with keep-alive and connection timeout.
Implements security measures such as path traversal prevention and host header validation.
Returns proper HTTP error responses as per protocol.


How to Run:-
Open a command prompt or terminal in your project directory and run:
python server.py

You may also specify custom arguments:
python server.py 8000 0.0.0.0 20

This starts the server on port 8000, listening on all interfaces, with a thread pool size of 20.


How to Test GET requests:-

Open a web browser and go to:

http://127.0.0.1:8080/
You can also test specific pages or files:

text
http://127.0.0.1:8080/about.html
http://127.0.0.1:8080/sample.txt
http://127.0.0.1:8080/photo1.jpg


POST JSON uploads:-

Use this curl command from another terminal window:

curl -i -X POST http://127.0.0.1:8080/upload -H "Content-Type: application/json" -d "{\"name\":\"Test User\",\"message\":\"Hello Server!\"}"
This sends JSON data to the server. Uploaded JSON files will be saved inside resources/uploads/.


Features Implemented:-

Multi-threading with a thread pool to handle concurrent clients efficiently.
Serving HTML, JPEG, and text files with correct content types and headers.
Accepting and saving JSON uploads via POST requests.
Connection persistence (keep-alive) and connection timeout features implemented.
Path traversal protection and HTTP Host header validation for security.
Proper HTTP error status codes and messages for various client and server errors.


Folder Structure:-

server.py
resources/
  ├── index.html
  ├── about.html
  ├── contact.html
  ├── photo1.jpg
  ├── photo2.jpg
  ├── photo3.jpg
  ├── photo4.jpg
  ├── sample.txt
  ├── readme.txt
  └── uploads/   # directory where POSTed JSON files are saved


How to Test POST JSON Uploads:-

Run this command in your terminal (make sure you are in the project directory):

curl -i -X POST http://127.0.0.1:8080/upload -H "Content-Type: application/json" -d @sample.json
The -d @sample.json tells curl to send the contents of the file.

The server will save the JSON in the resources/uploads/ folder with a unique file name.
You will receive a JSON response confirming the upload and the file path.


Known Issues or Limitations:-

Does not currently support HTTPS (no SSL/TLS).
Does not provide detailed user authentication or session management.
Assumes well-formed HTTP/1.1 requests and may not handle very large payloads beyond buffer sizes.
No advanced caching or compression mechanisms.
Designed primarily for educational and prototype purposes