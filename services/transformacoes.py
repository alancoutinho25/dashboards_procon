"""
Funções de transformação da ABT (Analytical Base Table).
 
Cada função aqui é "pura": recebe um DataFrame vindo das queries brutas
(services/queries.py) e devolve um DataFrame com colunas derivadas.
Nenhuma função aqui acessa o banco de dados — isso mantém a lógica de
negócio testável sem precisar de conexão real, e reutilizável por
qualquer implementação de dashboard (Streamlit, Fale Procon, etc).
"""
 
import pandas as pd
from services.dic_interacoes import INTERACAO_DESARQUIVAMENTO
from services.dic_encerramentos import *
 
# ==========================================================
# ORIGEM DA RECLAMAÇÃO
# ==========================================================
 
def classificar_origem_reclamacao(df_abertura: pd.DataFrame, mapa_origem:dict) -> pd.DataFrame:
    """
    Classifica cada processo conforme a interação que o originou:
    - 20  -> nasceu como Reclamação Individual
    - 172 -> foi convertido para Reclamação Individual
 
    Espera um DataFrame com a coluna 'tipo_primeira_interacao'
    (saída de consultar_abertura_processos()).
    """
 
    df = df_abertura.copy()
 
 
    df["origem_reclamacao"] = (
        df["tipo_primeira_interacao"]
        .map(mapa_origem)
        .fillna("Outro")
    )
 
    return df
 
 
# ==========================================================
# STATUS DE RESOLUÇÃO
# ==========================================================
 
def calcular_status_resolucao(df_status: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe o resultado de consultar_status_resolucao() — já 1 linha
    por processo, contendo o evento mais recente entre resolução e
    desarquivamento (o banco já fez essa deduplicação via ROW_NUMBER)
    — e apenas adiciona a flag de negócio processo_resolvido (0/1).
 
    Regra de negócio: se o evento mais recente for um desarquivamento,
    o processo NÃO está resolvido (mesmo que tenha sido resolvido
    antes). Se for qualquer outro tipo de resolução, está resolvido.
    Processos sem nenhuma linha aqui (nunca tiveram evento de
    resolução/desarquivamento) não são tratados nesta função — ficam
    de fora do resultado, e é responsabilidade de quem faz o merge
    (services/abt.py) tratá-los como não resolvidos.
    """
 
    colunas_saida = [
        "process_id",
        "dt_ultima_interacao_relevante",
        "tipo_ultima_interacao_relevante",
        "processo_resolvido",
    ]
 
    if df_status.empty:
        return pd.DataFrame(columns=colunas_saida)
 
    df = df_status.copy()
 
    df["processo_resolvido"] = (
        df["tipo_ultima_interacao_relevante"]
        .ne(INTERACAO_DESARQUIVAMENTO)
        .astype(int)
    )
 
    return df[colunas_saida]
 
 
# ==========================================================
# VARIÁVEIS DE TEMPO
# ==========================================================
 
def adicionar_variaveis_tempo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deriva ano/mês/semestre de abertura e o tempo (em dias) até a
    resolução. Espera um DataFrame já contendo 'dt_abertura',
    'dt_ultima_interacao_relevante' e 'processo_resolvido'.
    """
 
    df = df.copy()
 
    df["dt_abertura"] = pd.to_datetime(df["dt_abertura"])
    df["dt_ultima_interacao_relevante"] = pd.to_datetime(
        df["dt_ultima_interacao_relevante"]
    )
 
    df["ano_abertura"] = df["dt_abertura"].dt.year
    df["mes_abertura"] = df["dt_abertura"].dt.month
    df["trimestre_abertura"] = df["dt_abertura"].dt.quarter
    df["semestre_abertura"] = df["mes_abertura"].apply(
        lambda m: 1 if m <= 6 else 2
    )
 
    df["dias_ate_resolucao"] = (
        df["dt_ultima_interacao_relevante"] - df["dt_abertura"]
    ).dt.days

    # Ajuste para inconsistências temporais
    # Casos de -1 dia normalmente decorrem de diferença de horário/fuso
    # entre abertura e resolução ocorridas no mesmo dia.
    df.loc[
        df["dias_ate_resolucao"] == -1,
        "dias_ate_resolucao"
    ] = 0

    # Demais valores negativos representam inconsistências da base
    # e não devem compor os indicadores.
    df.loc[
        df["dias_ate_resolucao"] < -1,
        "dias_ate_resolucao"
    ] = pd.NA
 
    # Processos não resolvidos não têm tempo de resolução definido
    df.loc[df["processo_resolvido"] == 0, "dias_ate_resolucao"] = pd.NA

    df["faixa_tempo_resolucao"] = pd.cut(

    df["dias_ate_resolucao"],

    bins=[
        -0.1,
        0,
        7,
        15,
        30,
        60,
        90,
        180,
        float("inf")
    ],

    labels=[
        "Mesmo dia",
        "1–7 dias",
        "8–15 dias",
        "16–30 dias",
        "31–60 dias",
        "61–90 dias",
        "91–180 dias",
        "Acima de 180 dias"
    ]

    )
 
    return df

# ==========================================================
# CATEGORIA GERENCIAL DE ENCERRAMENTO
# ==========================================================

def adicionar_categoria_encerramento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza os diversos títulos de encerramento em categorias
    gerenciais, utilizando o tipo da última interação.
    """

    df = df.copy()

    df["categoria_encerramento"] = (
        df["tipo_ultima_interacao"]
          .map(MAPA_ENCERRAMENTOS)
          .fillna("Outros")
    )

    return df