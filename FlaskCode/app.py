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

# Weekly infection rate vs mobility
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

    query = """WITH 
    AggregatedCountyData AS (
        SELECT 
            date_key,
            SUBSTR(location_key, 1, 5) AS location_key,
            NVL(SUM(new_confirmed), 0) AS new_confirmed
        FROM
            rgugale.US_Epidemiology
        WHERE
            location_key LIKE 'US____%'
        GROUP BY
            date_key, SUBSTR(location_key, 1, 5)
    ),
    CurrentlyInfectedCountPerState AS (
        SELECT
            date_key,
            location_key,
            SUM(new_confirmed) OVER (PARTITION BY location_key ORDER BY date_key ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS CurrentlyInfectedCount
        FROM
            AggregatedCountyData
    ),
    CurrentlyInfectedCountPerStatePerWeek AS (
        SELECT 
            date_key AS start_of_week,
            location_key,
            CurrentlyInfectedCount
        FROM
            CurrentlyInfectedCountPerState
        WHERE
            date_key = TRUNC(date_key, 'IW')
    ),
    InfectionRatePerStatePerWeek AS (
        SELECT 
            cicpspw.location_key, 
            cicpspw.start_of_week,
            ROUND((CurrentlyInfectedCount/population)*100, 8) AS InfectionRatePerWeek 
        FROM
            CurrentlyInfectedCountPerStatePerWeek cicpspw
        JOIN
            rgugale.demographics demo ON cicpspw.location_key = demo.location_key
    ),
    WeeklyUSMobility AS (
        SELECT
            TRUNC(date_key, 'IW') AS start_of_week,
            SUBSTR(location_key, 1, 5) AS location_key,
            ROUND(AVG(mobility_retail_and_recreation), 4) AS AvgMobilityRetailAndRecreation,
            ROUND(AVG(mobility_grocery_and_pharmacy), 4) AS AvgMobilityGroceryAndPharmacy,
            ROUND(AVG(mobility_parks), 4) AS AvgMobilityParks,
            ROUND(AVG(mobility_transit_stations), 4) AS AvgMobilityTransitStations,
            ROUND(AVG(mobility_workplaces), 4) AS AvgMobilityWorkplaces,
            ROUND(AVG(mobility_residential), 4) AS AvgMobilityResidential
        FROM
            "AMMAR.AMJAD".US_Mobility
        WHERE
            location_key LIKE 'US____%'
        GROUP BY
            TRUNC(date_key, 'IW'),
            SUBSTR(location_key, 1, 5)
    )
    SELECT
        mobi.start_of_week
        cts.state_name,
        InfectionRatePerStatePerWeek.InfectionRatePerWeek,
        AvgMobilityRetailAndRecreation,
        AvgMobilityGroceryAndPharmacy,
        AvgMobilityParks,
        AvgMobilityTransitStations,
        AvgMobilityWorkplaces,
        AvgMobilityResidential
    FROM
        InfectionRatePerStatePerWeek
    JOIN
        WeeklyUSMobility mobi 
        ON InfectionRatePerStatePerWeek.location_key = mobi.location_key 
            AND InfectionRatePerStatePerWeek.start_of_week = mobi.start_of_week
    JOIN
        RGUGALE.CODE_TO_STATE cts 
        ON cts.state_code = InfectionRatePerStatePerWeek.location_key
    WHERE
        InfectionRatePerStatePerWeek.location_key = (SELECT state_code FROM RGUGALE.CODE_TO_STATE WHERE state_name = :input_state) 
        AND mobi.start_of_week BETWEEN :start_date AND :end_date
    ORDER BY
        mobi.start_of_week, mobi.location_key
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
        cts.state_name,
        MonthlyGoogleSearches.avg_monthly_sni_covid19_vaccination,
        MonthlyGoogleSearches.avg_monthly_sni_vaccination_intent,
        MonthlyGoogleSearches.avg_monthly_sni_safety_side_effects,
        MonthlyVacRate.VaccinationRate
    FROM
        (
            SELECT
                TRUNC(date_key, 'MM') AS start_of_month,
                SUBSTR(location_key, 1, 5) AS location_key,
                ROUND(AVG(sni_covid19_vaccination), 4) as avg_monthly_sni_covid19_vaccination,
                ROUND(AVG(sni_vaccination_intent), 4) as avg_monthly_sni_vaccination_intent,
                ROUND(AVG(sni_safety_side_effects), 4) as avg_monthly_sni_safety_side_effects
            FROM
                "AMMAR.AMJAD".vaccination_search
            WHERE
                location_key LIKE 'US____%' 
            GROUP BY
                TRUNC(date_key, 'MM'), SUBSTR(location_key, 1, 5) --Aggregating county data for each state for each month
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
                        TRUNC(date_key, 'MM'), location_key -- Aggregation on date. No aggregation on county data as suitable county data is not available. Directly used the state data.
                ) VacInfo
            JOIN
                "RGUGALE".Demographics ON VacInfo.location_key = Demographics.location_key
        ) MonthlyVacRate
    ON MonthlyGoogleSearches.start_of_month = MonthlyVacRate.start_of_month
        AND MonthlyGoogleSearches.location_key = MonthlyVacRate.location_key
    JOIN RGUGALE.CODE_TO_STATE cts ON cts.state_code = MonthlyGoogleSearches.location_key
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

# Ratio of no. of deaths vs no. of newly hospitalized patients for states 
# grouped into 4 categories according to no. of physicians per 100000 people.
@app.route('/query4', methods=['POST'])
def query4():
    data = request.json
    physician_categories = data.get('physician_categories', [])
    print(physician_categories)
    if len(physician_categories) == 0:
        physician_categories = ["Low (<200)", "Decent (200-300)", "Good (300-400)", "Very good (>400)"]
    else:
        # tuple() adds a comma at the end for tuples with only 1 element. To avoid that, creating my own tuple.
        if len(physician_categories) == 1:
            physician_tuple = "('" + physician_categories[0] + "')"
        else:
            physician_tuple = tuple(physician_categories)
    print(physician_tuple)

    start_date = data.get('start_date')
    end_date = data.get('end_date')

    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()

    query = """
        WITH 
        HospitalizationsForStates AS (
            (
                SELECT 
                    date_key,
                    location_key,
                    new_hospitalized_patients
                FROM
                    "AMMAR.AMJAD".hospitalizations
                WHERE
                    location_key LIKE 'US___'
            )
            MINUS
            -- Get rid of US_NY values as they are incomplete
            (
                SELECT 
                    date_key,
                    location_key,
                    new_hospitalized_patients
                FROM
                    "AMMAR.AMJAD".hospitalizations
                WHERE
                    location_key LIKE 'US_NY'
            )
            UNION
            -- Sum up county data for NY
            (
                SELECT 
                    date_key,
                    SUBSTR(location_key, 1, 5) AS location_key,
                    SUM(new_hospitalized_patients) AS new_hospitalized_patients
                FROM
                    "AMMAR.AMJAD".hospitalizations
                WHERE
                    location_key LIKE 'US_NY_%'
                GROUP BY
                    date_key,
                    SUBSTR(location_key, 1, 5)
            )
        ),
        EpidemiologyForStates AS (
            SELECT
                date_key,
                SUBSTR(location_key, 1, 5) AS location_key,
                SUM(new_deceased) AS new_deceased
            FROM
                RGUGALE.us_epidemiology
            WHERE 
                location_key LIKE 'US____%' 
            GROUP BY
                date_key, SUBSTR(location_key, 1, 5)
        ),
        RatioOfDeathsToHospitalizedPeople AS (
            SELECT
                HospitalizationsForStates.date_key,
                HospitalizationsForStates.location_key,
                (new_deceased / NULLIF(new_hospitalized_patients, 0)) AS ratio_of_deaths
            FROM
                HospitalizationsForStates 
            JOIN
                EpidemiologyForStates 
            ON 
                HospitalizationsForStates.date_key = EpidemiologyForStates.date_key 
                AND HospitalizationsForStates.location_key = EpidemiologyForStates.location_key
            WHERE 
                HospitalizationsForStates.date_key BETWEEN :start_date AND :end_date
        ),
        StateAndPhysicians AS (
            SELECT 
                location_key,
                physicians_per_100000,
                CASE
                    WHEN physicians_per_100000 < 200 THEN 'Low (<200)'
                    WHEN physicians_per_100000 >= 200 AND physicians_per_100000 < 300 THEN 'Decent (200-300)'
                    WHEN physicians_per_100000 >= 300 AND physicians_per_100000 < 400 THEN 'Good (300-400)'
                    WHEN physicians_per_100000 >= 400 THEN 'Very good (>400)'
                    ELSE 'Unknown'
                END AS physician_category
            FROM
                rgugale.health_stats
            WHERE 
                location_key LIKE 'US___'
        )
    SELECT 
        RatioOfDeathsToHospitalizedPeople.date_key,
        physician_category,
        GREATEST(NVL(ROUND(AVG(RatioOfDeathsToHospitalizedPeople.ratio_of_deaths), 8), 0), 0) AS AvgRatioOfDeathsToHospitalizedPeople
    FROM
        RatioOfDeathsToHospitalizedPeople
    JOIN
        StateAndPhysicians ON RatioOfDeathsToHospitalizedPeople.location_key = StateAndPhysicians.location_key
    JOIN
        rgugale.code_to_state ON  code_to_state.state_code = StateAndPhysicians.location_key
    WHERE physician_category in {}
    GROUP BY
        RatioOfDeathsToHospitalizedPeople.date_key, physician_category
    ORDER BY
        physician_category, date_key""".format(physician_tuple)

    cursor.execute(query, start_date=start_date, end_date=end_date)
    result = cursor.fetchall()

    res_list = []
    for row in result:
        data = {
            "date": row[0],
            "physician_category": row[1],
            "avg_ratio_of_deaths_to_hospitalized_people": row[2]
        }
        res_list.append(data)

    print(len(result))
    cursor.close()
    connection.close()

    return jsonify(res_list)

@app.route('/query5', methods=['POST'])
def query5():
    data = request.json
    party = data.get('party')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    print("Request for q5 received")

    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()

    query = """
    WITH WeeklyStringency AS (
        SELECT 
            TRUNC(date_key, 'IW') AS start_of_week,
            location_key,
            ROUND(AVG(stringency_index), 4) AS weekly_avg_stringency_index 
        FROM "AMMAR.AMJAD".government_responses 
        WHERE location_key LIKE 'US_%'
        GROUP BY TRUNC(date_key, 'IW'), location_key
    ),
    WeeklyStringencyWithCategory AS (
        SELECT
            start_of_week,
            location_key,
            weekly_avg_stringency_index,
            CASE
                WHEN weekly_avg_stringency_index < 20 THEN '0-19'
                WHEN weekly_avg_stringency_index >= 20 AND weekly_avg_stringency_index < 40 THEN '20-39'
                WHEN weekly_avg_stringency_index >= 40 AND weekly_avg_stringency_index < 60 THEN '40-59'
                WHEN weekly_avg_stringency_index >= 60 AND weekly_avg_stringency_index < 80 THEN '60-79'
                WHEN weekly_avg_stringency_index >= 80 AND weekly_avg_stringency_index < 100 THEN '80-100'
                ELSE 'Unknown'
            END AS stringency_category
        FROM WeeklyStringency
    ),
    WeeklyDeceased AS (
        SELECT 
            TRUNC(date_key, 'IW') AS start_of_week,
            SUBSTR(location_key, 1, 5) AS location_key,
            SUM(new_deceased) AS weekly_avg_deceased
        FROM rgugale.US_Epidemiology
        WHERE location_key LIKE 'US___'
        GROUP BY TRUNC(date_key, 'IW'), SUBSTR(location_key, 1, 5)
    ),
    MortalityInfo AS (
        SELECT 
            start_of_week,
            WeeklyDeceased.location_key,
            GREATEST(ROUND(weekly_avg_deceased * 100000 / population, 8), 0) AS mortality_rate_100000 --mortality rate for every 1000 people
        FROM
            WeeklyDeceased 
            JOIN rgugale.Demographics ON WeeklyDeceased.location_key = Demographics.location_key
    )
    SELECT
        WeeklyStringencyWithCategory.start_of_week,
        ruling_party,
        stringency_category,
        COUNT(WeeklyStringencyWithCategory.location_key) AS noOfStates,
        ROUND(AVG(MortalityInfo.mortality_rate_100000), 8) AS mortality_rate_100000
    FROM WeeklyStringencyWithCategory
    JOIN MortalityInfo ON MortalityInfo.start_of_week = WeeklyStringencyWithCategory.start_of_week AND MortalityInfo.location_key = WeeklyStringencyWithCategory.location_key
    JOIN rgugale.code_to_state ON code_to_state.state_code = WeeklyStringencyWithCategory.location_key
    WHERE MortalityInfo.start_of_week BETWEEN :start_date and :end_date AND ruling_party=:party
    GROUP BY WeeklyStringencyWithCategory.start_of_week, ruling_party, stringency_category
    ORDER BY WeeklyStringencyWithCategory.start_of_week, ruling_party, stringency_category
    """

    cursor.execute(query, start_date=start_date, end_date=end_date, party=party)
    result = cursor.fetchall()

    res_list = []
    for row in result:
        data = {
            "date": row[0],
            "ruling_party": row[1],
            "stringency_category": row[2],
            "no_of_states": row[3],
            "mortality_rate_per_100000": row[4]
        }
        res_list.append(data)

    print(len(result))
    cursor.close()
    connection.close()

    return jsonify(res_list)

# Query to get the total number of rows in the database
@app.route('/total_row_count', methods=['GET'])
def total_row_count():
    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()

    query = """
    SELECT
        count_code_to_country +
        count_code_to_state +
        count_demographics +
        count_stocks +
        count_us_epidemiology +
        count_us_mobility +
        count_government_responses +
        count_hospitalizations +
        count_vaccination_search +
        count_us_vaccinations AS total_count
    FROM (
        SELECT
            (SELECT COUNT(*) FROM RGUGALE.code_to_country) AS count_code_to_country,
            (SELECT COUNT(*) FROM RGUGALE.code_to_state) AS count_code_to_state,
            (SELECT COUNT(*) FROM RGUGALE.demographics) AS count_demographics,
            (SELECT COUNT(*) FROM RGUGALE.stocks) AS count_stocks,
            (SELECT COUNT(*) FROM RGUGALE.us_epidemiology) AS count_us_epidemiology,
            (SELECT COUNT(*) FROM "AMMAR.AMJAD".us_mobility) AS count_us_mobility,
            (SELECT COUNT(*) FROM "AMMAR.AMJAD".government_responses) AS count_government_responses,
            (SELECT COUNT(*) FROM "AMMAR.AMJAD".hospitalizations) AS count_hospitalizations,
            (SELECT COUNT(*) FROM "AMMAR.AMJAD".vaccination_search) AS count_vaccination_search,
            (SELECT COUNT(*) FROM "AMMAR.AMJAD".us_vaccinations) AS count_us_vaccinations
        FROM dual
    )
    """

    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    total_count_json = {
        "total_count": result[0]
    }

    return jsonify(total_count_json)

if __name__ == '__main__':
    app.run(debug=True)