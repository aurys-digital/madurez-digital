import re
from difflib import get_close_matches
import unicodedata
from io import BytesIO

import pandas as pd
from loguru import logger
from collections import Counter
import config as cfg


# -----------------------------
# Helper functions
# -----------------------------
def clean_text(text) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub("\W+", " ", text).strip()
    return text.lower()


def load_questions(file, sheet_name):
    data = pd.read_excel(file, sheet_name=sheet_name)
    data.columns = [clean_text(str(c)) for c in data.columns]
    questions = data["pregunta"].apply(clean_text)

    # Check for duplicates
    counts = Counter(questions)
    duplicates = [q for q, count in counts.items() if count > 1]
    if duplicates:
        logger.error(
            f"Se encontraron {len(duplicates)} pregunta(s) duplicadas en {sheet_name}: {duplicates}"
        )

    return list(set(questions))


def load_answers(file, sheet_name):
    data = pd.read_excel(file, sheet_name=sheet_name)
    data.columns = [clean_text(str(c)) for c in data.columns]

    # Check for duplicated columns
    duplicates = data.columns[data.columns.duplicated()].unique()
    if len(duplicates) > 0:
        logger.error(
            f"Se encontraron {len(duplicates)} pregunta(s) duplicadas en {sheet_name}: {duplicates}"
        )

    data = data.to_dict(orient="records")
    return {clean_text(v): k for dictionary in data for k, v in dictionary.items()}


def load_results(file, sheet_name):
    data = pd.read_excel(file, sheet_name=sheet_name)
    data.columns = [clean_text(str(c)) for c in data.columns]

    # Check for duplicated columns
    duplicates = data.columns[data.columns.duplicated()].unique()
    if len(duplicates) > 0:
        logger.error(
            f"Se encontraron {len(duplicates)} pregunta(s) duplicadas en {sheet_name}: {duplicates}"
        )

    return data


def map_results(levels, results_file, questions_file, answers_file):
    results_dict = {}
    for level in levels:
        questions = load_questions(questions_file, sheet_name=level)
        answers = load_answers(answers_file, sheet_name=level)
        results = load_results(results_file, sheet_name=level)

        # Chequea cada columna
        copy_cols = results.columns.to_list()
        for col in results.columns:
            # Si la columna es parte de alguna de las preguntas mapeamos
            if col in questions:
                results[col] = results[col].apply(
                    lambda x: answers.get(clean_text(x), x)
                )
                questions.remove(col)  # Quitamos la pregunta de la lista de opciones
                copy_cols.remove(col)
        if len(questions) != 0:
            logger.error(
                f"No se mapearon {len(questions)} pregunta(s) para el nivel {level}. Por favor chequea que coincidan las tablas **preguntas** y **resultados**: {questions}"
            )

        results_dict[level] = results
    return results_dict


def to_excel(results_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for level, df in results_dict.items():
            df.to_excel(writer, sheet_name=level, index=False)
    processed_data = output.getvalue()
    return processed_data


if __name__ == "__main__":
    mapped_res = map_results(
        cfg.LEVELS,
        results_file=cfg.DATA_DIR / "results.xlsx",
        questions_file=cfg.DATA_DIR / "questions.xlsx",
        answers_file=cfg.DATA_DIR / "answers.xlsx",
    )
