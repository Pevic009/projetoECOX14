import pandas as pd
from pathlib import Path
import limpeza

def carregar(BRONZE, PADRAO):
    """Busca o arquivo CSV mais recente na camada Bronze."""
    arquivos = sorted(BRONZE.glob(PADRAO))
    if not arquivos:
        raise FileNotFoundError(f"Nada encontrado em {BRONZE}")
    
    caminho = arquivos[-1]
    df = pd.read_csv(caminho)
    print("Lido:", caminho.name, df.shape)
    
    return df, caminho

def gerar_esqueleto():
    # script usado para formar os dicionarios usados nos scripts de transformacao
    fontes = [
        (Path("dados/bronze/transfermarkt"), "transfers_*.csv"),
        (Path("dados/bronze/brasileirao"), "partidas_*.csv")
    ]

    df_br, caminho_br = carregar(*fontes[1])
    df_tm, caminho_tm = carregar(*fontes[0])

    # --- 1. Dicionário do Brasileirão ---
    df_br["data"] = pd.to_datetime(df_br["data"], errors="coerce")
    df_br = df_br[df_br["data"].dt.year >= 2018] # Filtro temporal aplicado
    # Junta mandante e visitante para capturar todos os nomes
    todos_br = pd.concat([df_br["mandante"], df_br["visitante"]]).dropna()
    # Passa todos os nomes pela limpeza
    times_br_limpos = limpeza.chave_texto(todos_br).unique()

    # Criar um conjunto de palavras-chave dos times brasileiros para usar de filtro no dicionario do transfermarket
    palavras_br = set()
    for time in times_br_limpos:
        for palavra in time.split():
            if len(palavra) > 2: # Ignora preposições como 'de', 'da', 'fc'
                palavras_br.add(palavra)
    
    # Gera o esqueleto dos dicionarios, o lado direito devera ser preenchido corretamente e manualmente
    print("MAPA_CLUBES_BR = {")
    for time in sorted(times_br_limpos):
        print(f'    "{time}": "{time}",')
    print("}\n")

    # --- 2. Dicionário do Transfermarkt ---
    df_tm["data_tm"] = pd.to_datetime(df_tm["transfer_date"], errors="coerce")
    df_tm = df_tm[df_tm["data_tm"].dt.year >= 2018] # Filtro temporal aplicado
    todos_tm = pd.concat([df_tm["to_club_name"], df_tm["from_club_name"]]).dropna()
    times_tm_limpos = limpeza.chave_texto(todos_tm).unique()

    print("MAPA_CLUBES_TM = {")
    for time_tm in sorted(times_tm_limpos):
        # Só imprime se o time do TM tiver alguma palavra que existe no Brasileirão
        if any(palavra in time_tm for palavra in palavras_br):
            print(f'    "{time_tm}": "{time_tm}",') 
    print("}")

if __name__ == "__main__":
    gerar_esqueleto()