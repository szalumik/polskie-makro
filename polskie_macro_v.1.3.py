import keyboard
import mouse
import time
import json
import tkinter as tk
from tkinter import filedialog, messagebox

class MacroRecorder:
    def __init__(self):
        self.events = []
        self.is_recording = False
        self.last_key_event = None
        self.pressed_buttons = set()

    def record(self):
        self.events = []
        self.is_recording = True
        self.last_key_event = None
        self.pressed_buttons.clear()
        keyboard.hook(self.on_event)
        mouse.hook(self.on_event)

    def stop_recording(self):
        self.is_recording = False
        keyboard.unhook_all()
        mouse.unhook_all()

    def on_event(self, event):
        if self.is_recording:
            event_time = time.time()
            if isinstance(event, keyboard.KeyboardEvent):
                if event.event_type == "down":
                    if self.last_key_event and self.last_key_event['event'] == event.name and (event_time - self.last_key_event['time'] < 0.1):
                        return
                    self.last_key_event = {'event': event.name, 'time': event_time}
                    self.events.append({'type': 'keyboard', 'event': event.name, 'time': event_time})
            elif isinstance(event, mouse.ButtonEvent):
                if event.event_type == "down":
                    self.pressed_buttons.add(event.button)
                elif event.event_type == "up":
                    self.pressed_buttons.discard(event.button)
                self.events.append({'type': 'mouse', 'event': event.button, 'action': event.event_type, 'time': event_time})

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.events, f)

    def load(self, filename):
        with open(filename, 'r') as f:
            self.events = json.load(f)

    def play(self):
        if not self.events:
            messagebox.showwarning("Błąd", "Brak nagranych makr!")
            return
        time.sleep(1.0)
        start_time = self.events[0]['time']
        last_event_time = start_time
        for event in self.events:
            time.sleep(max(0, (event['time'] - last_event_time) * 0.2))
            last_event_time = event['time']
            if event['type'] == 'keyboard':
                keyboard.press_and_release(event['event'])
            elif event['type'] == 'mouse':
                if event['event'] in ['left', 'right', 'middle']:
                    if event['action'] == 'down':
                        mouse.press(event['event'])
                    elif event['action'] == 'up':
                        mouse.release(event['event'])

class MacroApp:
    def __init__(self, root):
        self.recorder = MacroRecorder()
        self.root = root
        self.root.title("polskie makro")
        self.root.geometry("300x400")
        self.root.configure(bg="#010202")

        button_style = {
            "font": ("Arial", 12, "bold"),
            "bg": "#3D3D3D",
            "fg": "white",
            "width": 20,
            "height": 2,
            "bd": 3,
            "relief": "raised"
        }

        self.animation_ids = {}

        def animate_button(button, enlarge=True):
            if button in self.animation_ids:
                self.root.after_cancel(self.animation_ids[button])
            target_size = 14 if enlarge else 12
            step = 0.2 if enlarge else -0.2
            def smooth_resize(current_size):
                if (enlarge and current_size < target_size) or (not enlarge and current_size > target_size):
                    new_size = current_size + step
                    button.config(font=("Arial", int(new_size), "bold"))
                    self.animation_ids[button] = self.root.after(10, lambda: smooth_resize(new_size))
                else:
                    button.config(font=("Arial", target_size, "bold"))
                    if button in self.animation_ids:
                        del self.animation_ids[button]
            smooth_resize(12 if not enlarge else 12.2)

        def on_enter(e):
            animate_button(e.widget, True)
            e.widget.config(bg="#3D3D3D")

        def on_leave(e):
            animate_button(e.widget, False)
            e.widget.config(bg="#3D3D3D")

        self.record_btn = tk.Button(root, text="🔴 Nagrywaj", command=self.start_recording, **button_style)
        self.record_btn.pack(pady=10)
        self.record_btn.bind("<Enter>", on_enter)
        self.record_btn.bind("<Leave>", on_leave)

        self.stop_btn = tk.Button(root, text="⏹ Zatrzymaj", command=self.stop_recording, **button_style)
        self.stop_btn.pack(pady=10)
        self.stop_btn.bind("<Enter>", on_enter)
        self.stop_btn.bind("<Leave>", on_leave)

        self.save_btn = tk.Button(root, text="💾 Zapisz", command=self.save_macro, **button_style)
        self.save_btn.pack(pady=10)
        self.save_btn.bind("<Enter>", on_enter)
        self.save_btn.bind("<Leave>", on_leave)

        self.load_btn = tk.Button(root, text="📂 Wczytaj", command=self.load_macro, **button_style)
        self.load_btn.pack(pady=10)
        self.load_btn.bind("<Enter>", on_enter)
        self.load_btn.bind("<Leave>", on_leave)

        self.play_btn = tk.Button(root, text="▶️ Odtwórz", command=self.recorder.play, **button_style)
        self.play_btn.pack(pady=10)
        self.play_btn.bind("<Enter>", on_enter)
        self.play_btn.bind("<Leave>", on_leave)

    def start_recording(self):
        self.recorder.record()

    def stop_recording(self):
        self.recorder.stop_recording()
        messagebox.showinfo("Nagrywanie", "Nagrywanie zakończone.")

    def save_macro(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filename:
            self.recorder.save(filename)
            messagebox.showinfo("Zapisano", "Makro zapisane poprawnie.")

    def load_macro(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filename:
            self.recorder.load(filename)
            messagebox.showinfo("Wczytano", "Makro wczytane poprawnie.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroApp(root)
    root.mainloop()
