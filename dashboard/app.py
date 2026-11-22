
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from datetime import date

from src.generate_insights import (
    generate_insights,
    answer_business_question
)

from ollama import chat
import json

# Monthly revenue data from PostgreSQL
monthly_data = [
    {"month": "2016-09", "revenue": 134.97},
    {"month": "2016-10", "revenue": 40325.11},
    {"month": "2016-11", "revenue": 0.00},
    {"month": "2016-12", "revenue": 10.90},
    {"month": "2017-01", "revenue": 111798.36},
    {"month": "2017-02", "revenue": 234223.40},
    {"month": "2017-03", "revenue": 359198.85},
    {"month": "2017-04", "revenue": 340669.68},
    {"month": "2017-05", "revenue": 489338.25},
    {"month": "2017-06", "revenue": 421923.37},
    {"month": "2017-07", "revenue": 481604.52},
    {"month": "2017-08", "revenue": 554699.70},
    {"month": "2017-09", "revenue": 607399.67},
    {"month": "2017-10", "revenue": 648247.65},
    {"month": "2017-11", "revenue": 987765.37},
    {"month": "2017-12", "revenue": 726033.19},
    {"month": "2018-01", "revenue": 924645.00},
    {"month": "2018-02", "revenue": 826437.13},
    {"month": "2018-03", "revenue": 953356.25},
    {"month": "2018-04", "revenue": 973534.09},
    {"month": "2018-05", "revenue": 977544.69},
    {"month": "2018-06", "revenue": 856077.86},
    {"month": "2018-07", "revenue": 867953.46},
    {"month": "2018-08", "revenue": 838576.64}
]

monthly_df = pd.DataFrame(monthly_data)
monthly_revenue = monthly_data

# Page configuration
st.set_page_config(
    page_title="E-commerce Business Intelligence",
    page_icon="📊",
    layout="wide"
)

# Dashboard title
st.title("📊 E-commerce Business Intelligence Dashboard")

st.markdown(
    "Monitor business performance, customer behavior, "
    "and product analytics."
)

st.divider()

# KPI Section
st.subheader("Business Performance Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Revenue",
        value="R$13.22M"
    )

with col2:
    st.metric(
        label="Delivered Orders",
        value="96,478"
    )

with col3:
    st.metric(
        label="Unique Customers",
        value="93,358"
    )

with col4:
    st.metric(
        label="Repeat Purchase Rate",
        value="3.00%"
    )

st.divider()

st.info(
    "Revenue represents delivered-order product revenue "
    "and excludes freight."
)

# Monthly Revenue Trend
st.subheader("Monthly Revenue Trend")

# Date filter
monthly_df["month_date"] = pd.to_datetime(monthly_df["month"])

date_range = st.sidebar.date_input(
    "Select Revenue Date Range",
    value=(
        monthly_df["month_date"].min().date(),
        monthly_df["month_date"].max().date()
    ),
    min_value=monthly_df["month_date"].min().date(),
    max_value=monthly_df["month_date"].max().date()
)

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_monthly_df = monthly_df[
        (monthly_df["month_date"] >= pd.Timestamp(start_date)) &
        (monthly_df["month_date"] <= pd.Timestamp(end_date))
    ]
else:
    filtered_monthly_df = monthly_df

st.line_chart(
    filtered_monthly_df,
    x="month",
    y="revenue",
    x_label="Month",
    y_label="Revenue (BRL)"
)

# Customer Segment Analysis

st.divider()
st.subheader("Customer Segment Analysis")

segment_data = [
    {
        "segment": "High Revenue Customers",
        "customers": 37665,
        "avg_recency": 278.98,
        "avg_frequency": 1.00,
        "avg_monetary": 237.26
    },
    {
        "segment": "Low Revenue Customers",
        "customers": 36601,
        "avg_recency": 285.20,
        "avg_frequency": 1.00,
        "avg_monetary": 45.10
    },
    {
        "segment": "Repeat Customers",
        "customers": 2801,
        "avg_recency": 220.81,
        "avg_frequency": 2.11,
        "avg_monetary": 260.05
    },
    {
        "segment": "Recent Customers",
        "customers": 16291,
        "avg_recency": 42.93,
        "avg_frequency": 1.00,
        "avg_monetary": 116.99
    }
]

segment_df = pd.DataFrame(segment_data)

selected_segments = st.sidebar.multiselect(
    "Select Customer Segments",
    options=segment_df["segment"].tolist(),
    default=segment_df["segment"].tolist()
)

filtered_segment_df = segment_df[
    segment_df["segment"].isin(selected_segments)
]

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Customer Distribution")

    st.bar_chart(
        filtered_segment_df,
        x="segment",
        y="customers",
        x_label="Customer Segment",
        y_label="Number of Customers"
    )

with col2:
    st.markdown("#### Average Customer Revenue")

    st.bar_chart(
        filtered_segment_df,
        x="segment",
        y="avg_monetary",
        x_label="Customer Segment",
        y_label="Average Revenue (BRL)"
    )

st.markdown("#### Customer Segment Details")

st.dataframe(
    filtered_segment_df,
    use_container_width=True,
    hide_index=True
)

# Product Performance Analysis

st.divider()
st.subheader("Product Category Performance")

product_data = [
    {"category": "Health & Beauty", "revenue": 1233131.72},
    {"category": "Watches & Gifts", "revenue": 1166176.98},
    {"category": "Bed, Bath & Table", "revenue": 1023434.76},
    {"category": "Sports & Leisure", "revenue": 954852.55},
    {"category": "Computers & Accessories", "revenue": 888724.61}
]

product_df = pd.DataFrame(product_data)

st.markdown("#### Top 5 Categories by Revenue")

selected_categories = st.sidebar.multiselect(
    "Select Product Categories",
    options=product_df["category"].tolist(),
    default=product_df["category"].tolist()
)

filtered_product_df = product_df[
    product_df["category"].isin(selected_categories)
]

st.bar_chart(
    filtered_product_df,
    x="category",
    y="revenue",
    x_label="Product Category",
    y_label="Revenue (BRL)",
    horizontal=True
)

st.markdown("#### Category Revenue Details")

st.dataframe(
    filtered_product_df,
    use_container_width=True,
    hide_index=True
)

# AI Executive Summary

st.divider()

st.header("🤖 AI-Powered Executive Summary")

kpis = {
    "unique_customers": 93358,
    "repeat_customers": 2801,
    "repeat_purchase_rate": 3.00,
    "high_value_revenue_brl": 7486237.06,
    "mid_value_revenue_brl": 3529087.20,
    "low_value_revenue_brl": 2206173.85
}

ai_insights = generate_insights(kpis)


# Ollama-powered Executive Summary

st.subheader("AI-Generated Executive Summary")

if st.button("Generate AI Executive Summary"):

    # Send verified business metrics, not raw customer data
    verified_context = {
        "measured_facts": ai_insights["measured_facts"],
        "possible_explanations": ai_insights["possible_explanations"],
        "latest_monthly_revenue": monthly_revenue[-2:]
    }


    prompt = f"""
    You are a senior business intelligence analyst preparing
    an executive briefing for an e-commerce business manager.

    VERIFIED BUSINESS DATA:
    {json.dumps(verified_context, indent=2)}

    Write an executive summary with exactly these sections:

    1. BUSINESS PERFORMANCE
    Summarize the most important customer and revenue findings.

    2. KEY OBSERVATIONS
    Identify important patterns in customer value and repeat purchasing.
    Also compare the latest two months of revenue.

    3. RECOMMENDED ACTIONS
    Give two practical actions management could investigate.

    4. DATA LIMITATIONS
    Explain what the available metrics cannot establish.

    Rules:
    - Use only the supplied metrics.
    - Include relevant numerical evidence.
    - Do not invent statistics.
    - Do not present hypotheses as proven causes.
    - Keep the language clear and professional.
    - Keep the entire response under 200 words.
    """


    with st.spinner("Generating executive summary..."):

        try:
            response = chat(
                model="qwen3.5:0.8b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={"temperature": 0.2}
            )

            ai_summary = response.message.content

            st.markdown(ai_summary)

        except Exception as e:
            st.error(f"Could not generate AI summary: {e}")


st.subheader("Business Insights")

st.info(ai_insights["business_insight_1"])

st.info(ai_insights["business_insight_2"])

st.info(ai_insights["business_insight_3"])

st.subheader("Recommended Business Actions")

st.write(
    "1. " + ai_insights["business_recommendation_1"]
)

st.write(
    "2. " + ai_insights["business_recommendation_2"]
)

with st.expander("View Supporting Evidence"):

    st.write("Measured Facts")

    st.json(ai_insights["measured_facts"])

    st.write("Possible Explanations")

    st.json(ai_insights["possible_explanations"])


# AI Business Question Interface

st.divider()

st.header("💬 Ask Your Business Data")

st.write(
    "Ask questions about business performance "
    "and receive answers supported by calculated metrics."
)

question = st.text_input(
    "Enter your business question",
    placeholder="Why did revenue decline this month?"
)

if st.button("Generate Answer"):

    if question.strip():

        answer = answer_business_question(
            question,
            monthly_revenue
        )

        st.subheader("Business Answer")

        st.write(answer["answer"])

        if "measured_metrics" in answer:

            st.subheader("Supporting Metrics")

            st.json(answer["measured_metrics"])

            st.caption(
                answer["limitation"]
            )

    else:
        st.warning("Please enter a business question.")
