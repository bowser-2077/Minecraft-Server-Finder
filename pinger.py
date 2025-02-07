import random
import subprocess
import threading
import tkinter as tk
from mcstatus import MinecraftServer
import os
from PIL import Image, ImageTk

SERVERS_FILE = "ValidServers.txt"  # Saved valid server files
THREAD_COUNT = 1  # Concurent thread
SCAN_RUNNING = False  # Scan state

# Cmd hider 2000
def hide_console():
    if os.name == "nt":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Ip generator 2000
def generate_valid_ip():
    first_octet = random.choice(range(1, 223))
    while any(lower <= first_octet <= upper for lower, upper in [(10, 10), (127, 127), (169, 172), (192, 192), (224, 255)]):
        first_octet = random.choice(range(1, 223))
    
    return f"{first_octet}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

# Ip verfier
def ping(ip):
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # Cache la fenêtre CMD
        
        output = subprocess.run(["ping", "-n", "1", "-w", "500", ip], capture_output=True, text=True, startupinfo=startupinfo)
        return "TTL=" in output.stdout
    except:
        return False

# Get MOTD of server if valid server
def check_minecraft(ip, port=25565):
    try:
        server = MinecraftServer.lookup(f"{ip}:{port}")
        status = server.status()
        return status.motd
    except:
        return None

# Server save
def save_server(ip, motd):
    with open(SERVERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ip} - {motd}\n")

# Thread management
def scan():
    while SCAN_RUNNING:
        ip = generate_valid_ip()
        result_text.set(f"Scanning the following ip : {ip}")

        if ping(ip):
            motd = check_minecraft(ip)
            if motd:
                log_text.insert(tk.END, f"[+] {ip}: SERVER FOUND! MOTD : {motd}\n", "green")
                save_server(ip, motd)  # Enregistre le serveur dans le fichier
            else:
                log_text.insert(tk.END, f"[-] {ip}: Server found, but its not a minecraft server...\n", "red")
        else:
            log_text.insert(tk.END, f"[-] {ip}: No response from server...\n", "gray")

        log_text.see(tk.END)

# Start scan function
def start_scan():
    global SCAN_RUNNING
    SCAN_RUNNING = True
    start_stop_button.config(text="Stop Scan", command=stop_scan)  # Change le texte et l'action du bouton
    for _ in range(THREAD_COUNT):
        threading.Thread(target=scan, daemon=True).start()

# Stop scan function
def stop_scan():
    global SCAN_RUNNING
    SCAN_RUNNING = False
    start_stop_button.config(text="Start Scan", command=start_scan)  # Change le texte et l'action du bouton

# Config window
def open_config():
    config_window = tk.Toplevel(root)
    config_window.title("Config Interface")
    config_window.geometry("600x400")

    # Thread box
    thread_label = tk.Label(config_window, text="Threads amount :", font=("Arial", 12))
    thread_label.pack(pady=10)

    thread_entry = tk.Entry(config_window, font=("Arial", 12), width=10)
    thread_entry.insert(tk.END, str(THREAD_COUNT))
    thread_entry.pack(pady=5)

    # Save button
    def save_and_reload():
        global THREAD_COUNT
        THREAD_COUNT = int(thread_entry.get())  
        save_config(THREAD_COUNT)  
        config_window.destroy()  
        stop_scan()  
        start_scan() 

    save_button = tk.Button(config_window, text="Save and relaunch scan", command=save_and_reload, font=("Arial", 12))
    save_button.pack(pady=10)

# Reload config
def load_config():
    config_file_path = os.path.join(os.getenv("TEMP"), "MSFconfig.txt")
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as f:
            global THREAD_COUNT
            THREAD_COUNT = int(f.read().strip())  # Lire la valeur du fichier et la convertir en entier

# Save in file (In %temp% folder (MSFconfig.txt) )
def save_config(thread_count):
    config_file_path = os.path.join(os.getenv("TEMP"), "MSFconfig.txt")
    with open(config_file_path, "w") as f:
        f.write(str(thread_count))

# Load config I think
load_config()

# GUI
root = tk.Tk()
root.title("Minecraft Server Finder (MSFV1) [Free edition]")
root.geometry("1920x1080")
root.resizable(True, True)

# cmd frame
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# background
if os.path.exists("background.jpg"):
    img = Image.open("background.jpg").resize((1920, 1080))
    bg = ImageTk.PhotoImage(img)
    label_bg = tk.Label(frame, image=bg)
    label_bg.place(x=0, y=0, relwidth=1, relheight=1)
else:
    frame.configure(bg="black")  # Met un fond noir si l'image est absente

# nothing
result_text = tk.StringVar()
result_label = tk.Label(frame, textvariable=result_text, font=("Arial", 14), fg="white", bg="black")
result_label.pack()

# logs console
log_text = tk.Text(frame, wrap=tk.WORD, height=15, width=70, bg="black", fg="white")
log_text.tag_config("green", foreground="green")
log_text.tag_config("red", foreground="red")
log_text.tag_config("gray", foreground="gray")
log_text.pack()

# Config button
config_icon = ImageTk.PhotoImage(file="config.ico")  # icon
config_button = tk.Button(frame, text="Config", command=open_config, font=("Arial", 14), fg="white", bg="blue", image=config_icon, compound="left")
config_button.image = config_icon  
config_button.place(x=10, y=10) 

# Start/Stop button
start_stop_button = tk.Button(frame, text="Start Scan", command=start_scan, font=("Arial", 14), fg="white", bg="green")
start_stop_button.pack(pady=20)

# idk it was on stack overflow...
start_scan()

# hide
if os.name == "nt":
    hide_console()

# just to launch
root.mainloop()
