# AI-Powered Business Intelligence & Analytics

An end-to-end e-commerce analytics platform designed to analyze business performance, understand customer purchasing behavior, identify trends, and generate AI-powered business recommendations.

## Project Overview

This project uses real-world e-commerce transaction data from the Brazilian Olist marketplace to develop an interactive business intelligence and analytics solution.

The platform will combine data analysis, SQL, statistical techniques, machine learning, and large language models to transform raw transactional data into actionable business insights.

## Objectives

- Analyze revenue and sales performance.
- Identify top-performing products and categories.
- Measure customer retention and repeat purchases.
- Develop RFM customer segments.
- Apply machine learning for customer clustering.
- Generate evidence-based business recommendations using an LLM.

## Technology Stack

- Python
- Pandas and NumPy
- PostgreSQL and SQL
- Scikit-learn
- Tableau / Power BI
- Streamlit
- LLM API
- Git and GitHub

## Dataset

Brazilian E-Commerce Public Dataset by Olist.

Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Download and extract the dataset into `data/raw/`.

The dataset is not included in this repository.

## Project Structure

```text
ai-powered-business-intelligence/
├── data/
├── notebooks/
├── src/
├── sql/
├── dashboard/
├── docs/
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies using `pip install -r requirements.txt`.
4. Download the Olist dataset into `data/raw/`.
5. Configure PostgreSQL credentials in a local `.env` file.
6. Run the data-loading script using `python src/load_data.py`.

## Project Status

Currently in development.

## Data Cleaning and Exploratory Data Analysis

### Data Cleaning
Used Python, Pandas, and NumPy to:
- Inspect missing values and duplicate records.
- Convert timestamp columns into appropriate datetime formats.
- Validate numerical fields.
- Identify missing product categories and delivery timestamps.
- Preserve optional fields rather than filling them with arbitrary values.

### SQL Analysis
Used PostgreSQL to perform:
- Revenue analysis by product category.
- Month-over-month revenue trend analysis.
- Customer purchase and repeat purchase analysis.
- Customer revenue segmentation using `NTILE()`.
- Payment method analysis.
- Revenue anomaly detection using common table expressions and statistical thresholds.

### Exploratory Data Analysis
Created an EDA notebook using Pandas, Matplotlib, and Seaborn.

The notebook includes:
- Dataset overview and data quality checks.
- Missing-value visualizations.
- Product category revenue analysis.
- Monthly revenue trends.
- Customer behavior and segmentation.
- Payment method analysis.
- Customer satisfaction analysis.

### Key Business Findings
- Health & Beauty was the highest-revenue product category.
- The repeat purchase rate was approximately 3%.
- High-value customers contributed approximately 57% of customer revenue.
- Credit cards were the dominant payment method.
- Several unusually high-revenue orders were identified for further investigation.

### Tools Used
Python | Pandas | NumPy | PostgreSQL | SQL | Matplotlib | Seaborn

## Author

Alisha Rawat