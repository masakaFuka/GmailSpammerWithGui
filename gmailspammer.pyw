import smtplib
import time
import threading
import random
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel, BooleanVar, StringVar
from email.header import Header
from email.mime.text import MIMEText
import json

SETTINGS_FILE = "settings.txt"

class EmailSpammerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Gmail Spammer by Fuka")
        self.spamming = False
        self.stop_event = threading.Event()
        self.settings = self.load_settings()

        tk.Label(master, text="Your Gmail: ").grid(row=0, column=0)
        tk.Label(master, text="App Password: ").grid(row=1, column=0)
        tk.Label(master, text="Target Email: ").grid(row=2, column=0)
        tk.Label(master, text="Delay (Sec): ").grid(row=3, column=0)

        self.sender_entry = tk.Entry(master, width=30)
        self.sender_entry.insert(0, self.settings["gmail"])
        self.sender_entry.grid(row=0, column=1)

        self.password_entry = tk.Entry(master, show="*", width=30)
        self.password_entry.insert(0, self.settings["app_password"])
        self.password_entry.grid(row=1, column=1)

        self.recipient_entry = tk.Entry(master, width=30)
        self.recipient_entry.insert(0, self.settings["recipient"])
        self.recipient_entry.grid(row=2, column=1)

        self.interval_entry = tk.Entry(master, width=10)
        self.interval_entry.insert(0, str(self.settings["interval"]))
        self.interval_entry.grid(row=3, column=1)

        self.start_button = tk.Button(master, text="Start Spam", command=self.start_spamming)
        self.start_button.grid(row=4, column=0, pady=1)

        self.stop_button = tk.Button(master, text="Stop Spam", command=self.stop_spamming)
        self.stop_button.grid(row=4, column=2, pady=1)

        self.settings_button = tk.Button(master, text="Settings", command=self.open_settings)
        self.settings_button.grid(row=4, column=1, padx=1)

        self.log_box = scrolledtext.ScrolledText(master, width=60, height=15, state='disabled')
        self.log_box.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        self.sender_entry.bind("<KeyRelease>", self.update_setting("gmail"))
        self.password_entry.bind("<KeyRelease>", self.update_setting("app_password"))
        self.recipient_entry.bind("<KeyRelease>", self.update_setting("recipient"))
        self.interval_entry.bind("<KeyRelease>", self.update_setting("interval_float"))

    def update_setting(self, key):
        def updater(event):
            if key == "interval_float":
                try:
                    self.settings["interval"] = float(self.interval_entry.get())
                except:
                    pass
            else:
                self.settings[key] = event.widget.get()
            self.save_settings()
        return updater

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            default = {
                "gmail": "",
                "app_password": "",
                "recipient": "",
                "interval": 1.0,
                "title": "Made by masakaFuka",
                "use_random_number": True,
                "message_body": "type any content here"
            }
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4)
            return default

    def save_settings(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)

    def log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')

    def start_spamming(self):
        self.stop_event.clear()
        self.spamming = True
        self.log("🚀 Starting Spam...")
        threading.Thread(target=self.spam_loop, daemon=True).start()

    def stop_spamming(self):
        self.spamming = False
        self.stop_event.set()
        self.log("🛑 Stopped Spam")

    def spam_loop(self):
        me = self.settings["gmail"]
        password = self.settings["app_password"]
        recipient = self.settings["recipient"]
        interval = self.settings["interval"]

        while not self.stop_event.is_set():
            subject = self.settings["title"]
            if self.settings["use_random_number"]:
                subject += " " + str(random.randint(1000, 9999))

            msg = MIMEText(self.settings["message_body"], 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = me
            msg['To'] = recipient

            try:
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(me, password)
                s.sendmail(me, [recipient], msg.as_string())
                s.quit()
                self.log(f"✅ Successfully {recipient} | Subject: {subject}")
            except Exception as e:
                self.log(f"❌ Failure {e}")

            if self.stop_event.wait(interval):
                break

    def open_settings(self):
        settings_window = Toplevel(self.master)
        settings_window.title("⚙️ Settings")

        tk.Label(settings_window, text="Title：").grid(row=0, column=0)
        title_entry = tk.Entry(settings_window, width=40)
        title_entry.insert(0, self.settings["title"])
        title_entry.grid(row=0, column=1)

        random_var = BooleanVar(value=self.settings["use_random_number"])
        random_check = tk.Checkbutton(settings_window, text="Randomize Number", variable=random_var)
        random_check.grid(row=1, column=0, columnspan=2)

        tk.Label(settings_window, text="Contents：").grid(row=2, column=0, sticky='n')
        content_text = scrolledtext.ScrolledText(settings_window, width=50, height=10)
        content_text.insert(tk.END, self.settings["message_body"])
        content_text.grid(row=2, column=1)

        def save_changes():
            self.settings["title"] = title_entry.get()
            self.settings["use_random_number"] = random_var.get()
            self.settings["message_body"] = content_text.get("1.0", tk.END).strip()
            self.save_settings()
            self.log("⚙️ Setings updated")
            settings_window.destroy()

        settings_window.protocol("WM_DELETE_WINDOW", save_changes)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailSpammerGUI(root)
    root.mainloop()
