"""
Padronização gerencial dos motivos de encerramento.

Converte o interaction_id da última interação do processo
em uma categoria de negócio utilizada pelos dashboards.
"""

MAPA_ENCERRAMENTOS = {

    # =====================================================
    # RESOLUÇÃO
    # =====================================================

    111: "Resolvido",
    220: "Resolvido",
    251: "Resolvido",
    252: "Resolvido",

    249: "Arquivamento por Resolução",
    257: "Arquivamento por Resolução",
    393: "Arquivamento por Resolução",
    276: "Arquivamento por Resolução",
    293: "Arquivamento por Improcedência",
    # =====================================================
    # ACORDOS
    # =====================================================

    201: "Arquivamento por Acordo",
    202: "Arquivamento por Acordo",

    # =====================================================
    # DESISTÊNCIA / INÉRCIA
    # =====================================================

    12: "Desistência do Consumidor",
    240: "Inércia do Consumidor",

    # =====================================================
    # NEGOCIAÇÃO
    # =====================================================

    204: "Renegociação Recusada",

    # =====================================================
    # AUDIÊNCIAS
    # =====================================================

    44: "Encerramento em Audiência",
    184: "Encerramento em Audiência",
    186: "Encerramento em Audiência",

    # =====================================================
    # DEMANDA
    # =====================================================

    177: "Demanda Encerrada",

    # =====================================================
    # PROCESSO ADMINISTRATIVO
    # =====================================================

    173: "Encaminhado para Processo Administrativo",
    199: "Encaminhado para Processo Administrativo",
    243: "Encaminhado para Processo Administrativo",

    # =====================================================
    # JURÍDICO / TAC / MULTA
    # =====================================================

    148: "Jurídico / TAC / Multa",
    165: "Jurídico / TAC / Multa",
    166: "Jurídico / TAC / Multa",

    253: "Jurídico / TAC / Multa",
    304: "Jurídico / TAC / Multa",
    305: "Jurídico / TAC / Multa",
    306: "Jurídico / TAC / Multa",
    307: "Jurídico / TAC / Multa",
    310: "Jurídico / TAC / Multa",
    311: "Jurídico / TAC / Multa",
    312: "Jurídico / TAC / Multa",
    313: "Jurídico / TAC / Multa",
    314: "Jurídico / TAC / Multa",
    315: "Jurídico / TAC / Multa",
    316: "Jurídico / TAC / Multa",
    319: "Jurídico / TAC / Multa",

    322: "Jurídico / TAC / Multa",
    323: "Jurídico / TAC / Multa",
    324: "Jurídico / TAC / Multa",

    326: "Jurídico / TAC / Multa",
    327: "Jurídico / TAC / Multa",
    328: "Jurídico / TAC / Multa",
    330: "Jurídico / TAC / Multa",
    334: "Jurídico / TAC / Multa",
    335: "Jurídico / TAC / Multa",

    338: "Jurídico / TAC / Multa",
    339: "Jurídico / TAC / Multa",
    340: "Jurídico / TAC / Multa",

    352: "Jurídico / TAC / Multa",
    369: "Jurídico / TAC / Multa",
    405: "Jurídico / TAC / Multa",

    # =====================================================
    # EM ANDAMENTO
    # =====================================================
    20: "Em andamento",   # Reclamação Individual Iniciada
    43: "Em andamento",   # Audiência Cancelada
    85: "Em andamento",
    96: "Em andamento",

    110: "Em andamento",

    137: "Em andamento",
    139: "Em andamento",

    162: "Em andamento",
    163: "Em andamento",

    176: "Em andamento",
    182: "Em andamento",  # Envolvido Adicionado
    183: "Em andamento",
    198: "Em andamento",

    206: "Em andamento",

    209: "Em andamento",
    210: "Em andamento",

    212: "Em andamento",
    213: "Em andamento",
    216: "Em andamento",

    218: "Em andamento",
    219: "Em andamento",
    224: "Em andamento",
    225: "Em andamento",
    226: "Em andamento",
    260: "Em andamento",
    301: "Em andamento",  # Certidão de Análise de Reiteração
    332: "Em andamento",  # Certidão de Agrupamento

    346: "Arquivamento por Improcedência",  # Excesso de prazo

    370: "Em andamento",  # Encaminhamento à Superintendência
    406: "Em andamento",  # Análise para instauração de PA
    419: "Em andamento",  # Habilitação de Advogado
    194: "Em andamento",
    
    # =====================================================
    # ATENDIMENTO
    # =====================================================

    407: "Atendimento Informativo",

}