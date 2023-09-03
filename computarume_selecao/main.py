import os
from csv import DictWriter
from pathlib import Path

import pandas as pd

pd.set_option("display.width", 1000)
pd.set_option("display.max_rows", 500)

ROOT_FOLDER = Path(__file__).parent.parent
INPUT_PATH = ROOT_FOLDER / "input.csv"
if not INPUT_PATH.exists():
    raise FileNotFoundError(
        f"""
        O arquivo de entrada não foi encontrado.
        Verifique se o arquivo {INPUT_PATH} existe.
        """
    )
OUTPUT_PATH = ROOT_FOLDER / "output.csv"
EXTRA_PATH = ROOT_FOLDER / "extra.csv"

if EXTRA_PATH.exists():
    os.remove(EXTRA_PATH)

if OUTPUT_PATH.exists():
    os.remove(OUTPUT_PATH)


def get_data() -> pd.DataFrame:
    df = pd.read_csv(INPUT_PATH)
    df.drop(columns=df.columns[[0, 6, 7]], inplace=True, axis=1)
    df.rename(
        columns={
            df.columns[0]: "email",
            df.columns[1]: "nome",
            df.columns[2]: "nivel",
            df.columns[3]: "github",
            df.columns[4]: "discord",
        },
        inplace=True,
    )
    df["github"] = df["github"].apply(lambda x: x.split("/")[-1])
    return df


def main():
    df = get_data()
    professors = df[df["nivel"] == "Professor"].to_dict(orient="records")
    others = df[df["nivel"] != "Professor"]
    num_professors = len(professors)
    extras = []
    for key, sub_df in others.groupby("nivel"):
        sub_df = sub_df.sample(frac=1)
        per_group = len(sub_df) // num_professors
        if per_group == 0:
            print(f"Não há participantes suficientes para o nível {key}")
            continue
        extras.extend(
            sub_df.iloc[per_group * num_professors :].to_dict(orient="records")
        )
        for i, professor in enumerate(professors):
            paritipants = sub_df.iloc[i * per_group : (i + 1) * per_group].to_dict(
                orient="records"
            )
            professor.setdefault("integrantes", []).extend(paritipants)

    result = []
    for professor in professors:
        for participant in professor["integrantes"]:
            participant["professor"] = professor["nome"]
            result.append(participant)
    if not result:
        raise ValueError(
            """
            Não foi possível gerar os grupos.
            Verifique se o número de participantes é suficiente.
            """
        )
    if extras:
        with open(EXTRA_PATH, "w") as f:
            writer = DictWriter(f, fieldnames=extras[0].keys())
            writer.writeheader()
            writer.writerows(extras)
    else:
        print("Não há participantes extras.")

    with open(OUTPUT_PATH, "w") as f:
        writer = DictWriter(f, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    main()
