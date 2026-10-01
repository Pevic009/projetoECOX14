import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

import limpeza

BRONZE = Path("dados/bronze/transfermarkt")
PRATA = Path("dados/prata")
PADRAO = "transfers_*.csv"

MAPA_CLUBES_BR = {
    "sao paulo futebol clube": "sao paulo",
    "clube atletico mineiro": "atletico mineiro",
    "cr flamengo": "flamengo"
}

def carregar():
    """Busca o arquivo CSV mais recente na camada Bronze e carrega em DataFrame."""
    arquivos = sorted(BRONZE.glob(PADRAO))
    if not arquivos:
        raise FileNotFoundError(f"Nada encontrado em {BRONZE}")
    
    caminho = arquivos[-1]
    df = pd.read_csv(caminho)
    print("Lido:", caminho.name, df.shape)
    
    return df, caminho

def remover_colunas_inuteis(df):
    """Remove a coluna de temporada europeia."""
    # Lista de colunas descartáveis
    colunas_para_cair = ["transfer_season"]
    df = df.drop(columns=colunas_para_cair, errors="ignore")
    
    return df

def filtrar_e_formatar_datas(df, ano_minimo=2018):
    """Garante o tipo datetime para datas, cria atributo de ano civil e filtra registros antigos."""
    df["transfer_date"] = pd.to_datetime(df["transfer_date"], errors="coerce")
    
    # Criacao de atributo derivado: ano civil da transferencia
    df["transfer_year"] = df["transfer_date"].dt.year.astype("Int64")
    
    # Aplicacao do filtro de dominio temporal
    valido = df["transfer_year"] >= ano_minimo
    df_filtrado = df[valido].copy()
    
    print(f"Registros anteriores a {ano_minimo} removidos:", (~valido).sum())
    
    return df_filtrado

def padronizar_nomes_clubes(df):
    """Aplica o modulo de limpeza generico nas chaves de juncao de texto."""
    df["to_club_name_padrao"] = limpeza.chave_texto(df["to_club_name"])
    df["to_club_name_padrao"] = limpeza.aplicar_mapa(df["to_club_name_padrao"], MAPA_CLUBES_BR)

    df["from_club_name_padrao"] = limpeza.chave_texto(df["from_club_name"])
    df["from_club_name_padrao"] = limpeza.aplicar_mapa(df["from_club_name_padrao"], MAPA_CLUBES_BR)

    return df

def converter_moeda_texto(valor):
    """Extrai valores numericos de strings monetarias ou converte transferencias gratuitas para 0.0."""
    if pd.isna(valor):
        return np.nan
        
    valor_str = str(valor).lower()
    
    # Regra de negocio: termos que indicam ausencia de custo direto de transferencia
    if any(palavra in valor_str for palavra in ["free", "loan", "-", "?", "draft"]):
        return 0.0
        
    # Remocao de caracteres de moeda
    valor_str = valor_str.replace("€", "").replace("£", "")
    
    # Conversao de sufixos de milhar e milhao para notacao cientifica/float
    try:
        if "m" in valor_str:
            return float(valor_str.replace("m", "")) * 1_000_000
        elif "k" in valor_str or "th" in valor_str:
            return float(valor_str.replace("k", "").replace("th", "")) * 1_000
        else:
            return float(valor_str)
    except ValueError:
        return np.nan

def tratar_valores_financeiros(df):
    """Aplica a funcao de conversao monetaria nas colunas financeiras do DataFrame."""
    colunas_financeiras = ["transfer_fee", "market_value_in_eur"]
    
    for col in colunas_financeiras:
        df[col + "_num"] = df[col].apply(converter_moeda_texto)
    
    print(f"Ausentes reais em taxa de transferencia apos conversao: {df['transfer_fee_num'].isna().sum()}")
    
    return df

def salvar(df):
    """Grava o DataFrame tratado na camada Prata utilizando o formato Parquet."""
    PRATA.mkdir(parents=True, exist_ok=True)
    destino = PRATA / "transfers.parquet"
    df.to_parquet(destino, index=False)
    
    print("Salvo em:", destino, df.shape)
    return destino

def registrar(origem, destino, antes, depois, decisoes):
    """Registra as operacoes realizadas no arquivo de log de proveniencia em JSONL."""
    info = {
        "origem": origem.name,
        "arquivo_prata": destino.name,
        "linhas_antes": antes,
        "linhas_depois": depois,
        "decisoes": decisoes,
        "transformado_em": datetime.now().isoformat(timespec="seconds"),
    }
    
    caminho = PRATA / "proveniencia.jsonl"
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")

def main():
    # Execucao sequencial do pipeline de transformacao
    df, origem = carregar()
    antes = len(df)
    
    df = limpeza.tirar_espacos(df)
    df = remover_colunas_inuteis(df)
    df = filtrar_e_formatar_datas(df, ano_minimo=2018)
    df = padronizar_nomes_clubes(df)
    df = tratar_valores_financeiros(df)
    
    destino = salvar(df)
    
    # Documentacao de metadados das alteracoes estruturais
    registrar(origem, destino, antes, len(df), [
        "espacos vazios removidos das extremidades das strings",
        "coluna transfer_season europeia descartada",
        "criacao de transfer_year e exclusao de registros anteriores a 2018",
        "padronizacao lowercase sem acentos em nomes de clubes para futura juncao",
        "extracao de valores financeiros de texto para float64 (cost-free tipado como 0.0)"
    ])

if __name__ == "__main__":
    main()