from __future__ import annotations

from pathlib import Path
from threading import Thread
from typing import Optional

from pydantic import BaseModel
from pydub import AudioSegment
from pydub.playback import play

from .speech import TextToAudio


class Answer(BaseModel):
    text: str
    correct: bool


class Question:
    text: str
    audio: AudioSegment

    def __init__(self, text: str, audio: AudioSegment):
        self.text = text
        self.audio = audio

    def play(self):
        Thread(target=play, args=(self.audio,)).start()


class Questions:
    _tta: TextToAudio
    _questions: list[str | Question]
    _index: int
    _answers: list[Answer]
    _correct_count: int
    _answers_file: Path

    def __init__(self, input_file: Path, answers_file: Path):
        assert isinstance(input_file, Path)
        assert input_file.exists()
        assert isinstance(answers_file, Path)
        self._tta = TextToAudio()
        self._index = 0
        self._answers = []
        self._correct_count = 0
        self._questions = []

        self._read_questions(input_file)

        if answers_file.exists():
            self._read_answers(answers_file)
        else:
            answers_file.parent.mkdir(parents=True, exist_ok=True)
        self._answers_file = answers_file

    def _read_answers(self, answers_file: Path):
        with open(answers_file, "r") as f:
            for line in f:
                answer = Answer()
                answer.text, answer.correct = line.strip().split(",")
                if answer.correct == "True":
                    answer.correct = True
                    self._correct_count += 1
                elif answer.correct == "False":
                    answer.correct = False
                self._answers.append(answer)
                self._index += 1

    def _read_questions(self, input_file: Path):
        with open(input_file, "r") as f:
            for line in f:
                text = line.strip()
                self._questions.append(text)

    def get_question(self) -> Optional[Question]:
        if self._index >= len(self._questions):
            return None
        question = self._questions[self._index]
        if isinstance(question, str):
            self._questions[self._index] = Question(question, self._tta.convert(question))
        return self._questions[self._index]

    def save_answers(self):
        with open(self._answers_file, "w") as f:
            for answer in self._answers:
                f.write(f"{answer.text},{answer.correct}\n")

    def put_answer(self, answer: Answer):
        self._answers[self._index] = answer
        self.save_answers()

    def next_question(self):
        self._index += 1

    def check_answer(self, user_answer:str)->bool:
        if user_answer == "":
            return False
        # Tokenize
        correct = (user_answer == self.get_question().text)
        answer = Answer(text=user_answer, correct=correct)
        self.put_answer(answer)
        return correct

    @property
    def index(self) -> int:
        return self._index

    @property
    def correct_count(self) -> int:
        return self._correct_count

    @property
    def failures_count(self) -> int:
        return self._index - self._correct_count

    def __len__(self):
        return len(self._questions)
