import os
import time
from deepface import DeepFace
import cv2
import numpy as np
import smtplib
from email.mime.text import MIMEText

# --- Configure emails ---
emails = {
    "Devansh Mankad" : "devansh7235@gmail.com" , 
    "Pithiya Shyam" : "pithiyashyam42@gmail.com",
    "Prof.Shubhangi Chaturvedi": "Shubhangi.chaturvedi@saffrony.ac.in" ,
    "Prof.Nainsi Soni" : "nainsi.soni@saffrony.ac.in" ,
    "Prof.Saliesh Patel" : "shailesh.patel@saffrony.ac.in" ,
    "Prof.Avani Dedhia" : "avani.dedhia@saffrony.ac.in" ,
    "Prof.Kunalsinh Kathia" : "kunalsinh.kathia@saffrony.ac.in" ,
    "Prof.Tausif Shaikh" : "tausif.shaikh@saffrony.ac.in" ,
    "Krish" : "1911krishpatel@gmail.com" ,
    "Bansari" : "bansipatel8780@gmail.com"
}

mail_body = {
    "Devansh Mankad": "Good Morning! Devansh Mankad. I am very very lucky to welcome you in The VEYG 2K25 Organized by Saffrony Institute Of Technology..." ,
    "Krish" : "Good Morning! Devansh Mankad. I am very very lucky to welcome you in The VEYG 2K25 Organized by Saffrony Institute Of Technology..." ,
    "Bansari" : "Good Morning! Devansh Mankad. I am very very lucky to welcome you in The VEYG 2K25 Organized by Saffrony Institute Of Technology..."
}

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "devmankad6064@gmail.com"
SENDER_PASSWORD = "ggtw lzts mgta nyik"  # Add your actual password or app password

# --- Face database ---
known_folder = "Database"
known_embeddings = []

print("Loading face embeddings...")
for file in os.listdir(known_folder):
    if file.endswith((".jpg", ".png")):
        img_path = os.path.join(known_folder, file)
        embedding = DeepFace.represent(img_path=img_path, model_name="Facenet")[0]["embedding"]
        name = os.path.splitext(file)[0]
        known_embeddings.append((name, embedding))
print("Face embeddings loaded.")

# --- Utility: Cosine similarity ---
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# --- Email function ---
def send_email(to_emails, subject, body):
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(to_emails)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_emails, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {', '.join(to_emails)}")
    except Exception as e:
        print("❌ Error sending email:", e)

# --- Track last email times ---
last_email_sent = {}
EMAIL_INTERVAL = 300  # 5 minutes

# --- Recognize faces and send email to all recognized ---
def recognize_face(frame):
    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect multiple faces
        face_objs = DeepFace.represent(img_path=frame_rgb, model_name="Facenet", enforce_detection=False)

        recognized_names = []
        results = []

        for face in face_objs:
            embedding = face["embedding"]

            match_name = "Unknown"
            similarity = 0

            # Compare with known embeddings
            for name, emb in known_embeddings:
                sim = cosine_similarity(embedding, emb)
                if sim > similarity:
                    similarity = sim
                    match_name = name

            if similarity >= 0.7:
                results.append(f"{match_name} ({similarity:.2f})")
                recognized_names.append(match_name)
            else:
                results.append("No Match Found")

        # Send one email to all recognized people at once
        emails_to_send = []
        body_lines = []
        current_time = time.time()

        for name in recognized_names:
            if name in emails:
                last_sent = last_email_sent.get(name, 0)
                if current_time - last_sent >= EMAIL_INTERVAL:
                    emails_to_send.append(emails[name])
                    body_lines.append(mail_body[name])
                    last_email_sent[name] = current_time

        emails_to_send = list(set(emails_to_send))  # Remove duplicates
        combined_body = "\n\n".join(body_lines)

        if emails_to_send and combined_body:
            send_email(
                to_emails=emails_to_send,
                subject="Welcome to VEYG 2K25!",
                body=combined_body
            )

        # --- Save the frame ---
        save_folder = "CapturedFrames"
        os.makedirs(save_folder, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        frame_filename = os.path.join(save_folder, f"frame_{timestamp}.jpg")
        cv2.imwrite(frame_filename, frame)
        print(f"📷 Frame saved: {frame_filename}")

        return results if results else ["No face detected"]

    except Exception as e:
        print("Error:", e)
        return ["No face detected"]

# --- Example usage with webcam ---
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        faces = recognize_face(frame)
        print(faces)

        # Show frame (optional)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
