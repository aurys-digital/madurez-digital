import pandas as pd
from pprint import pprint
from pathlib import Path
import config as cfg
from loguru import logger
import unicodedata


def clean_text(text):
    if not isinstance(text, str):
        logger.warning(f"input {str(text)} no es texto. Skip...")
        return None
    return unicodedata.normalize("NFKC", text.lower().strip())


def load_questions(sheet_name: str, path: str | Path = cfg.DATA_DIR):
    data = pd.read_excel(path / "questions.xlsx")
    data.columns = [clean_text(str(c)) for c in data.columns]
    questions = data["pregunta"].apply(clean_text)
    return questions.to_list()


def load_answers(sheet_name: str, path: str | Path = cfg.DATA_DIR):
    data = pd.read_excel(path / "answers.xlsx")
    data.columns = [clean_text(str(c)) for c in data.columns]
    data = data.to_dict(orient="records")
    return {clean_text(v): k for dictionary in data for k, v in dictionary.items()}


def load_results(sheet_name: str, path: str | Path = cfg.DATA_DIR):
    data = pd.read_excel(path / "results.xlsx")
    data.columns = [clean_text(str(c)) for c in data.columns]
    return data


def main():
    for level in cfg.LEVELS:
        questions = load_questions(sheet_name=level)
        answers = load_answers(sheet_name=level)
        results = load_results(sheet_name=level)
        # Mapeo a la columna de la pregunta
        for col in results.columns:
            if col in questions:
                results[col] = results[col].apply(lambda x: answers[clean_text(x)])
                logger.info(f"mapeo exitoso Nivel: {level} - Pregunta: {col}")


if __name__ == "__main__":
    main()
