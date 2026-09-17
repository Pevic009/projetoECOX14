from pathlib import Path
from datetime import date,datetime
import shutil
import kagglehub
import json

DATASET = "davidcariboo/player-scores"
BRONZE = Path("dados/bronze/transfermarkt")

def localizar(pasta):
    arquivo_alvo = pasta / "transfers.csv"
    if not arquivo_alvo.exists():
        raise FileNotFoundError("nenhum CSV")
    print("encontrado:", arquivo_alvo.name)
    return arquivo_alvo

def baixar():
    pasta = kagglehub.dataset_download(DATASET)
    print("baixado em:", pasta)
    return Path(pasta)

def copiar(origem):
    BRONZE.mkdir(parents=True, exist_ok=True)
    hoje = date.today().strftime("%Y%m%d")
    destino = BRONZE / f"transfers_{hoje}.csv"
    shutil.copy(origem, destino)
    return destino

def registrar(origem, destino):
    info = {
        "fonte": DATASET,
        "origem": origem.name,
        "arquivo_destino": destino.name,
        "extraido_em": datetime.now().isoformat()
    }

    caminho = BRONZE / "proveniencia.jsonl"
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")

def main():
    pasta = baixar()
    origem = localizar(pasta)
    destino = copiar(origem)
    registrar(origem, destino)

if __name__ == "__main__":
    main()