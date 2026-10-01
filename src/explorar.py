from pathlib import Path
import pandas as pd
from data_profiling import ProfileReport

RELATORIOS = Path("relatorios")

def mais_recente(pasta_bronze, padrao):
    """Busca o arquivo CSV mais novo na pasta informada usando a data no nome."""
    arquivos = sorted(pasta_bronze.glob(padrao))
    if not arquivos:
        raise FileNotFoundError(f"A pasta {pasta_bronze} está vazia ou sem arquivos no padrão {padrao}")
    return arquivos[-1]

def gerar(caminho):
    """Lê o CSV e gera o relatório HTML automático."""
    df = pd.read_csv(caminho)
    # O título usa o nome do arquivo para não confundir os relatórios
    perfil = ProfileReport(df, title=f"Relatório - {caminho.name}")
    
    RELATORIOS.mkdir(exist_ok=True)
    saida = RELATORIOS / f"{caminho.stem}.html"
    perfil.to_file(saida)
    
    return saida

def main():
    # Lista com as pastas da Bronze e o padrão de arquivo de cada fonte
    fontes = [
        (Path("dados/bronze/transfermarkt"), "transfers_*.csv"),
        (Path("dados/bronze/brasileirao"), "partidas_*.csv")
    ]
    
    for pasta, padrao in fontes:
        try:
            caminho = mais_recente(pasta, padrao)
            print("Perfilando:", caminho.name)
            print("Salvo em:", gerar(caminho))
            print("-" * 30)
        except FileNotFoundError as e:
            print(e)

if __name__ == "__main__":
    main()