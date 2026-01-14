import psycopg2
import pandas as pd
import streamlit as st
import plotly.express as px


# -----------------------------
# 1) DB-Verbindung
# -----------------------------
def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        database="pagila_dwh",
        user="postgres",
        password="admin",
        port=5432
    )


# -----------------------------
# 2) Hilfsfunktion: SQL -> DataFrame
# -----------------------------
def query_df(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
        return pd.DataFrame(rows, columns=cols)
    finally:
        conn.close()


# -----------------------------
# 3) Streamlit UI
# -----------------------------
st.title("Pagila DWH Reporting")
st.write("Reports from `vw_rental_analysis`")


# =========================================================
# REPORT 1: Rentals by Film Category (Bar Chart)
# =========================================================
st.header("Report 1: Rentals by Film Category (Bar Chart)")

metric1 = st.selectbox(
    "Report 1 – Y-Axis",
    ["rentals", "revenue"],
    format_func=lambda x: "Total Rentals" if x == "rentals" else "Total Revenue"
)

if metric1 == "rentals":
    sql1 = """
        SELECT film_category, COUNT(*) AS value
        FROM vw_rental_analysis
        GROUP BY film_category
        ORDER BY value DESC;
    """
else:
    sql1 = """
        SELECT film_category, SUM(rental_amount) AS value
        FROM vw_rental_analysis
        GROUP BY film_category
        ORDER BY value DESC;
    """

df1 = query_df(sql1)

fig1 = px.bar(df1, x="film_category", y="value")
st.plotly_chart(fig1, width="stretch")
st.dataframe(df1)


# =========================================================
# REPORT 2: Rental Trends Over Time (Line Chart)
# =========================================================
st.header("Report 2: Rental Trends Over Time (Line Chart)")

metric2 = st.selectbox(
    "Report 2 – Y-Axis",
    ["rentals", "revenue"],
    format_func=lambda x: "Number of Rentals" if x == "rentals" else "Total Revenue"
)

if metric2 == "rentals":
    sql2 = """
        SELECT year, month, month_name, COUNT(*) AS value
        FROM vw_rental_analysis
        GROUP BY year, month, month_name
        ORDER BY year, month;
    """
else:
    sql2 = """
        SELECT year, month, month_name, SUM(rental_amount) AS value
        FROM vw_rental_analysis
        GROUP BY year, month, month_name
        ORDER BY year, month;
    """

df2 = query_df(sql2)

# X-Achse als lesbarer Label "YYYY-MM"
df2["time"] = df2["year"].astype(str) + "-" + df2["month"].astype(str).str.zfill(2)

fig2 = px.line(df2, x="time", y="value")
st.plotly_chart(fig2, width="stretch")
st.dataframe(df2)
