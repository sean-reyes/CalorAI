import json
import queue
import threading
import tkinter as tk
from tkinter import ttk
import urllib.error
import urllib.request


class AIAssistant:
    def __init__(self, root, api_key, context_provider):
        self.root = root
        self.api_key = api_key
        self.context_provider = context_provider
        self.history = []
        self.request_pending = False
        self.active_request_id = 0
        self.response_queue = queue.Queue()
        self.window = None
        self.transcript = None
        self.status_label = None
        self.send_button = None

    def show(self):
        assistant_window = tk.Toplevel(self.root)
        assistant_window.title("CalorAI AI assistant")
        assistant_window.geometry("720x640")
        assistant_window.minsize(560, 480)
        assistant_window.configure(bg='#514d78')
        assistant_window.transient(self.root)
        assistant_window.protocol("WM_DELETE_WINDOW", self.close)
        self.window = assistant_window

        style = ttk.Style(assistant_window)
        style.theme_use('clam')
        style.configure('CalorAIFrame.TFrame', background='#252735')
        style.configure('CalorAIButton.TButton', background='#a8e760', foreground='#292a36',
                        font=('Segoe UI Variable Text', 10, 'bold'), padding=(12, 8))
        style.map('CalorAIButton.TButton', background=[('active', '#b9f178')],
              foreground=[('active', '#292a36')])

        frame = ttk.Frame(assistant_window, padding=24, style='CalorAIFrame.TFrame')
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="CalorAI assistant", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            frame,
            text="Your selected meals and nutrition totals are sent to Gemini.",
            wraplength=560,
            foreground='#b0b2c1',
        ).pack(anchor="w", pady=(0, 10))

        conversation_frame = ttk.Frame(frame)
        conversation_frame.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(conversation_frame)
        scrollbar.pack(side="right", fill="y")
        transcript = tk.Text(
            conversation_frame,
            height=18,
            width=64,
            wrap="word",
            state="disabled",
            background='#20222e',
            foreground='#f3f2f8',
            insertbackground='#f3f2f8',
            selectbackground='#bd9cf2',
            selectforeground='#292a36',
            relief='flat',
            borderwidth=0,
            yscrollcommand=scrollbar.set,
        )
        transcript.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=transcript.yview)
        self.transcript = transcript

        for item in self.history:
            speaker = "You" if item["role"] == "user" else "Gemini"
            self._append_message(
                transcript,
                speaker,
                item.get("display", item["parts"][0]["text"]),
            )

        status_label = ttk.Label(frame, text="Ready")
        status_label.pack(anchor="w", pady=(8, 4))
        self.status_label = status_label

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x")
        prompt_entry = ttk.Entry(input_frame)
        prompt_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        send_button = ttk.Button(
            input_frame,
            text="Send",
            command=lambda: self.send_message(
                prompt_entry, send_button, status_label, transcript, assistant_window
            ),
        )
        send_button.pack(side="left")
        self.send_button = send_button
        if self.request_pending:
            send_button.configure(state="disabled")
            status_label.configure(text="Gemini is preparing a recommendation...")
        prompt_entry.bind(
            "<Return>",
            lambda event: (send_button.invoke(), "break")[1],
        )
        ttk.Button(frame, text="Close", command=self.close).pack(
            anchor="e", pady=(8, 0)
        )

    def close(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.destroy()
        self.window = None
        self.transcript = None
        self.status_label = None
        self.send_button = None

    @staticmethod
    def _append_message(transcript, speaker, message):
        transcript.configure(state="normal")
        transcript.insert(tk.END, f"{speaker}:\n{message}\n\n")
        transcript.configure(state="disabled")
        transcript.see(tk.END)

    def send_message(self, prompt_entry, send_button, status_label, transcript, window):
        prompt = prompt_entry.get().strip()
        if not prompt:
            return
        if self.request_pending:
            status_label.config(text="Please wait for the current reply.")
            return

        if not self.api_key:
            status_label.config(text="Set the API Key environment variable to use AI assistant.")
            return

        self.active_request_id += 1
        request_id = self.active_request_id
        context = self.context_provider()
        system_instruction = (
            "You are a practical meal-planning assistant. Use the calorie limit, remaining calories, "
            "selected meals, and menu nutrition data below when making recommendations. Prefer foods "
            "from the available menu and do not claim a meal fits the remaining budget if its listed "
            "calories exceed it. If calories are already over the limit, say so plainly. Give concise, "
            "general food suggestions and do not present them as medical advice.\n\n"
            f"Current meal-planner data:\n{json.dumps(context, ensure_ascii=False)}"
        )
        user_entry = {
            "role": "user",
            "parts": [{"text": prompt}],
            "display": prompt,
        }
        self.history.append(user_entry)
        contents = [
            {"role": item["role"], "parts": item["parts"]}
            for item in self.history
        ]

        prompt_entry.delete(0, tk.END)
        self._append_message(transcript, "You", prompt)
        send_button.configure(state="disabled")
        status_label.configure(text="Please wait...")
        self.request_pending = True

        def request_recommendation():
            try:
                endpoint = (
                    "https://generativelanguage.googleapis.com/v1beta/"
                    "models/gemini-3.8-flash:generateContent"
                )
                body = {
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "contents": contents,
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 700},
                }
                request = urllib.request.Request(
                    endpoint,
                    data=json.dumps(body).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.api_key,
                    },
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=20) as response:
                    result = json.loads(response.read().decode("utf-8"))
                parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                answer = "\n".join(part.get("text", "") for part in parts).strip()
                if not answer:
                    raise ValueError("Gemini returned no text. Try asking a different question.")
                self.response_queue.put((request_id, answer, None))
            except urllib.error.HTTPError as error:
                try:
                    error_body = json.loads(error.read().decode("utf-8"))
                    message = error_body.get("error", {}).get("message", str(error))
                except Exception:
                    message = str(error)
                self.response_queue.put(
                    (request_id, None, f"Gemini API error: {message}")
                )
            except Exception as error:
                self.response_queue.put(
                    (request_id, None, f"Gemini request failed: {error}")
                )

        self.root.after(
            100,
            self._poll_for_response,
            request_id,
            user_entry,
            window,
        )
        self.root.after(
            30000,
            self._timeout_request,
            request_id,
            user_entry,
            window,
        )
        threading.Thread(target=request_recommendation, daemon=True).start()

    def _poll_for_response(self, request_id, user_entry, request_window):
        try:
            response_id, answer, error = self.response_queue.get_nowait()
        except queue.Empty:
            if self.request_pending and request_id == self.active_request_id:
                self.root.after(
                    100,
                    self._poll_for_response,
                    request_id,
                    user_entry,
                    request_window,
                )
            return

        if response_id != request_id:
            if self.request_pending and request_id == self.active_request_id:
                self.root.after(
                    100,
                    self._poll_for_response,
                    request_id,
                    user_entry,
                    request_window,
                )
            return
        self._finish_request(request_id, answer, error, user_entry, request_window)

    def _timeout_request(self, request_id, user_entry, request_window):
        if self.request_pending and request_id == self.active_request_id:
            self._finish_request(
                request_id,
                None,
                "Gemini timed out after 30 seconds. Check your connection and API key, then retry.",
                user_entry,
                request_window,
            )

    def _finish_request(self, request_id, answer, error, user_entry, request_window):
        if request_id != self.active_request_id or not self.request_pending:
            return
        self.request_pending = False
        if error:
            if self.history and self.history[-1] is user_entry:
                self.history.pop()
        else:
            self.history.append({
                "role": "model",
                "parts": [{"text": answer}],
                "display": answer,
            })

        current_window = self.window
        if current_window is None or not current_window.winfo_exists():
            return
        if self.send_button is not None and self.send_button.winfo_exists():
            self.send_button.configure(state="normal")
        if current_window is request_window:
            if error:
                self._append_message(self.transcript, "Assistant", error)
                self.status_label.configure(text="Request failed.")
            else:
                self._append_message(self.transcript, "Gemini", answer)
                self.status_label.configure(text="Ready")
