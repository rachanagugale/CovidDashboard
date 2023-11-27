import cx_Oracle
import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
from collections import defaultdict

app = Flask(__name__)
CORS(app)

load_dotenv()

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Database connection settings
dsn = cx_Oracle.makedsn('oracle.cise.ufl.edu', '1521', service_name='orcl')
db_username = DB_USERNAME
db_password = DB_PASSWORD

# Weekly infection rate vs mobility for a state
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

    # The query works as follows:
    # 1. Sum the daily new_confirmed from each county to get the new_confirmed for the state.
    # 2. Calculate the number of people currently infected on the day in the state by aggregating the new_confirmed values 
    # for the past 2 weeks. This is because an infected person takes around 2 weeks to be free of infection.
    # 3. Keep only the currently_infected values for the start of the week for each state.
    # 4. Calculate the "weekly infection rate" as (currently_infected/state_population) by joining with the demographics table.
    # 5. Calculate the aggregate weekly mobility values for each state for each week  from the per day county mobility values.
    # 6. Join the infection and mobility values to get values for each state for each week.
    # 7. Join with code_to_state table to get the state_name.
    # 8. Filter by date and state_name.
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
        mobi.start_of_week,
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


# Monthly vaccination search trends vs infection rate for a state
@app.route('/query2', methods=['POST'])
def query2():
    data = request.json
    input_state = data.get('state')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()
    print("Request for q2 received")

    # This query works as follows:
    # 1. Get the monthly vaccination search data by aggregating the daily data for every county of the state 
    # and computing its average.
    # 2. Get the monthly vaccination data for each state by aggregating the daily data.
    # 3. Calculate the monthly vaccination rate for each state using (new_persons_vaccinated/population) 
    # by joining vaccination data with demographics table.
    # 4. Join the vaccination search data with the vaccination rate data.
    # 5. Join with code_to_state table to get the state_name.
    # 6. Filter by date and state_name.
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
                ROUND((VacInfo.new_persons_vaccinated/Demographics.population), 8) as VaccinationRate
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


# This query shows the number of people tested per 100000 for the entire US vs 
# the percentage of companies from a sector whose stocks made a profit for the day.
@app.route('/query3', methods=['POST'])
def query3():
    data = request.json
    sectors = data.get('sectors', [])

    if len(sectors) == 1:
        sectors_tuple = "('" + sectors[0] + "')"
    else:
        sectors_tuple = tuple(sectors)

    start_date = data.get('start_date')
    end_date = data.get('end_date')

    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()
    print("Request for q3 received")

    # This query works as follows:
    # 1. Get daily profit percentage of the stock using ((close-open)/open)*100. Also get the sector 
    # information of the stock by joining the snp500 table with snp500_company_info table. Create a new column denoting
    # if the company was in profit or loss for the day based on the daily profit percentage.
    # 2. Get the count of number of companies from each sector that are in profit and in loss for the day.
    # 3. Calculate the percentage of companies from the sector that are in profit for the day.
    # 4. Get aggregated data about the number of people tested per 100000 people for the day in the entire US.
    # 5. Join the companies in profit data with the testing data.
    # 6. Filter by date and sector.
    query = """WITH PLCount AS (
        SELECT 
            date_key, 
            sector, 
            p_or_l, 
            COUNT(ticker) AS noOfCompanies
        FROM (
            SELECT 
                snp500.ticker,
                date_key,
                sector,
                ROUND(((close - open) / open) * 100, 4) AS profit_percent,
                CASE
                    WHEN ROUND(((close - open) / open) * 100, 4) < 0 THEN 'Loss'
                    WHEN ROUND(((close - open) / open) * 100, 4) >= 0 THEN 'Profit'
                END AS p_or_l
            FROM "AMMAR.AMJAD".snp500 
            JOIN rgugale.snp500_company_info ON snp500.ticker = snp500_company_info.ticker
        ) StockPriceWithSector
        GROUP BY date_key, sector, p_or_l
    ),
    PercentageOfCompaniesInProfit AS (
        SELECT 
            date_key, 
            sector, 
            p_or_l,
            noOfCompanies,
            ROUND((noOfCompanies / (SUM(noOfCompanies) OVER (PARTITION BY date_key, sector))) * 100, 4) AS PercentOfCompaniesInProfit
        FROM
            PLCount
    ),
    TestingInfoAggregated AS (
        SELECT 
            date_key, 
            ROUND(AVG(no_of_tested_per_100000), 5) AS no_of_tested_per_100000 
        FROM 
            (
                SELECT 
                    date_key,
                    US_Epidemiology.location_key,
                    NVL(100000 * new_tested / population, 0) AS no_of_tested_per_100000
                FROM
                    rgugale.US_Epidemiology 
                    JOIN rgugale.Demographics demo ON demo.location_key = US_Epidemiology.location_key
                WHERE
                    US_Epidemiology.location_key LIKE 'US___' AND date_key BETWEEN :start_date AND :end_date
            ) TestingInfo
        GROUP BY date_key
    )
    SELECT 
        PercentageOfCompaniesInProfit.date_key,
        no_of_tested_per_100000,
        PercentOfCompaniesInProfit,
        sector
    FROM 
        PercentageOfCompaniesInProfit
        JOIN TestingInfoAggregated ON TestingInfoAggregated.date_key = PercentageOfCompaniesInProfit.date_key
    WHERE sector IN {}
    ORDER BY PercentageOfCompaniesInProfit.date_key, sector
    """.format(sectors_tuple)

    print(query)

    cursor.execute(query, start_date=start_date, end_date=end_date)
    result = cursor.fetchall()

    res_map = {}
    for row in result:
        if str(row[0]) not in res_map:
            res_map[str(row[0])] = {}
            res_map[str(row[0])]["no_of_tested_people_per_100000_people"] = row[1]
            res_map[str(row[0])]["sectorwise_percent_of_companies_in_profit"] = {}

        res_map[str(row[0])]["sectorwise_percent_of_companies_in_profit"][row[3]] = row[2]        

    print(len(result))
    cursor.close()
    connection.close()

    return jsonify(res_map)

# Daily ratio of no. of deaths vs no. of newly hospitalized patients for states 
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

    # This query works as follows:
    # 1. Filter and get the daily hospitalization data for US states from all the other hospitalization data.
    # 2. The data for NY is just placeholder data. Actual data for NY is split into counties. 
    # Subtract the NY data and add the aggregated county data to the hospitalization data to include data for NY.
    # 3. For each state, get the number of deceased people for the day from epidemiology table by aggregating 
    # new_deceased for all the counties of the state.
    # 4. Calculate the ratio of deaths to hospitalized people for each state for each day.
    # 5. Divide the states into 4 groups depending on the number of physicians.
    # 6. Aggregate the ratio of deaths to hospitalized people for each group of states.
    # 7. Filter by date and noOfPhysician categories.
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
    date_mapping = defaultdict(lambda: {})
    for row in result:
        if row[0] not in date_mapping: date_mapping[row[0]] = { "date": row[0] }
        date_mapping[row[0]][row[1]] = row[2]
        # data = {
        #     "date": row[0],
        #     "physician_category": row[1],
        #     "avg_ratio_of_deaths_to_hospitalized_people": row[2]
        # }

    res_list = date_mapping.values()
    print(len(result))
    cursor.close()
    connection.close()

    return jsonify(list(res_list))

# Query to compare the mortality rate in democratic vs republican states based on their stringency index per month.
@app.route('/query5', methods=['POST'])
def query5():
    data = request.json
    party = data.get('party')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    print("Request for q5 received")

    connection = cx_Oracle.connect(db_username, db_password, dsn)
    cursor = connection.cursor()

    # How this query works:
    # 1. Calculate the average monthly stringency_index for each state.
    # 2. Calculate which of the 5 stringency level categories the state lies in.
    # 3. Get the number of states that belong to a stringency level category for each month for each party.
    # 3. Get the monthly deceased count per state by aggregating the daily deceased count.
    # 4. For each party, get the aggregate average mortality rate per 100000 people for the month across all the states where it rules
    # by joining the deceased data with population data from demographics table.
    # 6. Join the stringency and mortality information.
    # 7. Filter by date and the ruling party.
    query = """
    WITH MonthlyStringency AS (
        SELECT 
            TRUNC(date_key, 'MM') AS start_of_month,
            location_key,
            ROUND(AVG(stringency_index), 4) AS monthly_avg_stringency_index 
        FROM "AMMAR.AMJAD".government_responses 
        WHERE location_key LIKE 'US___'
        GROUP BY TRUNC(date_key, 'MM'), location_key
    ),
    MonthlyStringencyWithCategory AS (
        SELECT
            start_of_month,
            location_key,
            monthly_avg_stringency_index,
            CASE
                WHEN monthly_avg_stringency_index < 20 THEN '0-19'
                WHEN monthly_avg_stringency_index >= 20 AND monthly_avg_stringency_index < 40 THEN '20-39'
                WHEN monthly_avg_stringency_index >= 40 AND monthly_avg_stringency_index < 60 THEN '40-59'
                WHEN monthly_avg_stringency_index >= 60 AND monthly_avg_stringency_index < 80 THEN '60-79'
                WHEN monthly_avg_stringency_index >= 80 AND monthly_avg_stringency_index < 100 THEN '80-100'
                ELSE 'Unknown'
            END AS stringency_category
        FROM MonthlyStringency
    ),
    NoOfStatesInEachStringencyCategoryPerParty AS (
        SELECT 
            start_of_month, 
            ruling_party, 
            stringency_category,
            COUNT(MonthlyStringencyWithCategory.location_key) AS noOfStates
        FROM MonthlyStringencyWithCategory
        JOIN rgugale.code_to_state ON code_to_state.state_code = MonthlyStringencyWithCategory.location_key
        GROUP BY start_of_month, ruling_party, stringency_category
    ),
    MonthlyDeceasedPerState AS (
        SELECT 
            TRUNC(date_key, 'MM') AS start_of_month,
            location_key,
            SUM(new_deceased) AS monthly_avg_deceased
        FROM rgugale.US_Epidemiology
        WHERE location_key LIKE 'US___'
        GROUP BY TRUNC(date_key, 'MM'), location_key
    ),
    MortalityRatePerMonthPerRulingParty AS (
        SELECT 
            start_of_month,
            ruling_party,
            AVG(GREATEST(ROUND(monthly_avg_deceased * 100000 / population, 8), 0)) AS mortality_rate_100000 --mortality rate for every 1000 people
        FROM
            MonthlyDeceasedPerState 
            JOIN rgugale.Demographics ON MonthlyDeceasedPerState.location_key = Demographics.location_key
            JOIN rgugale.code_to_state ON code_to_state.state_code = Demographics.location_key
        GROUP BY start_of_month, ruling_party
    )
    SELECT
        mor.start_of_month,
        stringency_category,
        noOfStates,
        ROUND(mortality_rate_100000, 8) AS mortality_rate_100000
    FROM
        NoOfStatesInEachStringencyCategoryPerParty str_cat
    JOIN MortalityRatePerMonthPerRulingParty mor ON mor.start_of_month = str_cat.start_of_month AND mor.ruling_party = str_cat.ruling_party
    WHERE mor.start_of_month BETWEEN :start_date AND :end_date AND mor.ruling_party=:party
    ORDER BY mor.start_of_month, mor.ruling_party, stringency_category
    """

    cursor.execute(query, start_date=start_date, end_date=end_date, party=party)
    result = cursor.fetchall()

    res_map = {}
    for row in result:
        if str(row[0]) not in res_map:
            res_map[str(row[0])] = {}
            res_map[str(row[0])]["mortality_rate_100000"] = row[3]
            res_map[str(row[0])]["stringency_categories"] = {
                "0-19": 0,
                "20-39": 0,
                "40-59": 0,
                "60-79": 0,
                "80-100": 0
            }

        res_map[str(row[0])]["stringency_categories"][row[1]] = row[2]    

    print(len(res_map))
    cursor.close()
    connection.close()

    return jsonify(res_map)

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
        count_snp500 +
        count_snp500_company_info +
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
            (SELECT COUNT(*) FROM "AMMAR.AMJAD".snp500) AS count_snp500,
            (SELECT COUNT(*) FROM RGUGALE.snp500_company_info) AS count_snp500_company_info,
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