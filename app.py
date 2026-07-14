import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.abt import carregar_abt
from services.dic_interacoes import CONFIG_PROCESSOS, CONFIG_TEXTOS
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
logo_path = BASE_DIR / "dashboard" / "assets" / "logo_procon.png"


# ============================================================
# FUNÇÕES UTILITÁRIAS E DE FORMATAÇÃO
# ============================================================

def formatar_serie(serie: pd.Series, fmt) -> pd.Series:
    """Aplica uma função de formatação a cada elemento de uma Series numérica."""
    if serie.empty:
        return serie.astype(str)
    return serie.map(fmt)


def verificar_e_exibir_aviso_vazio(df: pd.DataFrame, mensagem: str) -> bool:
    """Exibe um aviso caso o DataFrame esteja vazio ou sem dados numéricos relevantes."""
    if df.empty:
        st.warning(mensagem)
        return True
        
    # Se for o caso do heatmap (onde queremos ver se a soma de todos os registros é zero)
    # ou de um dataframe normal, checamos apenas as colunas numéricas
    colunas_numericas = df.select_dtypes(include=['number'])
    if not colunas_numericas.empty and colunas_numericas.to_numpy().sum() == 0:
        st.warning(mensagem)
        return True
        
    return False

# ============================================================
# FUNÇÕES DE RENDERIZAÇÃO DOS GRÁFICOS E TABELAS
# ============================================================

def renderizar_evolucao_anual(df_filtrado: pd.DataFrame, textos: dict):
    st.header(f"📈 Evolução Anual do número de {textos['processos']}")
    st.caption(f"Quantidade de {textos['processos']} por ano de abertura.")

    df_evo = (
        df_filtrado.groupby("ano_abertura")
        .size()
        .reset_index(name="quantidade")
    )
    df_evo["percentual"] = (df_evo["quantidade"] / df_evo["quantidade"].sum() * 100)
    df_evo = df_evo.sort_values("ano_abertura")
    df_evo["ano"] = df_evo["ano_abertura"].astype(str)

    if verificar_e_exibir_aviso_vazio(df_evo, f"Não existem {textos['processos']} para o período selecionado.\n\nAltere os filtros para visualizar os resultados."):
        return

    # Gráfico
    fig = go.Figure()
    fig.add_bar(
        x=df_evo["ano"],
        y=df_evo["quantidade"],
        name=f"{textos['processos']}",
        marker_color="#0B3C5D"
    )

    df_evo["hover"] = (
        "<b>Ano:</b> " + df_evo["ano_abertura"].astype(str) +
        f"<br><b>{textos['processos']}:</b> " + df_evo["quantidade"].map(lambda x: f"{x:,}".replace(",", ".")) +
        "<br><b>Percentual:</b> " + df_evo["percentual"].map(lambda x: f"{x:.2f}%")
    )

    fig.update_layout(
        template="plotly_white",
        height=450,
        font=dict(family="Times New Roman", size=14, color="black"),
        title=dict(text=f"Evolução Anual do número de {textos['processos']}", x=0.02),
        legend=dict(orientation="v", x=1.02, y=1),
        xaxis_title="Ano",
        yaxis_title="Quantidade",
        hovermode="x",
        separators=",."
    )
    fig.update_yaxes(showgrid=True, gridcolor="#E5E5E5", tickformat=",d")
    fig.update_xaxes(type="category", showgrid=False)
    fig.update_traces(hovertemplate="%{customdata}<extra></extra>", customdata=df_evo["hover"])
    
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Apoio
    df_tabela = df_evo.copy()
    df_tabela["quantidade"] = df_tabela["quantidade"].map(lambda x: f"{x:,}".replace(",", "."))
    df_tabela["percentual"] = df_tabela["percentual"].map(lambda x: f"{x:.1f}".replace(".", ",") + "%")
    df_tabela = df_tabela.rename(columns={
        "ano_abertura": "Ano",
        "quantidade": f"{textos['processos']}",
        "percentual": "Participação"
    })
    st.dataframe(df_tabela[["Ano", f"{textos['processos']}", "Participação"]], use_container_width=True, hide_index=True)


def renderizar_evolucao_semestral(df_filtrado: pd.DataFrame, textos: dict):
    st.header(f"📊 Evolução Semestral das {textos['processos']}")
    st.caption(f"Quantidade de {textos['processos']} por semestre e ano de abertura.")

    df_evo = (
        df_filtrado.groupby(["ano_abertura", "semestre_abertura"])
        .size()
        .reset_index(name="quantidade")
    )
    df_evo["percentual"] = (df_evo["quantidade"] / df_evo["quantidade"].sum() * 100)
    df_evo = df_evo.sort_values(["ano_abertura", "semestre_abertura"])
    df_evo["semestre"] = df_evo["semestre_abertura"].map({1: "1º Semestre", 2: "2º Semestre"})
    df_evo["ano"] = df_evo["ano_abertura"].astype(str)

    if verificar_e_exibir_aviso_vazio(df_evo, f"Não existem {textos['processos']} para o período selecionado.\n\nAltere os filtros para visualizar os resultados."):
        return

    # Gráfico
    fig = go.Figure()
    for sem, cod, cor in [("1º Semestre", 1, "#0B3C5D"), ("2º Semestre", 2, "#3E7CB1")]:
        fig.add_bar(
            x=df_evo.loc[df_evo["semestre_abertura"] == cod, "ano"],
            y=df_evo.loc[df_evo["semestre_abertura"] == cod, "quantidade"],
            name=sem,
            marker_color=cor
        )

    fig.update_layout(
        template="plotly_white", height=450,
        font=dict(family="Times New Roman", size=14, color="black"),
        title=dict(text=f"Evolução Semestral das {textos['processos']}", x=0.02),
        legend=dict(title="Semestre", orientation="v", x=1.02, y=1),
        xaxis_title="Ano", yaxis_title="Quantidade",
        barmode="group", hovermode="x", separators=",."
    )
    fig.update_xaxes(type="category", showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E5E5E5", tickformat=",d")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Apoio
    df_tabela = df_evo.pivot(index="ano_abertura", columns="semestre", values="quantidade")
    for col in ["1º Semestre", "2º Semestre"]:
        if col not in df_tabela.columns:
            df_tabela[col] = 0
    df_tabela = df_tabela[["1º Semestre", "2º Semestre"]].fillna(0)
    df_tabela["Total"] = df_tabela["1º Semestre"] + df_tabela["2º Semestre"]
    df_tabela["Participação"] = (df_tabela["Total"] / df_tabela["Total"].sum() * 100)

    for col in ["1º Semestre", "2º Semestre", "Total"]:
        df_tabela[col] = df_tabela[col].astype(int).map(lambda x: f"{x:,}".replace(",", "."))
    df_tabela["Participação"] = df_tabela["Participação"].map(lambda x: f"{x:.1f}".replace(".", ",") + "%")
    df_tabela = df_tabela.reset_index().rename(columns={"ano_abertura": "Ano"}).fillna(0)
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)

def renderizar_evolucao_trimestral(df_filtrado: pd.DataFrame, textos: dict):
    st.header(f"📊 Evolução Trimestral das {textos['processos']}")
    st.caption(f"Quantidade de {textos['processos']} por trimestre e ano de abertura.")

    df_evo = (
        df_filtrado
        .groupby(["ano_abertura", "trimestre_abertura"])
        .size()
        .reset_index(name="quantidade")
    )

    df_evo["percentual"] = (
        df_evo["quantidade"] / df_evo["quantidade"].sum() * 100
    )

    df_evo = df_evo.sort_values(
        ["ano_abertura", "trimestre_abertura"]
    )

    df_evo["trimestre"] = df_evo["trimestre_abertura"].map({
        1: "1º Trimestre",
        2: "2º Trimestre",
        3: "3º Trimestre",
        4: "4º Trimestre"
    })

    df_evo["ano"] = df_evo["ano_abertura"].astype(str)

    if verificar_e_exibir_aviso_vazio(
        df_evo,
        f"Não existem {textos['processos']} para o período selecionado.\n\nAltere os filtros para visualizar os resultados."
    ):
        return

    # Gráfico
    fig = go.Figure()

    cores = {
        1: "#0B3C5D",
        2: "#3E7CB1",
        3: "#6FA8DC",
        4: "#9FC5E8"
    }

    for tri in [1, 2, 3, 4]:
        fig.add_bar(
            x=df_evo.loc[df_evo["trimestre_abertura"] == tri, "ano"],
            y=df_evo.loc[df_evo["trimestre_abertura"] == tri, "quantidade"],
            name=f"{tri}º Trimestre",
            marker_color=cores[tri]
        )

    fig.update_layout(
        template="plotly_white",
        height=450,
        font=dict(
            family="Times New Roman",
            size=14,
            color="black"
        ),
        title=dict(
            text=f"Evolução Trimestral das {textos['processos']}",
            x=0.02
        ),
        legend=dict(
            title="Trimestre",
            orientation="v",
            x=1.02,
            y=1
        ),
        xaxis_title="Ano",
        yaxis_title="Quantidade",
        barmode="group",
        hovermode="x",
        separators=",."
    )

    fig.update_xaxes(
        type="category",
        showgrid=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E5E5E5",
        tickformat=",d"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabela de apoio
    df_tabela = df_evo.pivot(
        index="ano_abertura",
        columns="trimestre",
        values="quantidade"
    )

    for col in [
        "1º Trimestre",
        "2º Trimestre",
        "3º Trimestre",
        "4º Trimestre"
    ]:
        if col not in df_tabela.columns:
            df_tabela[col] = 0

    df_tabela = df_tabela[
        [
            "1º Trimestre",
            "2º Trimestre",
            "3º Trimestre",
            "4º Trimestre"
        ]
    ].fillna(0)

    df_tabela["Total"] = (
        df_tabela["1º Trimestre"] +
        df_tabela["2º Trimestre"] +
        df_tabela["3º Trimestre"] +
        df_tabela["4º Trimestre"]
    )

    df_tabela["Participação"] = (
        df_tabela["Total"] /
        df_tabela["Total"].sum() * 100
    )

    for col in [
        "1º Trimestre",
        "2º Trimestre",
        "3º Trimestre",
        "4º Trimestre",
        "Total"
    ]:
        df_tabela[col] = (
            df_tabela[col]
            .astype(int)
            .map(lambda x: f"{x:,}".replace(",", "."))
        )

    df_tabela["Participação"] = (
        df_tabela["Participação"]
        .map(lambda x: f"{x:.1f}".replace(".", ",") + "%")
    )

    df_tabela = (
        df_tabela
        .reset_index()
        .rename(columns={"ano_abertura": "Ano"})
        .fillna(0)
    )

    st.dataframe(
        df_tabela,
        use_container_width=True,
        hide_index=True
    )


def renderizar_taxa_resolucao(df_filtrado: pd.DataFrame, textos: dict):
    st.header("📈 Evolução da Taxa de Resolução")
    st.caption(f"Percentual de {textos['processos']} por semestre e ano de abertura.")

    df_taxa = (
        df_filtrado.groupby(["ano_abertura", "semestre_abertura"])
        .agg(total=("process_id", "count"), resolvidas=("processo_resolvido", "sum"))
        .reset_index()
    )
    df_taxa["taxa"] = (df_taxa["resolvidas"] / df_taxa["total"] * 100)
    df_taxa["semestre"] = df_taxa["semestre_abertura"].map({1: "1º Semestre", 2: "2º Semestre"})
    df_taxa["ano"] = df_taxa["ano_abertura"].astype(str)

    if verificar_e_exibir_aviso_vazio(df_taxa, f"Não existem {textos['processos']} para o período selecionado.\n\nAltere os filtros para visualizar os resultados."):
        return

    df_taxa_1 = df_taxa[df_taxa["semestre_abertura"] == 1].copy()
    df_taxa_2 = df_taxa[df_taxa["semestre_abertura"] == 2].copy()

    # Gráfico
    fig = go.Figure()
    for df_t, sem_nome, cor in [(df_taxa_1, "1º Semestre", "#0B3C5D"), (df_taxa_2, "2º Semestre", "#D98E04")]:
        fig.add_bar(
            x=df_t["ano"], y=df_t["taxa"], name=sem_nome, marker_color=cor,
            text=df_t["taxa"].map(lambda x: f"{x:.1f}%".replace(".", ",")), textposition="outside"
        )
        df_t["hover"] = (
            "<b>Ano:</b> " + df_t["ano"] + "<br><b>Semestre:</b> " + df_t["semestre"] +
            f"<br><b>{textos['processos']}:</b> " + formatar_serie(df_t["total"], lambda x: f"{x:,}".replace(",", ".")) +
            "<br><b>Resolvidas:</b> " + formatar_serie(df_t["resolvidas"], lambda x: f"{x:,}".replace(",", ".")) +
            "<br><b>Taxa:</b> " + formatar_serie(df_t["taxa"], lambda x: f"{x:.1f}".replace(".", ",") + "%")
        )

    fig.update_layout(
        template="plotly_white", height=450,
        font=dict(family="Times New Roman", size=14, color="black"),
        title=dict(text="Evolução da Taxa de Resolução", x=0.02),
        legend=dict(title="Semestre", orientation="v", x=1.02, y=1),
        xaxis_title="Ano", yaxis_title="Taxa de Resolução (%)",
        barmode="group", hovermode="x", separators=",."
    )
    fig.update_xaxes(type="category", showgrid=False)
    fig.update_yaxes(range=[0, 105], ticksuffix="%", showgrid=True, gridcolor="#E5E5E5")
    
    if len(fig.data) >= 2:
        fig.data[0].update(hovertemplate="%{customdata}<extra></extra>", customdata=df_taxa_1["hover"])
        fig.data[1].update(hovertemplate="%{customdata}<extra></extra>", customdata=df_taxa_2["hover"])

    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Apoio
    df_tabela = df_taxa.pivot(index="ano_abertura", columns="semestre", values="taxa")
    for col in ["1º Semestre", "2º Semestre"]:
        if col not in df_tabela.columns:
            df_tabela[col] = 0
    df_tabela = df_tabela[["1º Semestre", "2º Semestre"]].fillna(0)

    df_total = df_taxa.groupby("ano_abertura").agg(total=("total", "sum"), resolvidas=("resolvidas", "sum"))
    df_tabela["Taxa Anual"] = (df_total["resolvidas"] / df_total["total"] * 100)

    for col in ["1º Semestre", "2º Semestre", "Taxa Anual"]:
        df_tabela[col] = df_tabela[col].map(lambda x: f"{x:.1f}".replace(".", ",") + "%")
    df_tabela = df_tabela.reset_index().rename(columns={"ano_abertura": "Ano"})
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)

def renderizar_taxa_resolucao_trimestral(df_filtrado: pd.DataFrame, textos: dict):
    st.header("📈 Evolução da Taxa de Resolução Trimestral")
    st.caption(f"Percentual de {textos['processos']} por trimestre e ano de abertura.")

    df_taxa = (
        df_filtrado.groupby(["ano_abertura", "trimestre_abertura"])
        .agg(
            total=("process_id", "count"),
            resolvidas=("processo_resolvido", "sum")
        )
        .reset_index()
    )

    df_taxa["taxa"] = (
        df_taxa["resolvidas"] / df_taxa["total"] * 100
    )

    df_taxa["trimestre"] = df_taxa["trimestre_abertura"].map({
        1: "1º Trimestre",
        2: "2º Trimestre",
        3: "3º Trimestre",
        4: "4º Trimestre"
    })

    df_taxa["ano"] = df_taxa["ano_abertura"].astype(str)

    if verificar_e_exibir_aviso_vazio(
        df_taxa,
        f"Não existem {textos['processos']} para o período selecionado.\n\nAltere os filtros para visualizar os resultados."
    ):
        return


    df_taxa_1 = df_taxa[df_taxa["trimestre_abertura"] == 1].copy()
    df_taxa_2 = df_taxa[df_taxa["trimestre_abertura"] == 2].copy()
    df_taxa_3 = df_taxa[df_taxa["trimestre_abertura"] == 3].copy()
    df_taxa_4 = df_taxa[df_taxa["trimestre_abertura"] == 4].copy()


    fig = go.Figure()

    for df_t, nome, cor in [
        (df_taxa_1, "1º Trimestre", "#0B3C5D"),
        (df_taxa_2, "2º Trimestre", "#D98E04"),
        (df_taxa_3, "3º Trimestre", "#2E8B57"),
        (df_taxa_4, "4º Trimestre", "#8B4513")
    ]:

        fig.add_bar(
            x=df_t["ano"],
            y=df_t["taxa"],
            name=nome,
            marker_color=cor,
            text=df_t["taxa"].map(
                lambda x: f"{x:.1f}%".replace(".", ",")
            ),
            textposition="outside"
        )

        df_t["hover"] = (
            "<b>Ano:</b> " + df_t["ano"]
            + "<br><b>Trimestre:</b> " + df_t["trimestre"]
            + f"<br><b>{textos['processos']}:</b> "
            + formatar_serie(df_t["total"], lambda x: f"{x:,}".replace(",", "."))
            + "<br><b>Resolvidas:</b> "
            + formatar_serie(df_t["resolvidas"], lambda x: f"{x:,}".replace(",", "."))
            + "<br><b>Taxa:</b> "
            + formatar_serie(df_t["taxa"], lambda x: f"{x:.1f}".replace(".", ",") + "%")
        )


    fig.update_layout(
        template="plotly_white",
        height=450,
        font=dict(
            family="Times New Roman",
            size=14,
            color="black"
        ),
        title=dict(
            text="Evolução Trimestral da Taxa de Resolução",
            x=0.02
        ),
        legend=dict(
            title="Trimestre",
            orientation="v",
            x=1.02,
            y=1
        ),
        xaxis_title="Ano",
        yaxis_title="Taxa de Resolução (%)",
        barmode="group",
        hovermode="x",
        separators=",."
    )

    fig.update_xaxes(
        type="category",
        showgrid=False
    )

    fig.update_yaxes(
        range=[0, 105],
        ticksuffix="%",
        showgrid=True,
        gridcolor="#E5E5E5"
    )


    textos_hover = [
        df_taxa_1,
        df_taxa_2,
        df_taxa_3,
        df_taxa_4
    ]

    for i, df_t in enumerate(textos_hover):
        if i < len(fig.data):
            fig.data[i].update(
                hovertemplate="%{customdata}<extra></extra>",
                customdata=df_t["hover"]
            )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # Tabela de apoio

    df_tabela = df_taxa.pivot(
        index="ano_abertura",
        columns="trimestre_abertura",
        values="taxa"
    )

    for col in [1, 2, 3, 4]:
        if col not in df_tabela.columns:
            df_tabela[col] = 0

    df_tabela = df_tabela[[1, 2, 3, 4]].fillna(0)

    df_total = (
        df_taxa.groupby("ano_abertura")
        .agg(
            total=("total", "sum"),
            resolvidas=("resolvidas", "sum")
        )
    )

    df_tabela["Taxa Anual"] = (
        df_total["resolvidas"] /
        df_total["total"] * 100
    )

    df_tabela.columns = [
        "1º Trimestre",
        "2º Trimestre",
        "3º Trimestre",
        "4º Trimestre",
        "Taxa Anual"
    ]

    for col in df_tabela.columns:
        df_tabela[col] = df_tabela[col].map(
            lambda x: f"{x:.1f}".replace(".", ",") + "%"
        )

    df_tabela = (
        df_tabela
        .reset_index()
        .rename(columns={"ano_abertura": "Ano"})
    )

    st.dataframe(
        df_tabela,
        use_container_width=True,
        hide_index=True
    )


def renderizar_tempo_medio_resolucao(df_filtrado: pd.DataFrame, textos: dict):
    st.header("⏳ Evolução do Tempo Médio e Mediano de Resolução")
    st.caption(f"Tempo médio e mediano entre a abertura da {textos['processos']} e sua resolução, por semestre e ano.")

    df_resolvidos_filtrado = df_filtrado[df_filtrado["processo_resolvido"] == 1]

    df_tempo = (
        df_resolvidos_filtrado
        .groupby(["ano_abertura", "semestre_abertura"])
        .agg(tempo_medio=("dias_ate_resolucao", "mean"), mediana=("dias_ate_resolucao", "median"), quantidade=("process_id", "count"))
        .reset_index()
    )
    df_tempo["semestre"] = df_tempo["semestre_abertura"].map({1: "1º Semestre", 2: "2º Semestre"})
    df_tempo["ano"] = df_tempo["ano_abertura"].astype(str)

    if verificar_e_exibir_aviso_vazio(df_tempo, "Não existem processos resolvidos para o período selecionado.\n\nAltere os filtros para visualizar os resultados."):
        return

    df_tempo_1 = df_tempo[df_tempo["semestre_abertura"] == 1].copy()
    df_tempo_2 = df_tempo[df_tempo["semestre_abertura"] == 2].copy()

    # Gráfico - barras duplas: Média (sólida) e Mediana (hachurada), cor identifica o semestre
    fig = go.Figure()
    config_semestres = [(1, "1º Semestre", "#0B3C5D", df_tempo_1), (2, "2º Semestre", "#D98E04", df_tempo_2)]

    for sem, nome, cor, df_t in config_semestres:
        df_t["hover"] = (
            "<b>Ano:</b> " + df_t["ano"] + "<br><b>Semestre:</b> " + df_t["semestre"] +
            "<br><b>Tempo médio:</b> " + formatar_serie(df_t["tempo_medio"], lambda x: f"{x:.1f}".replace(".", ",") + " dias") +
            "<br><b>Mediana:</b> " + formatar_serie(df_t["mediana"], lambda x: f"{x:.1f}".replace(".", ",") + " dias") +
            "<br><b>Processos resolvidos:</b> " + formatar_serie(df_t["quantidade"], lambda x: f"{x:,}".replace(",", "."))
        )

        fig.add_bar(
            x=df_t["ano"], y=df_t["tempo_medio"], name=f"{nome} - Média",
            marker=dict(color=cor),
            text=df_t["tempo_medio"].map(lambda x: f"{x:.1f}".replace(".", ",")), textposition="outside",
            legendgroup=nome,
            hovertemplate="%{customdata}<extra></extra>", customdata=df_t["hover"]
        )
        fig.add_bar(
            x=df_t["ano"], y=df_t["mediana"], name=f"{nome} - Mediana",
            marker=dict(color=cor, pattern=dict(shape="/", fgcolor="white", size=6)),
            text=df_t["mediana"].map(lambda x: f"{x:.1f}".replace(".", ",")), textposition="outside",
            legendgroup=nome,
            hovertemplate="%{customdata}<extra></extra>", customdata=df_t["hover"]
        )

    fig.update_layout(
        template="plotly_white", height=480,
        font=dict(family="Times New Roman", size=14, color="black"),
        title=dict(text="Evolução do Tempo Médio e Mediano de Resolução", x=0.02),
        legend=dict(title="Semestre / Métrica", orientation="v", x=1.02, y=1),
        xaxis_title="Ano", yaxis_title="Tempo (dias)",
        barmode="group", hovermode="x", separators=",."
    )
    fig.update_xaxes(type="category", showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E5E5E5")

    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Apoio - Média e Mediana por semestre, lado a lado
    df_tabela_media = df_tempo.pivot(index="ano_abertura", columns="semestre", values="tempo_medio")
    df_tabela_mediana = df_tempo.pivot(index="ano_abertura", columns="semestre", values="mediana")
    for col in ["1º Semestre", "2º Semestre"]:
        if col not in df_tabela_media.columns:
            df_tabela_media[col] = 0
        if col not in df_tabela_mediana.columns:
            df_tabela_mediana[col] = 0
    df_tabela_media = df_tabela_media[["1º Semestre", "2º Semestre"]].fillna(0)
    df_tabela_mediana = df_tabela_mediana[["1º Semestre", "2º Semestre"]].fillna(0)

    df_tabela = pd.DataFrame(index=df_tabela_media.index)
    df_tabela["1º Semestre (Média)"] = df_tabela_media["1º Semestre"]
    df_tabela["1º Semestre (Mediana)"] = df_tabela_mediana["1º Semestre"]
    df_tabela["2º Semestre (Média)"] = df_tabela_media["2º Semestre"]
    df_tabela["2º Semestre (Mediana)"] = df_tabela_mediana["2º Semestre"]

    # Média e mediana anuais calculadas direto dos dados brutos (não a partir das médias por semestre),
    # garantindo o valor correto mesmo quando os semestres têm quantidades diferentes de processos.
    df_total = (
        df_resolvidos_filtrado
        .groupby("ano_abertura")
        .agg(
            media_anual=("dias_ate_resolucao", "mean"),
            mediana_anual=("dias_ate_resolucao", "median"),
            resolvidos=("process_id", "count"),
        )
    )
    df_tabela["Média Anual"] = df_total["media_anual"]
    df_tabela["Mediana Anual"] = df_total["mediana_anual"]
    df_tabela["Resolvidos"] = df_total["resolvidos"]

    colunas_dias = [
        "1º Semestre (Média)", "1º Semestre (Mediana)",
        "2º Semestre (Média)", "2º Semestre (Mediana)",
        "Média Anual", "Mediana Anual",
    ]
    for col in colunas_dias:
        df_tabela[col] = df_tabela[col].map(lambda x: f"{x:.1f}".replace(".", ",") + " dias")
    df_tabela["Resolvidos"] = df_tabela["Resolvidos"].astype(int).map(lambda x: f"{x:,}".replace(",", "."))
    df_tabela = df_tabela.reset_index().rename(columns={"ano_abertura": "Ano"})
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)

def renderizar_tempo_medio_resolucao_trimestral(df_filtrado: pd.DataFrame, textos: dict):
    st.header("⏳ Evolução do Tempo Médio e Mediano de Resolução Trimestral")
    st.caption(f"Tempo médio e mediano entre a abertura da {textos['processos']} e sua resolução, por trimestre e ano.")

    df_resolvidos_filtrado = df_filtrado[df_filtrado["processo_resolvido"] == 1]

    df_tempo = (
        df_resolvidos_filtrado
        .groupby(["ano_abertura", "trimestre_abertura"])
        .agg(
            tempo_medio=("dias_ate_resolucao", "mean"),
            mediana=("dias_ate_resolucao", "median"),
            quantidade=("process_id", "count")
        )
        .reset_index()
    )

    df_tempo["trimestre"] = df_tempo["trimestre_abertura"].map({
        1: "1º Trimestre", 2: "2º Trimestre", 3: "3º Trimestre", 4: "4º Trimestre"
    })
    df_tempo["ano"] = df_tempo["ano_abertura"].astype(str)

    if verificar_e_exibir_aviso_vazio(
        df_tempo,
        "Não existem processos resolvidos para o período selecionado.\n\nAltere os filtros para visualizar os resultados."
    ):
        return

    df_tempo_1 = df_tempo[df_tempo["trimestre_abertura"] == 1].copy()
    df_tempo_2 = df_tempo[df_tempo["trimestre_abertura"] == 2].copy()
    df_tempo_3 = df_tempo[df_tempo["trimestre_abertura"] == 3].copy()
    df_tempo_4 = df_tempo[df_tempo["trimestre_abertura"] == 4].copy()

    # Gráfico - barras duplas: Média (sólida) e Mediana (hachurada), cor identifica o trimestre
    fig = go.Figure()
    config_trimestres = [
        (1, "1º Trimestre", "#0B3C5D", df_tempo_1),
        (2, "2º Trimestre", "#D98E04", df_tempo_2),
        (3, "3º Trimestre", "#2E8B57", df_tempo_3),
        (4, "4º Trimestre", "#8B4513", df_tempo_4),
    ]

    for tri, nome, cor, df_t in config_trimestres:
        df_t["hover"] = (
            "<b>Ano:</b> " + df_t["ano"]
            + "<br><b>Trimestre:</b> " + df_t["trimestre"]
            + "<br><b>Tempo médio:</b> " + formatar_serie(df_t["tempo_medio"], lambda x: f"{x:.1f}".replace(".", ",") + " dias")
            + "<br><b>Mediana:</b> " + formatar_serie(df_t["mediana"], lambda x: f"{x:.1f}".replace(".", ",") + " dias")
            + "<br><b>Processos resolvidos:</b> " + formatar_serie(df_t["quantidade"], lambda x: f"{x:,}".replace(",", "."))
        )

        fig.add_bar(
            x=df_t["ano"], y=df_t["tempo_medio"], name=f"{nome} - Média",
            marker=dict(color=cor),
            text=df_t["tempo_medio"].map(lambda x: f"{x:.1f}".replace(".", ",")), textposition="outside",
            legendgroup=nome,
            hovertemplate="%{customdata}<extra></extra>", customdata=df_t["hover"]
        )
        fig.add_bar(
            x=df_t["ano"], y=df_t["mediana"], name=f"{nome} - Mediana",
            marker=dict(color=cor, pattern=dict(shape="/", fgcolor="white", size=6)),
            text=df_t["mediana"].map(lambda x: f"{x:.1f}".replace(".", ",")), textposition="outside",
            legendgroup=nome,
            hovertemplate="%{customdata}<extra></extra>", customdata=df_t["hover"]
        )

    fig.update_layout(
        template="plotly_white", height=500,
        font=dict(family="Times New Roman", size=14, color="black"),
        title=dict(text="Evolução Trimestral do Tempo Médio e Mediano de Resolução", x=0.02),
        legend=dict(title="Trimestre / Métrica", orientation="v", x=1.02, y=1),
        xaxis_title="Ano", yaxis_title="Tempo (dias)",
        barmode="group", hovermode="x", separators=",."
    )
    fig.update_xaxes(type="category", showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E5E5E5")

    st.plotly_chart(fig, use_container_width=True)

    # Tabela de apoio - Média e Mediana por trimestre, lado a lado
    df_tabela_media = df_tempo.pivot(index="ano_abertura", columns="trimestre_abertura", values="tempo_medio")
    df_tabela_mediana = df_tempo.pivot(index="ano_abertura", columns="trimestre_abertura", values="mediana")
    for col in [1, 2, 3, 4]:
        if col not in df_tabela_media.columns:
            df_tabela_media[col] = 0
        if col not in df_tabela_mediana.columns:
            df_tabela_mediana[col] = 0
    df_tabela_media = df_tabela_media[[1, 2, 3, 4]].fillna(0)
    df_tabela_mediana = df_tabela_mediana[[1, 2, 3, 4]].fillna(0)

    df_tabela = pd.DataFrame(index=df_tabela_media.index)
    nomes_trimestre = {1: "1º Trimestre", 2: "2º Trimestre", 3: "3º Trimestre", 4: "4º Trimestre"}
    for tri, nome in nomes_trimestre.items():
        df_tabela[f"{nome} (Média)"] = df_tabela_media[tri]
        df_tabela[f"{nome} (Mediana)"] = df_tabela_mediana[tri]

    # Média e mediana anuais calculadas direto dos dados brutos (não a partir das médias por trimestre),
    # garantindo o valor correto mesmo quando os trimestres têm quantidades diferentes de processos.
    df_total = (
        df_resolvidos_filtrado
        .groupby("ano_abertura")
        .agg(
            media_anual=("dias_ate_resolucao", "mean"),
            mediana_anual=("dias_ate_resolucao", "median"),
            resolvidos=("process_id", "count"),
        )
    )
    df_tabela["Média Anual"] = df_total["media_anual"]
    df_tabela["Mediana Anual"] = df_total["mediana_anual"]
    df_tabela["Resolvidos"] = df_total["resolvidos"]

    colunas_dias = [f"{nome} (Média)" for nome in nomes_trimestre.values()] + \
                   [f"{nome} (Mediana)" for nome in nomes_trimestre.values()] + \
                   ["Média Anual", "Mediana Anual"]
    for col in colunas_dias:
        df_tabela[col] = df_tabela[col].map(lambda x: f"{x:.1f}".replace(".", ",") + " dias")
    df_tabela["Resolvidos"] = df_tabela["Resolvidos"].astype(int).map(lambda x: f"{x:,}".replace(",", "."))

    df_tabela = df_tabela.reset_index().rename(columns={"ano_abertura": "Ano"})
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)

def renderizar_distribuicao_tempo(df_filtrado: pd.DataFrame, textos: dict):
    st.header(f"⏳ Distribuição do Tempo de Resolução de {textos['processos']}")
    st.caption(f"Distribuição das {textos['processos'].lower()} resolvidas por faixa de tempo.")

    df_dist = (
        df_filtrado[df_filtrado["processo_resolvido"] == 1]
        .groupby("faixa_tempo_resolucao")
        .size()
        .reset_index(name="quantidade")
    )
    ordem_faixas = ["Mesmo dia", "1–7 dias", "8–15 dias", "16–30 dias", "31–60 dias", "61–90 dias", "91–180 dias", "Acima de 180 dias"]
    df_dist["faixa_tempo_resolucao"] = pd.Categorical(df_dist["faixa_tempo_resolucao"], categories=ordem_faixas, ordered=True)
    df_dist = df_dist.sort_values("faixa_tempo_resolucao")
    df_dist["percentual"] = (df_dist["quantidade"] / df_dist["quantidade"].sum() * 100)

    if verificar_e_exibir_aviso_vazio(df_dist, "Não existem processos resolvidos para o período selecionado.\n\nAltere os filtros para visualizar os resultados."):
        return

    fig = go.Figure()
    fig.add_bar(
        y=df_dist["faixa_tempo_resolucao"], x=df_dist["quantidade"],
        orientation="h", marker_color="#0B3C5D", text=df_dist["quantidade"], textposition="outside"
    )
    fig.update_traces(
        textfont=dict(family="Times New Roman", size=12, color="black"),
        hovertemplate=f"<b>{textos['processos']}:</b> %{{x}}<br><b>Tempo resolução:</b> %{{y}}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white", height=650,
        font=dict(family="Times New Roman", size=14, color="black"),
        title=dict(text=f"Distribuição do tempo de resolução de {textos['processos']}", x=0.02),
        coloraxis_colorbar=dict(title=f"{textos['processos']}")
    )
    st.plotly_chart(fig, use_container_width=True)


def renderizar_heatmap_mensal(df_filtrado: pd.DataFrame, textos: dict):
    st.header(f"📅 Distribuição Mensal de {textos['processos']}")
    st.caption(f"Quantidade de {textos['processos']} por mês e ano de abertura.")

    df_heat = df_filtrado.groupby(["ano_abertura", "mes_abertura"]).size().reset_index(name="quantidade")
    df_heat = df_heat.pivot(index="mes_abertura", columns="ano_abertura", values="quantidade").reindex(range(1, 13)).fillna(0)
    df_heat.columns = df_heat.columns.astype(str)

    meses = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    df_heat.index = df_heat.index.map(meses)

    if verificar_e_exibir_aviso_vazio(df_heat, f"Não existem {textos['processos']} para o período selecionado.\n\nAltere os filtros para visualizar os resultados."):
        return

    fig = px.imshow(
        df_heat, text_auto=".0f", aspect="auto",
        color_continuous_scale=[[0.00, "#FFFFFF"], [0.30, "#D6EAF8"], [0.60, "#5DADE2"], [1.00, "#0B3C5D"]],
        labels=dict(x="Ano", y="Mês", color=f"{textos['processos']}")
    )
    fig.update_traces(
        textfont=dict(family="Times New Roman", size=12, color="black"),
        hovertemplate="<b>Ano:</b> %{x}<br><b>Mês:</b> %{y}" + f"<br><b>{textos['processos']}:</b> %{{z:,.0f}}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white", height=650,
        font=dict(family="Times New Roman", size=14, color="black"),
        title=dict(text=f"Distribuição Mensal das {textos['processos']}", x=0.02),
        coloraxis_colorbar=dict(title=f"{textos['processos']}")
    )
    st.plotly_chart(fig, use_container_width=True)

def renderizar_top_motivos_encerramento(df_filtrado: pd.DataFrame, textos: dict):
    st.header(f"🏆 Top 10 Movimentações Finais de {textos['processos']}")
    st.caption(
        f"Principais categorias de últimas interações de {textos['processos_min']}."
    )

    # Agrupa pela categoria gerencial criada na ABT
    df_motivos = (
        df_filtrado
        .groupby("categoria_encerramento")
        .size()
        .reset_index(name="quantidade")
    )

    # Ordena e mantém apenas os 10 maiores
    df_motivos = (
        df_motivos
        .sort_values("quantidade", ascending=False)
        .head(10)
    )

    #Calcula o percentual de cada motivo
    df_motivos["percentual"] = (
    df_motivos["quantidade"]
    / df_motivos["quantidade"].sum()
    * 100
    )

    # Para gráfico horizontal (maior no topo)
    df_grafico = df_motivos.sort_values("quantidade", ascending=True)

    if verificar_e_exibir_aviso_vazio(
        df_motivos,
        "Não existem dados de movimentações finais para os filtros selecionados."
    ):
        return

    fig = go.Figure()

    fig.add_bar(
        y=df_grafico["categoria_encerramento"],
        x=df_grafico["quantidade"],
        orientation="h",
        marker_color="#3E7CB1",
        text=df_grafico["quantidade"],
        textposition="outside"
    )

    fig.update_traces(
    textfont=dict(
        family="Times New Roman",
        size=12,
        color="black"
    ),
    customdata=df_grafico["percentual"],
    hovertemplate=
        "<b>Motivo:</b> %{y}"
        "<br><b>Quantidade:</b> %{x:,.0f}"
        "<br><b>Participação:</b> %{customdata:.1f}%"
        "<extra></extra>"
    )

    fig.update_layout(
        template="plotly_white",
        height=500,
        font=dict(
            family="Times New Roman",
            size=14,
            color="black"
        ),
        title=dict(
            text=f"Principais movimentações finais de ({textos['processos']})",
            x=0.02
        ),
        xaxis_title="Quantidade de Processos",
        yaxis_title="Categoria de movimentação",
        margin=dict(l=250)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E5E5E5"
    )

    st.plotly_chart(fig, use_container_width=True)
# ============================================================
# EXECUÇÃO PRINCIPAL DO APP STREAMLIT
# ============================================================

# Configurações básicas da página
st.set_page_config(page_title="Painel Procon", page_icon=None, layout="wide", initial_sidebar_state="expanded")

# Sidebar - Tipo de Processo
tipo_processo = st.sidebar.selectbox("Tipo de Processo", list(CONFIG_PROCESSOS.keys()))
config = CONFIG_PROCESSOS[tipo_processo]
textos = CONFIG_TEXTOS[tipo_processo]

# Carregamento da ABT
df = carregar_abt(config["interacoes_abertura"], config["mapa_origem"])

# Cabeçalho da página
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    st.image(logo_path)
with col_titulo:
    st.title("PROCON MUNICIPAL DE UBERLÂNDIA")
    st.subheader("Painel Analítico Geral dos Processos")

st.divider()

# Sidebar - Filtros Dinâmicos
st.sidebar.header("🔎 Filtros")
ano = st.sidebar.selectbox("📅 Ano", ["Todos"] + sorted(df["ano_abertura"].dropna().unique().tolist()))

# Período: substitui os antigos seletores em cascata de Semestre/Trimestre.
# Um único seletor cobre trimestre OU semestre, evitando a dependência entre filtros.
OPCOES_PERIODO = [
    "Todos",
    "1º Trimestre", "2º Trimestre", "3º Trimestre", "4º Trimestre",
    "1º Semestre", "2º Semestre",
]
periodo = st.sidebar.selectbox("📆 Período", OPCOES_PERIODO)

origem = st.sidebar.selectbox("🔄 Abertura/Conversão", ["Todos"] + sorted(df["origem_reclamacao"].dropna().unique().tolist()))
situacao = st.sidebar.selectbox("✅ Situação", ["Todos", "Resolvida", "Não Resolvida"])

# Mapas de tradução do período escolhido para os campos reais da base
MAPA_TRIMESTRE = {"1º Trimestre": 1, "2º Trimestre": 2, "3º Trimestre": 3, "4º Trimestre": 4}
MAPA_SEMESTRE = {"1º Semestre": 1, "2º Semestre": 2}

# Aplicação de Filtros
df_filtrado = df.copy()
if ano != "Todos":
    df_filtrado = df_filtrado[df_filtrado["ano_abertura"] == ano]

if periodo in MAPA_TRIMESTRE:
    df_filtrado = df_filtrado[df_filtrado["trimestre_abertura"] == MAPA_TRIMESTRE[periodo]]
elif periodo in MAPA_SEMESTRE:
    df_filtrado = df_filtrado[df_filtrado["semestre_abertura"] == MAPA_SEMESTRE[periodo]]

if origem != "Todos":
    df_filtrado = df_filtrado[df_filtrado["origem_reclamacao"] == origem]
if situacao == "Resolvida":
    df_filtrado = df_filtrado[df_filtrado["processo_resolvido"] == 1]
elif situacao == "Não Resolvida":
    df_filtrado = df_filtrado[df_filtrado["processo_resolvido"] == 0]

# Define a granularidade dos gráficos de evolução/taxa/tempo:
# - Semestral: só quando Ano = Todos e Período = Todos (visão mais "zoom out")
# - Trimestral: em qualquer outro caso (ano específico e/ou período específico selecionado)
if ano == "Todos" and periodo == "Todos":
    granularidade = "semestral"
else:
    granularidade = "trimestral"

# Cálculo de KPIs Básicos
total = len(df_filtrado)
resolvidas = len(df_filtrado[df_filtrado["processo_resolvido"] == 1])
taxa_resolucao = (resolvidas / total) * 100 if total > 0 else 0
df_resolvidos = df_filtrado[df_filtrado["processo_resolvido"] == 1]

# Renderização de KPIs
st.markdown("### Indicadores gerais")
col1, col2, col3, col4 = st.columns(4)
col1.metric(f"📄 Total de {textos['processos']}", f"{total:,}".replace(",", "."))
col2.metric(f"✅ {textos['processos']} Resolvidas", f"{resolvidas:,}".replace(",", "."))
col3.metric("📊 Taxa de Resolução", f"{taxa_resolucao:.2f}%")

tempo_medio = df_resolvidos["dias_ate_resolucao"].mean()
valor_tempo = "-" if pd.isna(tempo_medio) else f"{tempo_medio:.1f} dias"
col4.metric(label="⏳ Tempo Médio de Resolução", value=valor_tempo)

st.markdown("### Indicadores de tempo de resolução")
col5, col6, col7 = st.columns(3)

mediana = df_resolvidos["dias_ate_resolucao"].median()
valor_mediana = "-" if pd.isna(mediana) else f"{mediana:.1f} dias"
col5.metric(label="📌 Tempo Mediano", value=valor_mediana, help=f"Metade das {textos['processos']} são resolvidas neste tempo.")

percentil90 = df_resolvidos["dias_ate_resolucao"].quantile(0.90)
valor_p90 = "-" if pd.isna(percentil90) else f"{percentil90:.1f} dias"
col6.metric(label="📌 Percentil 90", value=valor_p90, help=f"90% das {textos['processos']} são resolvidas neste tempo.")

tempo_maximo = df_resolvidos["dias_ate_resolucao"].max()
valor_max = "-" if pd.isna(tempo_maximo) else f"{tempo_maximo:.1f} dias"
col7.metric(label="📌 Tempo máximo", value=valor_max, help=f"Tempo de resolução mais longo entre todas as {textos['processos']} resolvidas")

st.divider()

# RENDERIZAÇÃO DAS SEÇÕES REFACTORADAS DE GRÁFICOS
renderizar_evolucao_anual(df_filtrado, textos)

if granularidade == "semestral":
    renderizar_evolucao_semestral(df_filtrado, textos)
    renderizar_taxa_resolucao(df_filtrado, textos)
    renderizar_tempo_medio_resolucao(df_filtrado, textos)
else:
    renderizar_evolucao_trimestral(df_filtrado, textos)
    renderizar_taxa_resolucao_trimestral(df_filtrado, textos)
    renderizar_tempo_medio_resolucao_trimestral(df_filtrado, textos)

renderizar_distribuicao_tempo(df_filtrado, textos)
renderizar_heatmap_mensal(df_filtrado, textos)
renderizar_top_motivos_encerramento(df_filtrado, textos)