"""
Dicionário de tipos de interação utilizados nas consultas SQL.

Este módulo centraliza todas as regras de negócio relacionadas
aos tipos de interação do sistema Fale Procon.
"""

# ==========================================================
# ABERTURA DE PROCESSOS
# ==========================================================

INTERACOES_ABERTURA = [
    20,
    172
]

INTERACOES_ABERTURA_RECLAMACAO = [
    20,
    172
]

INTERACOES_ABERTURA_NEGOCIACAO = [
    151,
    174
]

INTERACOES_ABERTURA_PROCESSO_ADMINISTRATIVO = [2, 173]

# ==========================================================
# INTERAÇÕES DE RESOLUÇÃO
# ==========================================================

INTERACOES_RESOLUCAO = [
    32,
    111,
    166,
    177,
    188,
    201,
    202,
    220,
    249,
    251,
    252,
    257,
    276,
    293,
    393
]

# ==========================================================
# DESARQUIVAMENTO
# ==========================================================

INTERACAO_DESARQUIVAMENTO = 208

MAPA_ORIGEM_RECLAMACAO = {
    20: "Reclamação Individual",
    172: "Convertida para Reclamação Individual"
}

MAPA_ORIGEM_NEGOCIACAO = {
    151: "Negociação de Dívida",
    174: "Convertida para Negociação de Dívida"
}

MAPA_ORIGEM_PROCESSO_ADMINISTRATIVO = {
    2: "Processo Administrativo",
    173: "Convertido para Processo Administrativo"
}

CONFIG_PROCESSOS = {

    "Reclamação Individual": {

        "interacoes_abertura": INTERACOES_ABERTURA_RECLAMACAO,

        "mapa_origem": MAPA_ORIGEM_RECLAMACAO

    },

    "Negociação de Dívida": {

        "interacoes_abertura": INTERACOES_ABERTURA_NEGOCIACAO,

        "mapa_origem": MAPA_ORIGEM_NEGOCIACAO

    },

    "Processo Administrativo": {

    "interacoes_abertura": INTERACOES_ABERTURA_PROCESSO_ADMINISTRATIVO,

    "mapa_origem": MAPA_ORIGEM_PROCESSO_ADMINISTRATIVO
    }

}

CONFIG_TEXTOS = {

    "Reclamação Individual": {

        "processo": "Reclamação",
        "processos": "Reclamações",
        "processo_min": "reclamação individual",
        "processos_min": "reclamações individuais"

    },

    "Negociação de Dívida": {

        "processo": "Negociação de Dívida",
        "processos": "Negociações",
        "processo_min": "negociação de dívida",
        "processos_min": "negociações de dívida"

    },

    "Processo Administrativo": {

    "processo": "Processo Administrativo",

    "processos": "Processos",

    "processo_min": "processo administrativo",

    "processos_min": "processos administrativos"

    },

}