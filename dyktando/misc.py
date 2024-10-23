from pathlib import Path


def get_resource_path(audio_file: Path|str) -> Path:
    if isinstance(audio_file, str):
        audio_file = Path(audio_file)
    current_file_path = Path(__file__)
    project_root = current_file_path.parent.parent
    return project_root / "data" / "audio" / audio_file

def cannonize_text(text:str)->str:
    # 1. Removes all non-alphanumeric characters from the text.
    # 2. Splits the text into words.
    # 3. Converts each word to lowercase.
    # 4. Assembles the words back into a single string.

    tokens = text.split(' ')
    ans = []

    for token in tokens:
        ans.append(''.join([c for c in token if c.isalnum()]))

    return ' '.join(tokens)