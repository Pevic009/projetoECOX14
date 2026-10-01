from pathlib import Path
from datetime import date, datetime
import shutil
import kagglehub
import json

# 1. Configurações exclusivas para a segunda fonte
DATASET = "adaoduque/campeonato-brasileiro-de-futebol"
BRONZE = Path("dados/bronze/brasileirao")

def localizar(pasta):
    # Busca o arquivo principal de partidas. 
    # Se o nome do CSV no seu Kaggle for diferente, mude aqui:
    arquivo_alvo = pasta / "campeonato-brasileiro-full.csv"
    
    # Plano B: se não achar pelo nome exato, pega o primeiro CSV que encontrar
    if not arquivo_alvo.exists():
        arquivos = list(pasta.glob("*.csv"))
        if not arquivos:
            raise FileNotFoundError("Nenhum CSV encontrado na pasta baixada")
        arquivo_alvo = arquivos[0]
        
    print("encontrado:", arquivo_alvo.name)
    return arquivo_alvo

def baixar():
    pasta = kagglehub.dataset_download(DATASET)
    print("baixado em:", pasta)
    return Path(pasta)

def copiar(origem):
    BRONZE.mkdir(parents=True, exist_ok=True)
    hoje = date.today().strftime("%Y%m%d")
    destino = BRONZE / f"partidas_{hoje}.csv"
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