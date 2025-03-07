import keyboard
import mouse
import time
import json
import tkinter as tk
from tkinter import filedialog

class MacroRecorder:
    def __init__(self):
        self.events = []
        self.is_recording = False
        self.last_key_event = None

    def record(self):
        if self.is_recording:
            return
        self.events = []
        self.is_recording = True
        self.last_key_event = None
        keyboard.hook(self.on_event)
        mouse.hook(self.on_event)

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        keyboard.unhook_all()
        mouse.unhook_all()

    def on_event(self, event):
        if self.is_recording:
            event_time = time.time()
            try:
                if isinstance(event, keyboard.KeyboardEvent):
                    if event.event_type == "down":
                        if self.last_key_event and self.last_key_event['event'] == event.name and (event_time - self.last_key_event['time'] < 0.1):
                            return
                        self.last_key_event = {'event': event.name, 'time': event_time}
                        self.events.append({'type': 'keyboard', 'event': event.name, 'time': event_time})
                elif isinstance(event, mouse.ButtonEvent):
                    self.events.append({'type': 'mouse', 'event': event.button, 'action': event.event_type, 'time': event_time})
            except Exception as e:
                print(f"Błąd podczas rejestrowania zdarzenia: {e}")

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.events, f)

    def load(self, filename):
        with open(filename, 'r') as f:
            self.events = json.load(f)

    def play(self, speed=1.0):
        if not self.events:
            return
        time.sleep(1.0)
        start_time = self.events[0]['time']
        last_event_time = start_time
        for event in self.events:
            time.sleep(max(0, (event['time'] - last_event_time) / speed))
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
        self.root.geometry("300x430")
        self.current_theme = "dark"
        self.animation_ids = {}
        self.buttons = []
        self.is_recording = False
        self.button_color = {}
        self.hover_color = {}

        self.status_label = tk.Label(root, text="", font=("Arial", 10), fg="white", bg="#010202")
        self.status_label.pack()

        button_style = {
            "font": ("Arial", 12, "bold"),
            "width": 20,
            "height": 2,
            "bd": 3,
            "relief": "raised"
        }

        self.theme_colors = {
            "dark": ("#010202", "#3D3D3D"),
            "white": ("white", "#CCCCCC"),
            "rainbow": ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082"]
        }

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
            e.widget.config(bg=self.hover_color.get(e.widget, "#555"))

        def on_leave(e):
            animate_button(e.widget, False)
            if e.widget != self.buttons[0] or not self.is_recording:
                e.widget.config(bg=self.button_color.get(e.widget, "#3D3D3D"))

        for i, (text, command) in enumerate([("🔴 Nagrywaj", self.start_recording),
                                             ("⏹ Zatrzymaj", self.stop_recording),
                                             ("💾 Zapisz", self.save_macro),
                                             ("📂 Wczytaj", self.load_macro),
                                             ("▶️ Odtwórz", self.play_macro),
                                             ("🌈 Zmień kolor", self.change_theme)]):
            btn = tk.Button(root, text=text, command=command, **button_style)
            btn.pack(pady=5)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            self.buttons.append(btn)

        self.set_theme(self.current_theme)

    def start_recording(self):
        self.status_label.config(text="Nagrywanie w toku...")
        self.is_recording = True
        self.buttons[0].config(bg="red")

        self.recorder.record()

    def stop_recording(self):
        self.status_label.config(text="Nagrywanie zatrzymane.")
        self.is_recording = False
        self.set_theme(self.current_theme)
        self.recorder.stop_recording()

    def save_macro(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filename:
            self.recorder.save(filename)

    def load_macro(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filename:
            self.recorder.load(filename)

    def play_macro(self):
        self.recorder.play()

    def change_theme(self):
        themes = list(self.theme_colors.keys())
        self.current_theme = themes[(themes.index(self.current_theme) + 1) % len(themes)]
        self.set_theme(self.current_theme)
        self.status_label.config(text=f"Zmieniono na tryb {self.current_theme}")

    def set_theme(self, theme):
        self.root.configure(bg=self.theme_colors[theme][0])
        for i, btn in enumerate(self.buttons):
            color = self.theme_colors[theme][1] if theme != "rainbow" else self.theme_colors[theme][i % len(self.theme_colors[theme])]
            self.button_color[btn] = color
            self.hover_color[btn] = "#777" if theme != "rainbow" else color
            btn.config(bg=color, fg="black" if theme == "white" else "white")

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroApp(root)
    root.mainloop()
