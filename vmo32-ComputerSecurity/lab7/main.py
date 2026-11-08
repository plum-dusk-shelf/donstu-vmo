from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from key_processor import KeyProcessor
from storage import UserStorage

APP_DIR = Path(__file__).resolve().parent
USERS_FILE = APP_DIR / "users.enc"
KEY_FILE = APP_DIR / "secret.key"


class PatternLockCanvas(tk.Frame):
    def __init__(self, master, processor: KeyProcessor, size: int = 330):
        super().__init__(master)
        self.processor = processor
        self.size = size
        self.margin = 45
        self.node_radius = 18
        self.hit_radius = 26
        self.spacing = (size - 2 * self.margin) // (processor.grid_size - 1)

        self.canvas = tk.Canvas(self, width=size, height=size, bg="white", highlightthickness=0)
        self.canvas.pack()

        self.node_centers = self._build_node_centers()
        self.pattern: list[int] = []
        self.visited: set[int] = set()
        self.preview_line_id: int | None = None

        self._draw_static_nodes()

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    def _build_node_centers(self) -> dict[int, tuple[int, int]]:
        centers = {}
        for idx in range(self.processor.total_nodes):
            r, c = self.processor.node_to_rc(idx)
            x = self.margin + c * self.spacing
            y = self.margin + r * self.spacing
            centers[idx] = (x, y)
        return centers

    def _draw_static_nodes(self):
        self.canvas.delete("all")
        for idx, (x, y) in self.node_centers.items():
            fill = "#2b8cff" if idx in self.visited else "white"
            outline = "#2b8cff" if idx in self.visited else "#909090"
            self.canvas.create_oval(
                x - self.node_radius,
                y - self.node_radius,
                x + self.node_radius,
                y + self.node_radius,
                fill=fill,
                outline=outline,
                width=3,
            )

        for i in range(1, len(self.pattern)):
            n1, n2 = self.pattern[i - 1], self.pattern[i]
            x1, y1 = self.node_centers[n1]
            x2, y2 = self.node_centers[n2]
            self.canvas.create_line(x1, y1, x2, y2, fill="#2b8cff", width=5, capstyle=tk.ROUND)

    def _node_at(self, x: int, y: int) -> int | None:
        for node, (nx, ny) in self.node_centers.items():
            if (x - nx) ** 2 + (y - ny) ** 2 <= self.hit_radius ** 2:
                return node
        return None

    def _append_node(self, node: int):
        if node in self.visited:
            return
        if not self.pattern:
            self.pattern.append(node)
            self.visited.add(node)
        else:
            last = self.pattern[-1]
            additions = self.processor.expanded_transition(last, node, self.visited)
            for nxt in additions:
                self.pattern.append(nxt)
                self.visited.add(nxt)
        self._draw_static_nodes()

    def _update_preview_line(self, x: int, y: int):
        if not self.pattern:
            return
        x1, y1 = self.node_centers[self.pattern[-1]]
        if self.preview_line_id is not None:
            self.canvas.delete(self.preview_line_id)
        self.preview_line_id = self.canvas.create_line(
            x1,
            y1,
            x,
            y,
            fill="#7db6ff",
            width=3,
            dash=(4, 2),
        )

    def _on_press(self, event):
        node = self._node_at(event.x, event.y)
        if node is not None:
            self._append_node(node)

    def _on_drag(self, event):
        node = self._node_at(event.x, event.y)
        if node is not None:
            self._append_node(node)
        self._update_preview_line(event.x, event.y)

    def _on_release(self, _event):
        if self.preview_line_id is not None:
            self.canvas.delete(self.preview_line_id)
            self.preview_line_id = None

    def clear(self):
        self.pattern = []
        self.visited = set()
        self.preview_line_id = None
        self._draw_static_nodes()

    def get_pattern(self) -> list[int]:
        return list(self.pattern)


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Графический ключ")
        self.processor = KeyProcessor()
        self.storage = UserStorage(USERS_FILE, KEY_FILE)
        self.users = self.storage.load_users()

        self.attempts_left = 3
        self.login_threshold = 0.80

        self.name_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="register")

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(padx=12, pady=8, fill="x")

        tk.Label(top, text="Имя пользователя:").pack(side="left")
        tk.Entry(top, textvariable=self.name_var, width=24).pack(side="left", padx=8)

        tk.Radiobutton(top, text="Регистрация", variable=self.mode_var, value="register", command=self._on_mode_change).pack(side="left")
        tk.Radiobutton(top, text="Вход", variable=self.mode_var, value="login", command=self._on_mode_change).pack(side="left")

        self.canvas_widget = PatternLockCanvas(self.root, self.processor)
        self.canvas_widget.pack(padx=12, pady=8)

        controls = tk.Frame(self.root)
        controls.pack(padx=12, pady=6, fill="x")

        self.action_button = tk.Button(controls, text="Сохранить", command=self._on_action)
        self.action_button.pack(side="left")

        tk.Button(controls, text="Очистить", command=self.canvas_widget.clear).pack(side="left", padx=8)

        self.attempts_label = tk.Label(self.root, text="")
        self.attempts_label.pack(pady=(0, 10))
        self._refresh_attempts()

    def _on_mode_change(self):
        if self.mode_var.get() == "register":
            self.action_button.config(text="Сохранить")
        else:
            self.action_button.config(text="Проверить")
        self.attempts_left = 3
        self._refresh_attempts()

    def _refresh_attempts(self):
        if self.mode_var.get() == "login":
            self.attempts_label.config(text=f"Осталось попыток: {self.attempts_left}")
        else:
            self.attempts_label.config(text="")

    def _on_action(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите имя пользователя")
            return

        pattern = self.canvas_widget.get_pattern()
        if not self.processor.enough_points(pattern):
            messagebox.showerror("Ошибка", "Соедините минимум 4 точки")
            return

        if self.mode_var.get() == "register":
            self._register(name, pattern)
        else:
            self._login(name, pattern)

    def _register(self, name: str, pattern: list[int]):
        payload = {
            "type": "pattern_lock",
            "fingerprint": self.processor.fingerprint(pattern),
            "pattern": pattern,
        }
        self.users[name] = json.dumps(payload, separators=(",", ":"))
        self.storage.save_users(self.users)
        messagebox.showinfo("Успех", f"Пользователь '{name}' сохранён")
        self.canvas_widget.clear()

    def _login(self, name: str, pattern: list[int]):
        if name not in self.users:
            messagebox.showerror("Ошибка", "Пользователь не найден")
            return

        stored_payload = json.loads(self.users[name])

        if stored_payload.get("type") != "pattern_lock":
            messagebox.showerror("Ошибка", "Старый формат ключа. Зарегистрируйте пользователя заново")
            return

        stored_pattern = stored_payload["pattern"]
        stored_fingerprint = stored_payload["fingerprint"]

        exact_ok = self.processor.fingerprint(pattern) == stored_fingerprint
        similarity = self.processor.similarity(pattern, stored_pattern)
        fuzzy_ok = similarity >= self.login_threshold

        if exact_ok or fuzzy_ok:
            messagebox.showinfo("Вход выполнен", f"Доступ разрешён (похожесть: {similarity:.0%})")
            self.attempts_left = 3
            self.canvas_widget.clear()
            self._refresh_attempts()
            return

        self.attempts_left -= 1
        if self.attempts_left <= 0:
            messagebox.showerror("Доступ запрещён", "Попытки закончились")
            self.attempts_left = 3
        else:
            messagebox.showwarning("Неверный ключ", f"Ключ не совпал. Похожесть: {similarity:.0%}")
        self._refresh_attempts()


def main():
    root = tk.Tk()
    App(root)
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
