import unicodedata
import pandas as pd

def tirar_espacos(df):
    """Remove espacos sobrando dos nomes de colunas e textos."""
    df.columns = df.columns.str.strip()
    for c in df.select_dtypes(include="object"):
        df[c] = df[c].str.strip()
    return df

def chave_texto(serie):
    """Versao comparavel de um texto: sem acento, sem espaco e tudo minusculo."""
    s = serie.str.strip().str.lower()
    s = s.str.normalize("NFKD")
    s = s.str.encode("ascii", errors="ignore")
    return s.str.decode("utf-8")

def aplicar_mapa(serie, mapa):
    """Troca variantes pelo valor canonico usando um dicionario."""
    return serie.replace(mapa)