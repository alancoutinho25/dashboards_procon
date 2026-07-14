"""
Monta a tabela dos dados em memória, direto do banco de
dados, combinando os dados brutos definidas em queries.py com as
regras de negócio definidas em transformacoes.py.
 
Este é o módulo que o dashboard (app.py) importa:
 
    from services.abt import carregar_abt
"""
 
import pandas as pd
 
from services.queries import (
    consultar_abertura_processos,
    consultar_status_resolucao,
    consultar_ultima_interacao
)
from services.transformacoes import (
    classificar_origem_reclamacao,
    calcular_status_resolucao,
    adicionar_variaveis_tempo,
    adicionar_categoria_encerramento
)

 
def carregar_abt(interacoes_abertura,mapa_origem) -> pd.DataFrame:
    """
    Constrói a ABT de processos (nascidos ou convertidos)
    com todas as variáveis de negócio usadas no dashboard.
    """
 
    # 1. Dados brutos
    df_abertura = consultar_abertura_processos(interacoes_abertura)
    df_status_bruto = consultar_status_resolucao()
    df_ultima_interacao = consultar_ultima_interacao(interacoes_abertura)
 
    # 2. Transformações
    df_abertura = classificar_origem_reclamacao(
    df_abertura,
    mapa_origem
    )
    df_status = calcular_status_resolucao(df_status_bruto)
 
    # 3. União: abertura é a base (1 linha por processo = universo),
    #    status é LEFT porque nem todo processo tem evento de resolução
    abt = df_abertura.merge(df_status, on="process_id", how="left")
    abt = abt.merge(df_ultima_interacao, on="process_id", how="left")
    abt["processo_resolvido"] = (
        abt["processo_resolvido"].fillna(0).astype(int)
    )
 
    # 4. Variáveis de tempo (depende das colunas geradas acima)
    abt = adicionar_variaveis_tempo(abt)
    abt = adicionar_categoria_encerramento(abt)
 
    return abt