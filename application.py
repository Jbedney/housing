import numpy as np
import pandas as pd
import csv
from cs50 import SQL
from scipy.stats import zscore
from flask import Flask, request, render_template

app = Flask(__name__)

open("properties.db", "w").close()
db = SQL("sqlite:///properties.db")

db.execute("CREATE TABLE IF NOT EXISTS properties ( link TEXT,city TEXT,asking_price bigint,hoa real,sq_ft real, driving_commute integer,transit_commute TEXT,nearest_pub integer,parking TEXT,laundry TEXT,dishwasher BOOLEAN,balcony BOOLEAN,gym BOOLEAN,pool BOOLEAN,school_rank real,est_tax_rate REAL,nj INTEGER,population BIGINT,violent_crime INTEGER,property_crime INTEGER,law_enforcement_employees INTEGER,total_crimes INTEGER,crime_rate_per_1000 REAL,violent_crimes_per_1000 REAL,property_crimes_per_1000 REAL,law_enforcement_per_1000 REAL )");

with open("properties.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        link = row["Link"]
        city = row["City"]
        asking_price =row["Asking Price"]
        hoa = row["HOA"]
        sq_ft = row["Sq Ft."]
        driving_commute = row["Driving Commute"]
        transit_commute = row["Transit Commute"]
        nearest_pub = row["Nearest Pub"]
        parking = row["Parking"]
        laundry = row["Laundry"]
        dishwasher = row["Dishwasher"]
        balcony = row["Balcony"]
        gym = row["Gym"]
        pool = row["Pool"]
        school_rank = row["School Rank"]
        est_tax_rate = row['Est. Tax Rate']
        nj = row["NJ"]
        population = row["Population"]
        violent_crime = row["Violent crime"]
        property_crime = row["Property crime"]
        law_enforcement_employees = row["Law enforcement employees"]
        total_crimes = row["Total crimes"]
        crime_rate_per_1000 = row["Crime rate per 1,000"]
        violent_crimes_per_1000 = row['Violent crimes per 1,000']
        property_crimes_per_1000 = row["Property crimes per 1,000"]
        law_enforcement_per_1000 = row["Law enforcement per 1,000"]
        

        db.execute("INSERT INTO properties (link,city,asking_price,hoa,sq_ft,driving_commute,transit_commute,nearest_pub,parking,laundry,dishwasher,balcony,gym,pool,school_rank,est_tax_rate,nj,population,violent_crime,property_crime,law_enforcement_employees,total_crimes,crime_rate_per_1000,violent_crimes_per_1000,property_crimes_per_1000,law_enforcement_per_1000) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",link,city,asking_price,hoa,sq_ft,driving_commute,transit_commute,nearest_pub,parking,laundry,dishwasher,balcony,gym,pool,school_rank,est_tax_rate,nj,population,violent_crime,property_crime,law_enforcement_employees,total_crimes,crime_rate_per_1000,violent_crimes_per_1000,property_crimes_per_1000,law_enforcement_per_1000)
    
          

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results", methods=["POST"])
def results():
    table = db.execute("SELECT * FROM properties")
    insurance = pd.to_numeric(request.form.get("insurance"))
    down_payment = pd.to_numeric(request.form.get("down_payment"))
    budget = pd.to_numeric(request.form.get("budget"))
    interest_rate = pd.to_numeric(request.form.get("interest"))
    df = pd.DataFrame(table[1:], columns=table[0])
    properties = df.apply(pd.to_numeric, errors='ignore')
    
    mortgage = ((properties['asking_price']-down_payment)/30/12)
    interest = mortgage*interest_rate
    tax = ((properties['asking_price']*(properties['est_tax_rate']/100))/12)
    HOA = properties['hoa'].fillna(0)
    properties['est_monthly_payment'] = mortgage+interest+tax+HOA+(insurance/12)
    properties['value'] =properties['est_monthly_payment']/properties['sq_ft']
    properties = properties.where(properties['est_monthly_payment'] <= budget).dropna(axis=0,subset=['link'])
    
    # numeric_cols = properties.select_dtypes(include=[np.number]).columns
    # zscores = properties[numeric_cols].apply(zscore)
    # neighborhood = zscores[['school_rank','nj']].mean(axis=1)
    # commute = zscores[['driving_commute','transit_commute']].mean(axis=1)
    # social = zscores[['nearest_pub']].mean(axis=1)
    # value = zscores[['Value']].mean(axis=1)
    # must_haves = zscores[['Dishwasher','laundry']].mean(axis=1)
    # nice_to_haves = zscores[['gym','balcony','pool']].mean(axis=1)
    
    neighborhood = properties[['school_rank','nj']].mean(axis=1)
    commute = properties[['driving_commute','transit_commute']].mean(axis=1)
    social = properties[['nearest_pub']].mean(axis=1)
    value = properties[['value']].mean(axis=1)
    must_haves = properties[['dishwasher','laundry']].mean(axis=1)
    nice_to_haves = properties[['gym','balcony','pool']].mean(axis=1)
    neighborhood_preference = pd.to_numeric(request.form.get("neighborhood"))
    commute_preference = pd.to_numeric(request.form.get("commute"))
    social_preference = pd.to_numeric(request.form.get("nightlife"))
    must_haves_preferences = pd.to_numeric(request.form.get("cleaning"))
    nice_to_haves_preferences = pd.to_numeric(request.form.get("nicetohaves"))
    properties['total_score'] = (neighborhood * neighborhood_preference)+(commute * commute_preference)+(value * 5)+(social * social_preference)-(must_haves * must_haves_preferences)-(nice_to_haves* nice_to_haves_preferences)
    properties['rank'] = properties['total_score'].rank(ascending = True)
    winner = properties.sort_values("rank").head(1)
    if len(winner.index) < 1:
        return render_template("error.html",
        down_payment=request.form.get("down_payment"), 
        budget=request.form.get("budget"),
        insurance=request.form.get("insurance"),
        interest=request.form.get("interest"),
        neighborhood=request.form.get("neighborhood"),
        commute=request.form.get("commute"),
        nightlife=request.form.get("nightlife"),
        cleaning=request.form.get("cleaning"),
        nicetohaves=request.form.get("nicetohaves"))
    else:
        winner_id = winner.iloc[0]['link']
        est_monthly_payment = round(winner.iloc[0]['est_monthly_payment'],2)
        tables = db.execute(f"SELECT distinct city, asking_price, link from properties where link = '{winner_id}'")
        return render_template("results.html", 
        down_payment=request.form.get("down_payment"), 
        budget=request.form.get("budget"),
        insurance=request.form.get("insurance"),
        interest=request.form.get("interest"),
        neighborhood=request.form.get("neighborhood"),
        commute=request.form.get("commute"),
        nightlife=request.form.get("nightlife"),
        cleaning=request.form.get("cleaning"),
        nicetohaves=request.form.get("nicetohaves"),
        tables=tables,
        est_monthly_payment=est_monthly_payment)
        



