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

# Weekly infected population percentage vs mobility
@app.route('/query1', methods=['POST'])
def query1():
    data = request.json
    input_state = data.get('state')
    mobility_types = data.get('mobility_types', [])
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()
    print("Request for q1 received")

    query = """WITH WeeklyUSEpidemiology AS (
        SELECT
            TRUNC(date_key, 'IW') AS start_of_week,
            CASE
                WHEN location_key LIKE 'US\___%' THEN SUBSTR(location_key, 1, 5)
                ELSE location_key
            END AS truncated_location,
            SUM(cumulative_confirmed) AS TotalInfected
        FROM
            rgugale.US_Epidemiology
        GROUP BY
            TRUNC(date_key, 'IW'),
            CASE
                WHEN location_key LIKE 'US\___%' THEN SUBSTR(location_key, 1, 5)
                ELSE location_key
            END
    ),
    WeeklyUSMobility AS (
        SELECT
            TRUNC(date_key, 'IW') AS start_of_week,
            CASE
                WHEN location_key LIKE 'US\___%' THEN SUBSTR(location_key, 1, 5)
                ELSE location_key
            END AS truncated_location,
            ROUND(AVG(mobility_retail_and_recreation), 4) AS AvgMobilityRetailAndRecreation,
            ROUND(AVG(mobility_grocery_and_pharmacy), 4) AS AvgMobilityGroceryAndPharmacy,
            ROUND(AVG(mobility_parks), 4) AS AvgMobilityParks,
            ROUND(AVG(mobility_transit_stations), 4) AS AvgMobilityTransitStations,
            ROUND(AVG(mobility_workplaces), 4) AS AvgMobilityWorkplaces,
            ROUND(AVG(mobility_residential), 4) AS AvgMobilityResidential
        FROM
            "AMMAR.AMJAD".US_Mobility
        GROUP BY
            TRUNC(date_key, 'IW'),
            CASE
                WHEN location_key LIKE 'US\___%' THEN SUBSTR(location_key, 1, 5)
                ELSE location_key
            END
    )
    SELECT
        mobi.start_of_week,
        cts.state_name,
        ROUND((us_epi.TotalInfected / demo.population), 4) * 100 AS PercentageInfected,
        mobi.AvgMobilityRetailAndRecreation,
        mobi.AvgMobilityGroceryAndPharmacy,
        mobi.AvgMobilityParks,
        mobi.AvgMobilityTransitStations,
        mobi.AvgMobilityWorkplaces,
        mobi.AvgMobilityResidential
    FROM
        RGUGALE.US_Demographics demo
    JOIN WeeklyUSEpidemiology us_epi ON us_epi.truncated_location = demo.location_key
    JOIN WeeklyUSMobility mobi ON us_epi.truncated_location = mobi.truncated_location AND us_epi.start_of_week = mobi.start_of_week
    JOIN RGUGALE.Location_INDEX loc ON us_epi.truncated_location = loc.location_key
    JOIN RGUGALE.CODE_TO_STATE cts ON cts.state_code = loc.location_key
    WHERE loc.location_key=(SELECT state_code from RGUGALE.CODE_TO_STATE where state_name=:input_state) 
        AND us_epi.start_of_week BETWEEN :start_date AND :end_date
    ORDER BY
        mobi.start_of_week, mobi.truncated_location
    """

    cursor.execute(query, input_state=input_state, start_date=start_date, end_date=end_date)
    result = cursor.fetchall()

    res_list = []
    for row in result:
        data = {
            "date": row[0],
            "state": row[1],
            "infected_population_percent": row[2],
        }

        # If no mobility_types specified, send back data about all of them
        if len(mobility_types) == 0:
            data["mobility_retail_and_recreation"] = row[3]
            data["mobility_grocery_and_pharmacy"] = row[4]
            data["mobility_parks"] = row[5]
            data["mobility_transit_stations"] = row[6]
            data["mobility_workplaces"] = row[7]
            data["mobility_residential"] = row[8]
            res_list.append(data)
            continue

        # Include only the selected mobility types
        for mobility_type in mobility_types:
            if mobility_type == "mobility_retail_and_recreation":
                data["mobility_retail_and_recreation"] = row[3]
            elif mobility_type == "mobility_grocery_and_pharmacy":
                data["mobility_grocery_and_pharmacy"] = row[4]
            elif mobility_type == "mobility_parks":
                data["mobility_parks"] = row[5]
            elif mobility_type == "mobility_transit_stations":
                data["mobility_transit_stations"] = row[6]
            elif mobility_type == "mobility_workplaces":
                data["mobility_workplaces"] = row[7]
            elif mobility_type == "mobility_residential":
                data["mobility_residential"] = row[8]

        res_list.append(data)

    print(len(result))
    cursor.close()
    connection.close()

    return jsonify(res_list)


# Monthly vaccination search trends vs infection rate
@app.route('/query2', methods=['POST'])
def query2():
    data = request.json
    input_state = data.get('state')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()
    print("Request for q2 received")

    query = """
    SELECT
        MonthlyGoogleSearches.start_of_month,
        MonthlyGoogleSearches.location_key,
        MonthlyGoogleSearches.avg_monthly_sni_covid19_vaccination,
        MonthlyGoogleSearches.avg_monthly_sni_vaccination_intent,
        MonthlyGoogleSearches.avg_monthly_sni_safety_side_effects,
        MonthlyVacRate.VaccinationRate
    FROM
        (
            SELECT
                TRUNC(date_key, 'MM') AS start_of_month,
                location_key,
                ROUND(AVG(sni_covid19_vaccination), 4) as avg_monthly_sni_covid19_vaccination,
                ROUND(AVG(sni_vaccination_intent), 4) as avg_monthly_sni_vaccination_intent,
                ROUND(AVG(sni_safety_side_effects), 4) as avg_monthly_sni_safety_side_effects
            FROM
                "AMMAR.AMJAD".vaccination_search
            WHERE
                location_key LIKE 'US%'
            GROUP BY
                TRUNC(date_key, 'MM'), location_key
        ) MonthlyGoogleSearches
    JOIN
        (
            SELECT
                VacInfo.start_of_month,
                VacInfo.location_key,
                VacInfo.new_persons_vaccinated,
                Demographics.population,
                ROUND(VacInfo.new_persons_vaccinated/Demographics.population*100, 4) as VaccinationRate
            FROM
                (
                    SELECT
                        TRUNC(date_key, 'MM') AS start_of_month,
                        location_key,
                        ROUND(AVG(new_persons_vaccinated), 4) AS new_persons_vaccinated,
                        ROUND(AVG(cumulative_persons_vaccinated), 4) AS cumulative_persons_vaccinated,
                        ROUND(AVG(new_persons_fully_vaccinated), 4) AS new_persons_fully_vaccinated,
                        ROUND(AVG(cumulative_persons_fully_vaccinated), 4) AS cumulative_persons_fully_vaccinated
                    FROM
                        "AMMAR.AMJAD".us_vaccinations
                    GROUP BY
                        TRUNC(date_key, 'MM'), location_key
                ) VacInfo
            JOIN
                Demographics ON VacInfo.location_key = Demographics.location_key
        ) MonthlyVacRate
    ON MonthlyGoogleSearches.start_of_month = MonthlyVacRate.start_of_month
        AND MonthlyGoogleSearches.location_key = MonthlyVacRate.location_key
    WHERE
        MonthlyGoogleSearches.location_key = (SELECT state_code FROM RGUGALE.CODE_TO_STATE WHERE state_name = :input_state)
        AND MonthlyGoogleSearches.start_of_month BETWEEN TO_DATE(:start_date, 'DD-MON-YY') AND TO_DATE(:end_date, 'DD-MON-YY')
    ORDER BY
        MonthlyGoogleSearches.start_of_month, MonthlyGoogleSearches.location_key
    """

    cursor.execute(query, input_state=input_state, start_date=start_date, end_date=end_date)
    result = cursor.fetchall()

    res_list = []
    for row in result:
        data = {
            "date": row[0],
            "state": row[1],
            "avg_monthly_sni_covid19_vaccination": row[2],
            "avg_monthly_sni_vaccination_intent": row[3],
            "avg_monthly_sni_safety_side_effects": row[4],
            "vaccination_rate": row[5]
        }

        res_list.append(data)

    print(len(result))
    cursor.close()
    connection.close()

    return jsonify(res_list)


# Healthcare stocks vs hospitalizations - returns 34 records
@app.route('/query3', methods=['GET'])
def query3():
    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()
    print("Request for q3 received")

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