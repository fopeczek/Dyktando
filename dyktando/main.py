import click
from pathlib import Path

from .app import App
from .question_server import Questions

@click.command()
@click.argument('question_file', type=click.Path(exists=True, path_type=Path))
@click.option('--answer_file', type=click.Path(path_type=Path), default=None, help='Path to the answer file')
def cli(question_file, answer_file):
    assert isinstance(question_file, Path)
    question_file = question_file.absolute()
    if answer_file is None:
        answer_file = question_file.parent / "answers.txt"

    qs = Questions(question_file, answer_file)
    app = App(qs)
    app.window.mainloop()

if __name__ == "__main__":
    cli()