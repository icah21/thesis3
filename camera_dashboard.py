import cv2
from roboflow import Roboflow
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time

# Roboflow setup
rf = Roboflow(api_key="f4UBb9Y1BqAaVoiasTC1")
project = rf.workspace("cacaotrain").project("cacao_final")
version = project.version(1)
model = version.model

# Shared state
counts = {"Criollo": 0, "Forastero": 0, "Trinitario": 0}
last_pred_time = 0
last_predicted_frame = None
camera_ready = False
prediction_interval = 0.5
detection_active = False
last_detected_class = None
last_detection_time = 0
cooldown_time = 2
servo_queue = None

# Tkinter GUI
root = tk.Tk()
root.title("Cacao Detection")
root.geometry("900x650")
root.configure(bg="#2E2E2E")

frame = tk.Frame(root, bg="#2E2E2E")
frame.pack(expand=True)

video_label = tk.Label(frame, bd=2, relief="solid")
video_label.grid(row=0, column=0, padx=10, pady=10)

dashboard = tk.Frame(frame, bg="#2E2E2E", width=300)
dashboard.grid(row=0, column=1, sticky="ns", padx=10)

criollo_var = tk.StringVar(value="Criollo: 0")
forastero_var = tk.StringVar(value="Forastero: 0")
trinitario_var = tk.StringVar(value="Trinitario: 0")
detected_type_var = tk.StringVar(value="Detected: Waiting")

tk.Label(dashboard, text="🧠 Detection Summary", font=("Arial", 16, "bold"), fg="white", bg="#2E2E2E").pack(pady=10)
for v in [criollo_var, forastero_var, trinitario_var]:
    tk.Label(dashboard, textvariable=v, font=("Arial", 12), fg="white", bg="#2E2E2E").pack(pady=5)
tk.Label(dashboard, textvariable=detected_type_var, font=("Arial", 14, "bold"), fg="#00BFFF", bg="#2E2E2E").pack(pady=(10, 0))

tk.Button(dashboard, text="❌ Exit", font=("Arial", 12), command=lambda: root.quit(), bg="#FF6347", fg="white", relief="flat", padx=15, pady=5).pack(pady=20)
tk.Button(frame, text="🟢 Detect", font=("Arial", 12, "bold"), command=lambda: start_detection(), bg="#32CD32", fg="white", relief="flat", padx=10, pady=5).grid(row=1, column=0, pady=10)

def show_logo():
    try:
        logo_image = Image.open("cacao.jpg").resize((640, 480), Image.Resampling.LANCZOS)
        logo_tk = ImageTk.PhotoImage(logo_image)
        video_label.configure(image=logo_tk)
        video_label.image = logo_tk
    except Exception as e:
        print(f"Logo load failed: {e}")

def start_detection():
    global detection_active
    detection_active = True
    detected_type_var.set("Detected: Starting...")

def predict_and_update(frame):
    global last_pred_time, last_predicted_frame, last_detected_class, last_detection_time
    last_pred_time = time.time()
    resized_frame = cv2.resize(frame, (640, 480))

    try:
        predictions = model.predict(resized_frame, confidence=20, overlap=30).json()
    except Exception as e:
        print(f"Prediction error: {e}")
        return

    for k in counts:
        counts[k] = 0

    min_area = 5000
    valid_classes = {"Criollo", "Forastero", "Trinitario"}

    for pred in predictions.get("predictions", []):
        label = pred['class']
        if label not in valid_classes:
            continue

        x, y, w, h = map(int, [pred['x'], pred['y'], pred['width'], pred['height']])
        area = w * h
        x1, y1 = max(x - w // 2, 0), max(y - h // 2, 0)
        x2, y2 = min(x + w // 2, frame.shape[1]), min(y + h // 2, frame.shape[0])
        if area < min_area:
            continue

        counts[label] += 1
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label_text = f"{label}"
        (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 4), (x1 + tw, y1), (0, 255, 0), -1)
        cv2.putText(frame, label_text, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    criollo_var.set(f"Criollo: {counts['Criollo']}")
    forastero_var.set(f"Forastero: {counts['Forastero']}")
    trinitario_var.set(f"Trinitario: {counts['Trinitario']}")

    total = sum(counts.values())
    current_time = time.time()

    if total == 0:
        detected_type_var.set("Detected: No beans")
        last_detected_class = None
    else:
        current_class = max(counts, key=counts.get)
        if (current_time - last_detection_time >= cooldown_time) and (current_class != last_detected_class):
            detected_type_var.set(f"Detected: {current_class}")
            last_detected_class = current_class
            last_detection_time = current_time
            if servo_queue:
                servo_queue.put(current_class)
        else:
            detected_type_var.set("Detected: Waiting")

    last_predicted_frame = frame

def update_frame():
    global last_pred_time, last_predicted_frame, camera_ready
    ret, frame = cap.read()
    if ret:
        if not camera_ready:
            camera_ready = True
            print("Camera ready.")

        if detection_active and time.time() - last_pred_time >= prediction_interval:
            threading.Thread(target=predict_and_update, args=(frame.copy(),), daemon=True).start()

        display = last_predicted_frame if last_predicted_frame is not None else frame
        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb).resize((640, 480), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        video_label.configure(image=img_tk)
        video_label.image = img_tk
    else:
        if not camera_ready:
            show_logo()

    root.after(30, update_frame)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def start_dashboard(queue):
    global servo_queue
    servo_queue = queue
    show_logo()
    update_frame()
    root.mainloop()
    cap.release()
    cv2.destroyAllWindows()
