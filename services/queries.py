import pandas as pd
from services.database import obter_engine
from services.dic_interacoes import (
    INTERACOES_RESOLUCAO,
    INTERACAO_DESARQUIVAMENTO,
    INTERACOES_ABERTURA_RECLAMACAO
)

engine = obter_engine()


def consultar_abertura_processos(interacoes_abertura):
    """
    Consulta o evento que originou a reclamação individual.
    """
    tipos_sql = ", ".join(
    map(str, interacoes_abertura)
    )

    sql = f"""
    SELECT

        process_id,

        createdAt AS dt_abertura,

        type_interaction_id AS tipo_primeira_interacao,

        title AS titulo_primeira_interacao

    FROM (

        SELECT

            process_id,

            createdAt,

            type_interaction_id,

            title,

            ROW_NUMBER() OVER (

                PARTITION BY process_id

                ORDER BY createdAt

            ) AS rn

        FROM interaction

        WHERE type_interaction_id IN ({tipos_sql})

    ) abertura

    WHERE rn = 1

    ORDER BY process_id
    """

    df = pd.read_sql(sql, engine)

    return df

def consultar_status_resolucao():
    """
    Consulta o evento mais recente de resolução/desarquivamento de
    cada processo — 1 linha por processo, não o histórico completo.

    Processos que nunca tiveram um evento de resolução ou
    desarquivamento simplesmente não aparecem no resultado (em vez de
    vir nulo/NaN aqui); é responsabilidade de quem consome esta query
    fazer um LEFT JOIN a partir do universo de processos e tratar os
    ausentes como não resolvidos — é isso que services/abt.py faz.
    """

    tipos_interacao = (
        INTERACOES_RESOLUCAO
        + [INTERACAO_DESARQUIVAMENTO]
    )

    tipos_sql = ", ".join(map(str, tipos_interacao))

    sql = f"""
    SELECT

        process_id,

        createdAt AS dt_ultima_interacao_relevante,

        type_interaction_id AS tipo_ultima_interacao_relevante,

        title AS titulo_ultima_interacao_relevante

    FROM (

        SELECT

            process_id,

            id,

            createdAt,

            type_interaction_id,

            title,

            ROW_NUMBER() OVER (

                PARTITION BY process_id

                ORDER BY createdAt DESC, id DESC

            ) AS rn

        FROM interaction

        WHERE type_interaction_id IN ({tipos_sql})

    ) t

    WHERE rn = 1

    ORDER BY process_id
    """

    df = pd.read_sql(sql, engine)

    return df

def consultar_ultima_interacao(interacoes_abertura):
    """
    Consulta a última interação de cada reclamação individual.
    """
    tipos_sql = ", ".join(map(str, interacoes_abertura))
    sql = f"""
    SELECT

        i.process_id,

        i.createdAt AS dt_ultima_interacao,

        i.type_interaction_id AS tipo_ultima_interacao,

        i.title AS titulo_ultima_interacao

    FROM (

        SELECT

            process_id

        FROM interaction

        WHERE type_interaction_id IN (20,172)

        GROUP BY process_id

    ) reclamacoes

    INNER JOIN (

        SELECT

            process_id,

            createdAt,

            type_interaction_id,

            title,

            ROW_NUMBER() OVER (

                PARTITION BY process_id

                ORDER BY createdAt DESC

            ) AS rn

        FROM interaction

    ) i

    ON reclamacoes.process_id = i.process_id

    WHERE i.rn = 1

    ORDER BY i.process_id
    """

    df = pd.read_sql(sql, engine)

    return df

