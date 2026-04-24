# Who Can Still Afford Berlin?

## Project Overview
Berlin’s housing market has become increasingly difficult to navigate.  
This project explores housing pressure and affordability across Berlin districts by combining housing listings, district income data, and Berlin Social Atlas indicators.

The goal is to understand how rent levels, income, and social conditions vary across the city, and to answer one central question:

## Main Question
**Who can still afford Berlin today?**

This project explores:
- how rent levels vary across Berlin districts
- how income differs across the city
- how social conditions relate to affordability
- whether housing pressure is evenly distributed or concentrated in specific areas

---

## Data Sources
The analysis combines three main data sources:

1. **Berlin housing listings**
   - rent per sqm
   - base rent
   - total rent
   - living space
   - district and district-part information

2. **District income data**
   - average monthly income
   - median monthly income

3. **Berlin Social Atlas indicators**
   - unemployment rate
   - transfer income share
   - social status indicators

---

## Tools Used
- **Python**
  - pandas
  - plotly express
  - jupyter notebook
- **PostgreSQL**
- **Tableau**
- **GitHub**

---

## Project Workflow
The project followed these main steps:

1. collected and cleaned housing, income, and social datasets  
2. standardized district names and joined the different sources  
3. stored structured data in PostgreSQL  
4. explored affordability patterns in Python  
5. created dashboards and story points in Tableau  
6. prepared presentation slides to communicate the findings clearly  

---

## Key Findings
- Housing pressure is strongest in central and high-demand districts.
- Higher income does not automatically mean better affordability.
- District averages can hide important local differences.
- Berlin’s housing market shows clear spatial inequality in affordability.

**Overall, affording Berlin depends strongly on location, local rent pressure, and unequal housing conditions across the city.**

---

## Python Analysis
The Python part of the project includes:
- a **correlation heatmap** showing relationships between housing and social indicators
- a **rent distribution histogram** showing how listings cluster across price ranges

These visualizations help support the broader Tableau story.

---

## Tableau Storytelling
The Tableau part of the project presents the findings through dashboards and story points, including:
- Berlin at a glance
- district-level affordability overview
- district-part differences
- highest vs lowest rent burden
- rent trend over time
- rent distribution by district part

---

## Project Structure
```bash
Berlin_Housing_Final/
├── data/
│   ├── raw/
│   └── processed/
├── figures/
├── notebooks/
├── reports/
├── scripts/
├── .gitignore
```



---

## Important Files
- `notebooks/Berlin_Housing_Affordability_Analysis.ipynb`  
  Main notebook for cleaning, analysis, and visualizations

- `scripts/01_setup_postgres.sql`  
  PostgreSQL setup

- `scripts/02_load_data_to_postgres.py`  
  Load processed data into PostgreSQL

- `scripts/03_analysis_queries.sql`  
  SQL queries for analysis

- `scripts/berlin_affordability_analysis.py`  
  Additional analysis script

- `data/processed/berlin_affordability_master.csv`  
  Main district-level analysis dataset

- `data/processed/berlin_housing_detailed_tableau.csv`  
  Detailed housing dataset used for Tableau

⸻

---

## How to Run the Project
1. clone the repository  
2. open the project folder  
3. install the required Python libraries  
4. run the notebook or analysis scripts  
5. connect the processed CSV files or PostgreSQL tables to Tableau  
6. open the Tableau workbook / dashboards for the final visual story  

---

## Presentation
The final project also includes:
- a Google Slides presentation
- a Tableau story for interactive visual storytelling

---

## Author
**Munzer Al Awad**  
Data Analytics Project