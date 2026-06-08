from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("f1.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# HOME PAGE
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# DRIVERS (INTERACTIVE + FILTER)
# -------------------------
@app.route("/drivers")
def drivers():
    year = request.args.get("year")

    conn = get_db_connection()

    query = """
        SELECT d.forename, d.surname, COUNT(*) AS wins
        FROM results r
        JOIN drivers d ON r.driverId = d.driverId
        JOIN races ra ON r.raceId = ra.raceId
        WHERE r.position = 1
    """

    params = []

    if year:
        query += " AND ra.year = ?"
        params.append(year)

    query += """
        GROUP BY r.driverId
        ORDER BY wins DESC
        LIMIT 10;
    """

    data = conn.execute(query, params).fetchall()
    conn.close()

    labels = [f"{d['forename']} {d['surname']}" for d in data]
    values = [d['wins'] for d in data]

    return render_template(
        "drivers.html",
        data=data,
        labels=labels,
        values=values,
        year=year
    )


# -------------------------
# CONSTRUCTORS
# -------------------------
@app.route("/constructors")
def constructors():
    year = request.args.get("year")

    conn = get_db_connection()

    query = """
        SELECT c.name, COUNT(*) AS wins
        FROM results r
        JOIN constructors c ON r.constructorId = c.constructorId
        JOIN races ra ON r.raceId = ra.raceId
        WHERE r.position = 1
    """

    params = []

    if year:
        query += " AND ra.year = ?"
        params.append(year)

    query += """
        GROUP BY c.constructorId
        ORDER BY wins DESC;
    """

    data = conn.execute(query, params).fetchall()
    conn.close()

    labels = [row["name"] for row in data]
    values = [row["wins"] for row in data]

    return render_template(
        "constructors.html",
        data=data,
        labels=labels,
        values=values,
        year=year
    )

@app.route("/query-builder", methods=["GET"])
def query_builder():

    metric = request.args.get("metric")
    group_by = request.args.get("group_by")
    year = request.args.get("year")

    conn = get_db_connection()

    # -----------------------------
    # MAP USER INPUT → SQL PIECES
    # -----------------------------

    metric_sql = {
        "wins": "COUNT(CASE WHEN r.position = 1 THEN 1 END)",
        "avg_finish": "AVG(r.positionOrder)",
        "races": "COUNT(*)"
    }.get(metric, "COUNT(*)")

    group_sql = {
        "driver": "d.driverId, d.forename, d.surname",
        "constructor": "c.constructorId, c.name",
        "circuit": "ci.circuitId, ci.name"
    }.get(group_by, "d.driverId")

    select_name = {
        "driver": "d.forename || ' ' || d.surname",
        "constructor": "c.name",
        "circuit": "ci.name"
    }.get(group_by, "d.forename || ' ' || d.surname")

    query = f"""
        SELECT {select_name} AS name,
               {metric_sql} AS value
        FROM results r
        JOIN drivers d ON r.driverId = d.driverId
        JOIN races ra ON r.raceId = ra.raceId
        JOIN constructors c ON r.constructorId = c.constructorId
        JOIN circuits ci ON ra.circuitId = ci.circuitId
        WHERE 1=1
    """

    params = []

    if year:
        query += " AND ra.year = ?"
        params.append(year)

    query += f" GROUP BY {group_sql} ORDER BY value DESC LIMIT 10"

    data = conn.execute(query, params).fetchall()
    conn.close()

    labels = [row["name"] for row in data]
    values = [row["value"] for row in data]

    return render_template(
        "query_builder.html",
        data=data,
        labels=labels,
        values=values,
        metric=metric,
        group_by=group_by,
        year=year
    )

# -------------------------
# CIRCUITS
# -------------------------
@app.route("/circuits")
def circuits():
    circuit_id = request.args.get("circuit_id")

    conn = get_db_connection()

    # dropdown list
    circuits_list = conn.execute("""
        SELECT circuitId, name
        FROM circuits
        ORDER BY name;
    """).fetchall()

    # default: overall circuit ranking
    base_query = """
        SELECT ci.circuitId, ci.name,
               AVG(r.positionOrder) AS avg_finish,
               COUNT(*) AS total_results
        FROM results r
        JOIN races ra ON r.raceId = ra.raceId
        JOIN circuits ci ON ra.circuitId = ci.circuitId
    """

    params = []

    if circuit_id:
        base_query += " WHERE ci.circuitId = ?"
        params.append(circuit_id)

    base_query += """
        GROUP BY ci.circuitId
        ORDER BY avg_finish ASC;
    """

    data = conn.execute(base_query, params).fetchall()

    # 🧠 INSIGHT PANEL (only if circuit selected)
    insight = None

    if circuit_id:
        insight = conn.execute("""
            SELECT 
                ci.name,
                AVG(r.positionOrder) AS avg_finish,
                COUNT(r.resultId) AS total_races
            FROM results r
            JOIN races ra ON r.raceId = ra.raceId
            JOIN circuits ci ON ra.circuitId = ci.circuitId
            WHERE ci.circuitId = ?
        """, (circuit_id,)).fetchone()

    conn.close()

    labels = [r["name"] for r in data]
    values = [r["avg_finish"] for r in data]

    return render_template(
        "circuits.html",
        circuits_list=circuits_list,
        data=data,
        labels=labels,
        values=values,
        circuit_id=circuit_id,
        insight=insight
    )


if __name__ == "__main__":
    app.run(debug=True)