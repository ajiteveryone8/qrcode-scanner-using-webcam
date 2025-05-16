import cv2
from pyzbar.pyzbar import decode
import webbrowser
import csv
import os
import time
import winsound  # For beep sound on Windows
import pyperclip  # pip install pyperclip

# Open webcam
cap = cv2.VideoCapture(0)

opened_links = set()  # To keep track of opened links
scanned_history = []  # To keep history for display

csv_file = "scanned_qr_history.csv"
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Type", "Data"])

def play_beep():
    duration = 200  # milliseconds
    freq = 1000  # Hz
    winsound.Beep(freq, duration)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    codes = decode(frame)

    for code in codes:
        x, y, w, h = code.rect
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        data = code.data.decode('utf-8')
        qr_type = code.type
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        text = f"{qr_type}: {data}"

        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)

        # Only process new scans
        if data not in opened_links:
            print(f"[{timestamp}] Detected: {text}")
            play_beep()
            pyperclip.copy(data)  # Copy to clipboard

            # Save to CSV
            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, qr_type, data])

            # Add to history
            scanned_history.append(f"{timestamp} | {qr_type} | {data}")
            if len(scanned_history) > 10:
                scanned_history = scanned_history[-10:]  # Keep last 10

            # Open link if it's a URL
            if data.startswith("http"):
                webbrowser.open(data)

            opened_links.add(data)

    # Show history on the frame
    y0 = 30
    for i, hist in enumerate(scanned_history[::-1]):
        cv2.putText(frame, hist, (10, y0 + i*20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1)

    cv2.imshow("QR Code Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()