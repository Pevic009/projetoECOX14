from pathlib import Path
import pandas as pd
from data_profiling import ProfileReport

# 1. Constantes ajustadas para a sua fonte
BRONZE = Path("dados/bronze/transfermarkt")
PADRAO = "transfers_*.csv"
RELATORIOS = Path("relatorios")

def mais_recente():
    """Busca o arquivo CSV mais novo na pasta bronze usando a data no nome."""
    arquivos = sorted(BRONZE.glob(PADRAO))
    if not arquivos:
        raise FileNotFoundError("bronze vazia")
    return arquivos[-1]

def gerar(caminho):
    """Lê o CSV e gera o relatório HTML automático."""
    df = pd.read_csv(caminho)
    perfil = ProfileReport(df, title=caminho.name)
    
    RELATORIOS.mkdir(exist_ok=True)
    saida = RELATORIOS / f"{caminho.stem}.html"
    perfil.to_file(saida)
    
    return saida

def main():
    caminho = mais_recente()
    print("perfilando:", caminho.name)
    print(gerar(caminho))

if __name__ == "__main__":
    main() 