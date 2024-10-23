import os
import tkinter as tk
from pathlib import Path
from threading import Thread
from time import sleep

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


def get_resource_path(audio_file: Path) -> Path:
    current_file_path = Path(__file__)
    project_root = current_file_path.parent
    return project_root / "data" / "audio" / audio_file


class TextToAudio:
    def __init__(self):
        pass

    def convert(self, text: str) -> AudioSegment:
        tts = gTTS(text, lang="pl")
        tts.save("tmp.mp3")
        audio = AudioSegment.from_mp3("tmp.mp3")
        os.remove("tmp.mp3")
        return audio


class Question:
    text: str
    audio: AudioSegment

    def __init__(self, text: str, audio: AudioSegment):
        self.text = text
        self.audio = audio


class Answer:
    text: str
    correct: bool


class App:
    answers: list[Answer]
    questions: list[Question]
    current_position: int

    correct: int
    wrong: int

    time_start: float
    time_taken: float

    _window: tk.Tk
    _question_button: tk.Button
    _user_input: tk.Text
    _next_question_button: tk.Button
    _correct_label: tk.Label
    _wrong_label: tk.Label

    def __init__(self):
        self.correct = 0
        self.wrong = 0
        self.current_position = 0

        tta = TextToAudio()

        self.questions = []
        if os.path.exists("questions/questions.txt"):
            with open("questions/questions.txt", "r") as f:
                for line in f:
                    text = line.strip()
                    audio = tta.convert(text)
                    self.questions.append(Question(text, audio))

        self.answers = []
        if os.path.exists("answers/answers.txt"):
            with open("answers/answers.txt", "r") as f:
                for line in f:
                    answer = Answer()
                    answer.text, answer.correct = line.strip().split(",")
                    if answer.correct == "True":
                        answer.correct = True
                        self.correct += 1
                    elif answer.correct == "False":
                        answer.correct = False
                        self.wrong += 1
                    self.answers.append(answer)
                    self.current_position += 1

        self.time_start = 0.0
        self.time_taken = 0.0

        self._replay_last_button = None
        self._info_label = None
        self._previous_answer = None
        self._next_answer = None

        self._window = tk.Tk()
        self._window.geometry("800x200")
        self._window.resizable(False, False)
        self._window.attributes("-type", "dialog")
        self._window.title("Dyktadno")
        self._window.configure(bg="black")
        self._window.grid_columnconfigure(0, weight=1)
        self._window.grid_columnconfigure(1, weight=1)
        self._window.grid_columnconfigure(2, weight=1)

        self._question_button = tk.Button(self._window, text="Play question")
        self._question_button.configure(background="black", foreground="white")
        self._question_button.configure(
            activebackground="black", activeforeground="white"
        )
        self._question_button.bind("<ButtonPress>", self.play_question)
        self._window.bind("<KeyPress>", self.key_pressed)
        self._question_button.grid(row=0, column=1, columnspan=3)

        self._user_input = tk.Text(self._window, font=("Helvetica", 20), height=2)
        self._user_input.configure(background="black", foreground="white")
        self._user_input.grid(row=1, column=1, columnspan=3)

        self._correct_label = tk.Label(
            self._window,
            text=f"Correct: {self.correct}",
            font=("Helvetica", 20),
        )
        self._correct_label.configure(background="black", foreground="white")
        self._correct_label.grid(row=2, column=1, columnspan=3)

        self._wrong_label = tk.Label(
            self._window,
            text=f"Wrong: {self.wrong}",
            font=("Helvetica", 20),
        )
        self._wrong_label.configure(background="black", foreground="white")
        self._wrong_label.grid(row=3, column=1, columnspan=3)

        self._next_question_button = tk.Button(self._window, text="Next question")
        self._next_question_button.configure(background="black", foreground="white")
        self._next_question_button.configure(
            activebackground="black", activeforeground="white"
        )
        self._next_question_button.bind("<ButtonPress>", self.next_question)
        self._next_question_button.grid(row=4, column=2, columnspan=3)

        self._next_question_button["state"] = "disabled"

        self._check_button = tk.Button(self._window, text="Check answer")
        self._check_button.configure(background="black", foreground="white")
        self._check_button.configure(
            activebackground="black", activeforeground="white"
        )
        self._check_button.bind("<ButtonPress>", self.check_answer)
        self._check_button.grid(row=4, column=0, columnspan=3)

        if self.current_position >= len(self.questions):
            self.finish_popup()

    def key_pressed(self, event):
        if event.keysym == "Return":
            self.check_answer()

    def play_question(self, event=None):
        if self._question_button.config("state")[-1] == "disabled":
            return
        Thread(target=play, args=(self.questions[self.current_position].audio,)).start()

    def check_answer(self, event=None):
        if self._check_button.config("state")[-1] == "disabled":
            return
        user_answer = self._user_input.get("1.0", "end").strip()
        if user_answer == "":
            return
        self._next_question_button["state"] = "normal"
        self._user_input["state"] = "disabled"
        self._check_button["state"] = "disabled"
        self.answers.append(Answer())
        self.answers[self.current_position].text = user_answer
        if user_answer == self.questions[self.current_position].text:
            self.correct += 1
            self.answers[self.current_position].correct = True
            self._correct_label["text"] = f"Correct: {self.correct}"
            song = AudioSegment.from_mp3(get_resource_path("correct.mp3"))
        else:
            self.wrong += 1
            self.answers[self.current_position].correct = False
            self._wrong_label["text"] = f"Wrong: {self.wrong}"
            song = AudioSegment.from_mp3(get_resource_path("incorrect.mp3"))
        Thread(target=play, args=(song,)).start()

        with open("answers/answers.txt", "w") as f:
            for answer in self.answers:
                f.write(f"{answer.text},{answer.correct}\n")

        if self.current_position >= len(self.questions) - 1:
            self.finish_popup()

    def finish_popup(self):
        self._next_question_button["state"] = "disabled"
        self._user_input["state"] = "disabled"
        self._question_button["state"] = "disabled"
        self._check_button["state"] = "disabled"
        popup = tk.Toplevel(self._window)
        popup.title("Finished")
        popup.geometry("300x150")
        popup.configure(bg="black")
        popup.resizable(False, False)
        popup.attributes("-type", "dialog")
        popup.attributes("-topmost", True)
        popup.grid_columnconfigure(0, weight=1)

        congrats_label = tk.Label(
            popup,
            text="Congratulations!",
            font=("Helvetica", 20),
        )
        congrats_label.configure(background="black", foreground="white")
        congrats_label.grid(row=0, column=0)

        correct_label = tk.Label(
            popup,
            text=f"Correct: {self.correct}",
            font=("Helvetica", 20),
        )
        correct_label.configure(background="black", foreground="white")
        correct_label.grid(row=1, column=0)

        wrong_label = tk.Label(
            popup,
            text=f"Wrong: {self.wrong}",
            font=("Helvetica", 20),
        )
        wrong_label.configure(background="black", foreground="white")
        wrong_label.grid(row=2, column=0)

        percent_label = tk.Label(
            popup,
            text=f"Percent: {int(self.correct / (self.correct + self.wrong) * 100)}%",
            font=("Helvetica", 20),
        )
        percent_label.configure(background="black", foreground="white")
        percent_label.grid(row=3, column=0)

        popup.mainloop()

    def next_question(self, event=None):
        if self._next_question_button.config("state")[-1] == "disabled":
            return
        self.current_position += 1
        self._next_question_button["state"] = "disabled"
        self._check_button["state"] = "normal"
        self._user_input["state"] = "normal"
        self._user_input.delete("1.0", "end")
        self.play_question()

    @property
    def window(self):
        return self._window


def main():
    app = App()
    app.window.mainloop()


main()
