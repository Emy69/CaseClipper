import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "CaseClipper – Case Converter"
POLL_MS = 500  # Clipboard polling interval (ms)


def transform(text: str, mode: str) -> str:
    """Return *text* converted according to *mode*."""
    match mode:
        case "upper":
            return text.upper()
        case "lower":
            return text.lower()
        case "title":
            return text.title()
        case "sentence":
            sentences = [s.strip().capitalize() for s in text.split('.')]
            return '. '.join(filter(None, sentences))
        case "toggle":
            return ''.join(c.lower() if c.isupper() else c.upper() for c in text)
        case _:
            return text


class CaseClipperGUI(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("600x360")
        self.resizable(True, True)

        self.prev_clip: str | None = None  # Last clipboard content seen
        self.clip_mode = tk.BooleanVar(value=False)

        self._build_widgets()
        self._poll_clipboard()  # Start polling loop

    # ---------- GUI ---------- #
    def _build_widgets(self) -> None:
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        self.text = tk.Text(frame, wrap="word", height=10)
        self.text.pack(fill="both", expand=True)

        # Bottom bar
        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", pady=(8, 0))

        # Transformation buttons
        buttons = [
            ("UPPER", "upper"),
            ("lower", "lower"),
            ("Title", "title"),
            ("Sentence", "sentence"),
            ("tOGGLE", "toggle"),
        ]
        for label, mode in buttons:
            ttk.Button(
                bottom,
                text=label,
                command=lambda m=mode: self.apply(m),
            ).pack(side="left", padx=2)

        # Copy and clear
        ttk.Button(bottom, text="Copy", command=self.copy_to_clip).pack(
            side="left", padx=(20, 2)
        )
        ttk.Button(bottom, text="Clear", command=self._clear_text).pack(side="left")

        # Clipboard filter toggle
        ttk.Checkbutton(
            bottom,
            text="Clipboard auto-filter",
            variable=self.clip_mode,
        ).pack(side="right")

        # Word/char counter
        self.counter = ttk.Label(self, anchor="e")
        self.counter.pack(fill="x")
        self.text.bind("<KeyRelease>", lambda _: self._update_counter())
        self._update_counter()

    # ---------- Actions ---------- #
    def apply(self, mode: str) -> None:
        """Apply a case conversion to the selection or the whole text."""
        selection = self.text.tag_ranges("sel")
        if selection:  # Convert only the selected part
            start, end = selection
            part = self.text.get(start, end)
            self.text.delete(start, end)
            self.text.insert(start, transform(part, mode))
        else:  # Convert entire buffer
            content = self.text.get("1.0", "end-1c")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", transform(content, mode))
        self._update_counter()

    def copy_to_clip(self) -> None:
        """Copy current text buffer to the system clipboard."""
        data = self.text.get("1.0", "end-1c")
        if not data:
            messagebox.showinfo(APP_TITLE, "Nothing to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(data)
        messagebox.showinfo(APP_TITLE, "Copied to clipboard!")

    def _clear_text(self) -> None:
        self.text.delete("1.0", "end")
        self._update_counter()

    # ---------- Clipboard polling ---------- #
    def _poll_clipboard(self) -> None:
        try:
            current = self.clipboard_get()
        except tk.TclError:
            current = None

        if self.clip_mode.get() and current and current != self.prev_clip:
            converted = transform(current, "upper")  # Default mode
            self.clipboard_clear()
            self.clipboard_append(converted)
            self.prev_clip = converted
        else:
            self.prev_clip = current

        self.after(POLL_MS, self._poll_clipboard)

    # ---------- Helpers ---------- #
    def _update_counter(self) -> None:
        text = self.text.get("1.0", "end-1c")
        words = len(text.split())
        chars = len(text)
        self.counter.config(text=f"{words} words · {chars} characters")


if __name__ == "__main__":
    CaseClipperGUI().mainloop()
