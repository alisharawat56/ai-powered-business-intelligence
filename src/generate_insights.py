
from ollama import chat
import json


def validate_recommendations(data):

    required_keys = [
        "business_recommendation_1",
        "business_recommendation_2"
    ]

    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required field: {key}")

        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"Invalid or empty field: {key}")

    forbidden_terms = [
        "high-margin",
        "low-margin",
        "strong loyalty",
        "minimal churn",
        "guaranteed",
        "100% fill rate",
        "rolling 30-day"
    ]

    for key in required_keys:
        text = data[key].lower()

        for term in forbidden_terms:
            if term in text:
                raise ValueError(
                    f"Unsupported claim in {key}: {term}"
                )

    return data


def generate_insights(kpi_data):

    # Python generates verified observations
    insights = {
        "business_insight_1": (
            f"High-value customers generated "
            f"R${kpi_data['high_value_revenue_brl']:,.2f} "
            f"in historical revenue."
        ),

        "business_insight_2": (
            f"Mid-value customers generated "
            f"R${kpi_data['mid_value_revenue_brl']:,.2f} "
            f"in historical revenue."
        ),

        "business_insight_3": (
            f"{kpi_data['repeat_customers']:,} out of "
            f"{kpi_data['unique_customers']:,} unique customers "
            f"were repeat customers. The repeat purchase rate "
            f"was {kpi_data['repeat_purchase_rate']:.2f}%."
        )
    }

    # Qwen generates recommendations only
    prompt = f"""
    You are an e-commerce business intelligence assistant.

    Verified business metrics:
    {json.dumps(kpi_data, indent=2)}

    Generate exactly two practical business recommendations.

    Rules:
    - Use only the supplied metrics.
    - Do not invent numbers.
    - Do not claim profitability or causation.
    - Do not assume customer behavior.
    - Do not describe the 3% repeat purchase rate as strong.
    - Recommendations must be suggestions, not proven solutions.
    - Do not introduce specific time periods, targets, budgets, or numerical thresholds that are not supplied.

    Return valid JSON with exactly these keys:
    {{
        "business_recommendation_1": "First recommendation",
        "business_recommendation_2": "Second recommendation"
    }}
    """

    response = chat(
        model="qwen3.5:0.8b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        think=False,
        format="json"
    )

    recommendations = json.loads(response.message.content)

    validate_recommendations(recommendations)

    # Combine verified observations and AI recommendations
    insights.update(recommendations)

    return insights


if __name__ == "__main__":

    kpis = {
        "unique_customers": 93358,
        "repeat_customers": 2801,
        "repeat_purchase_rate": 3.00,
        "high_value_revenue_brl": 7486237.06,
        "mid_value_revenue_brl": 3529087.20,
        "low_value_revenue_brl": 2206173.85
    }

    results = generate_insights(kpis)

    print("\nAI-Powered Business Insights")
    print("=" * 40)

    print(json.dumps(results, indent=4))
