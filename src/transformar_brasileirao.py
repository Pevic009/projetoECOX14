import json
from datetime import datetime
from pathlib import Path
import pandas as pd

import limpeza

BRONZE = Path("dados/bronze/brasileirao")
PRATA = Path("dados/prata")
PADRAO = "partidas_*.csv"

MAPA_CLUBES_BR = {
    "america-mg": "america-mg",
    "athletico-pr": "athletico-pr",
    "atletico-go": "atletico-go",
    "atletico-mg": "atletico-mg",
    "avai": "avai",
    "bahia": "bahia",
    "botafogo-rj": "botafogo-rj",
    "bragantino": "bragantino",
    "ceara": "ceara",
    "chapecoense": "chapecoense",
    "corinthians": "corinthians",
    "coritiba": "coritiba",
    "criciuma": "criciuma",
    "cruzeiro": "cruzeiro",
    "csa": "csa",
    "cuiaba": "cuiaba",
    "flamengo": "flamengo",
    "fluminense": "fluminense",
    "fortaleza": "fortaleza",
    "goias": "goias",
    "gremio": "gremio",
    "internacional": "internacional",
    "juventude": "juventude",
    "mirassol": "mirassol",
    "palmeiras": "palmeiras",
    "parana": "parana",
    "santos": "santos",
    "sao paulo": "sao paulo",
    "sport": "sport",
    "vasco": "vasco",
    "vitoria": "vitoria",
}

def carregar():
    """Busca o arquivo CSV mais recente na camada Bronze."""
    arquivos = sorted(BRONZE.glob(PADRAO))
    if not arquivos:
        raise FileNotFoundError(f"Nada encontrado em {BRONZE}")
    
    caminho = arquivos[-1]
    df = pd.read_csv(caminho)
    print("Lido:", caminho.name, df.shape)
    
    return df, caminho

def remover_colunas_inuteis(df):
    """Descarta colunas com alta incidencia de nulos ou sem utilidade."""
    # Omissao de variaveis com mais de 50% de nulos e variaveis granulares de tempo/local
    colunas_para_cair = [
        "arrecadacao", "formacao_mandante", "formacao_visitante", 
        "tecnico_mandante", "tecnico_visitante", "hora", "arena",
        "mandante_Estado", "visitante_Estado"
    ]
    df = df.drop(columns=colunas_para_cair, errors="ignore")
    
    return df

def filtrar_e_formatar_datas(df, ano_minimo=2018):
    """Garante o tipo datetime para datas, cria atributo de ano e filtra registros antigos."""
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    
    # Criacao de atributo derivado para alinhamento com a base financeira
    df["ano_campeonato"] = df["data"].dt.year.astype("Int64")
    
    # Aplicacao do filtro de dominio temporal
    valido = df["ano_campeonato"] >= ano_minimo
    df_filtrado = df[valido].copy()
    
    print(f"Registros anteriores a {ano_minimo} removidos:", (~valido).sum())
    
    return df_filtrado

def padronizar_nomes_clubes(df):
    """Aplica o modulo de limpeza generico nas chaves de juncao de texto."""
    df["mandante_padrao"] = limpeza.chave_texto(df["mandante"])
    df["mandante_padrao"] = limpeza.aplicar_mapa(df["mandante_padrao"], MAPA_CLUBES_BR)

    df["visitante_padrao"] = limpeza.chave_texto(df["visitante"])
    df["visitante_padrao"] = limpeza.aplicar_mapa(df["visitante_padrao"], MAPA_CLUBES_BR)

    df["vencedor_padrao"] = limpeza.chave_texto(df["vencedor"])
    df["vencedor_padrao"] = limpeza.aplicar_mapa(df["vencedor_padrao"], MAPA_CLUBES_BR)
    
    return df

def tipar_placares(df):
    """Garante o armazenamento dos resultados como numeros inteiros consistentes."""
    colunas_placar = ["mandante_Placar", "visitante_Placar"]
    
    for col in colunas_placar:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        
    return df

def remover_erros_placares(df, teto_gols=15):
    """Remove registros com placares impossíveis (negativos ou absurdamente altos)."""
    # Um placar é válido se for nulo (partida não realizada/sem dado) OU se estiver entre 0 e o teto máximo
    valido_mandante = df["mandante_Placar"].isna() | df["mandante_Placar"].between(0, teto_gols)
    valido_visitante = df["visitante_Placar"].isna() | df["visitante_Placar"].between(0, teto_gols)
    
    # A linha só sobrevive se AMBOS os placares forem válidos
    valido = valido_mandante & valido_visitante
    df_filtrado = df[valido].copy()
    
    removidos = (~valido).sum()
    print(f"Erros comprovados de placar removidos (fora da faixa 0 - {teto_gols}):", removidos)
    
    return df_filtrado

def salvar(df):
    """Grava o DataFrame tratado na camada Prata utilizando o formato Parquet."""
    PRATA.mkdir(parents=True, exist_ok=True)
    destino = PRATA / "partidas.parquet"
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
    df = tipar_placares(df)
    df = remover_erros_placares(df)
    
    destino = salvar(df)
    
    # Documentacao de metadados das alteracoes estruturais
    registrar(origem, destino, antes, len(df), [
        "espacos vazios removidos das extremidades das strings",
        "remocao de dados taticos nulos e informacoes de hora/arena",
        "criacao de ano_campeonato e exclusao de jogos anteriores a 2018",
        "padronizacao lowercase sem acentos em nomes de clubes para futura juncao",
        "garantia de integridade numerica (Int64) nas colunas de placar"
        "remocao de erros comprovados nos placares (valores negativos ou acima de 15 gols)"
    ])

if __name__ == "__main__":
    main()