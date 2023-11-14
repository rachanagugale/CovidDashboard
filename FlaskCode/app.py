import cx_Oracle
import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

load_dotenv()

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Database connection settings
dsn = cx_Oracle.makedsn('oracle.cise.ufl.edu', '1521', service_name='orcl')
db_username = DB_USERNAME
db_password = DB_PASSWORD


# Healthcare stocks vs hospitalizations - returns 34 records
@app.route('/query3', methods=['GET'])
def query3():
    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()

    query = """WITH MonthlyNewCases AS (
        SELECT 
            EXTRACT(MONTH FROM DATE_KEY) AS month,
            EXTRACT(YEAR FROM DATE_KEY) AS year,
            SUM(NEW_CONFIRMED) AS total_monthly_new_cases
        FROM 
            RGUGALE.US_EPIDEMIOLOGY
        GROUP BY 
            EXTRACT(MONTH FROM DATE_KEY), EXTRACT(YEAR FROM DATE_KEY)
    )
    SELECT 
        TRUNC(TO_DATE('01-' || LPAD(CAST(M.month AS VARCHAR2(2)), 2, '0') || '-' || CAST(M.year AS VARCHAR2(4)), 'DD-MM-YYYY'), 'MONTH') AS month_year,
        M.total_monthly_new_cases AS monthly_new_cases,
        AVG(S.CLOSE) AS avg_stock_prices, -- Stocks price
        AVG(H.NEW_INTENSIVE_CARE_PATIENTS) AS icu_patients
    FROM 
        MonthlyNewCases M
    LEFT JOIN 
        RGUGALE.STOCKS S ON M.month = EXTRACT(MONTH FROM S.DATE_KEY) AND M.year = EXTRACT(YEAR FROM S.DATE_KEY)
    LEFT JOIN
        "AMMAR.AMJAD".HOSPITALIZATIONS H ON M.month = EXTRACT(MONTH FROM H.DATE_KEY) AND M.year = EXTRACT(YEAR FROM H.DATE_KEY)
    GROUP BY 
        M.month, M.year, M.total_monthly_new_cases
    ORDER BY 
        M.year, M.month"""

    cursor.execute(query)
    result = cursor.fetchall()

    res_list = []
    for row in result:
        data = {
            "date": row[0],
            "monthly_new_cases": row[1],
            "avg_stock_prices": row[2],
            "icu_patients": row[3]
        }
        res_list.append(data)

    print(len(result))
    cursor.close()
    connection.close()

    return jsonify(res_list)


# Government stringency measures - returns 28k records
@app.route('/query4', methods=['GET'])
def query4():
    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()

    query = """WITH VaccinationRate AS (
        SELECT 
            date_key,
            location_key,
            SUM(new_persons_vaccinated) OVER (PARTITION BY location_key ORDER BY date_key ASC) AS rolling_sum_vaccinated,
            AVG(new_persons_vaccinated) OVER (PARTITION BY location_key ORDER BY date_key ASC ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS Weekly_day_avg_vaccinated
        FROM
            RGUGALE.US_VACCINATIONS
    ),
    StringencyMeasures AS (
        SELECT 
            date_key,
            location_key,
            AVG(stringency_index) OVER (PARTITION BY location_key ORDER BY date_key ASC ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS Weekly_day_avg_stringency
        FROM 
            "AMMAR.AMJAD".GOVERNMENT_RESPONSES
    )
    SELECT 
        V.date_key,
        V.location_key,
        V.rolling_sum_vaccinated,
        V.Weekly_day_avg_vaccinated,
        S.Weekly_day_avg_stringency,
        G.stay_at_home_requirements,
        G.public_transport_closing,
        G.school_closing,
        G.workplace_closing,
        G.cancel_public_events,
        G.restrictions_on_gatherings,
        G.restrictions_on_internal_movement,
        G.international_travel_controls
    FROM 
        VaccinationRate V
    INNER JOIN 
        StringencyMeasures S
    ON 
        V.date_key = S.date_key AND V.location_key = S.location_key
    INNER JOIN 
        "AMMAR.AMJAD".GOVERNMENT_RESPONSES G
    ON 
        V.date_key = G.date_key AND V.location_key = G.location_key
    WHERE 
        V.date_key >= TO_DATE('2020-01-01', 'YYYY-MM-DD') AND V.date_key <= TO_DATE('2022-12-31', 'YYYY-MM-DD')
    ORDER BY 
        V.date_key ASC, V.location_key ASC"""

    cursor.execute(query)
    result = cursor.fetchall()

    res_list = []
    for row in result:
        data = {
            "date": row[0],
            "location_key": row[1],
            "rolling_sum_vaccinated": row[2],
            "weekly_day_avg_vaccinated": row[3],
            "weekly_day_avg_stringency": row[4],
            "stay_at_home_requirements": row[5],
            "public_transport_closing": row[6],
            "school_closing": row[7],
            "workplace_closing": row[8],
            "cancel_public_events": row[9],
            "restrictions_on_gatherings": row[10],
            "restrictions_on_internal_movement": row[11],
            "international_travel_controls": row[12]
        }
        res_list.append(data)

    print(len(result))
    cursor.close()
    connection.close()

    return jsonify(res_list)

if __name__ == '__main__':
    app.run(debug=True)