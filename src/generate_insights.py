
from urllib import response

from ollama import chat
import json

from prompt_toolkit import prompt



def validate_recommendations(data):

    required_keys = {
        "business_recommendation_1",
        "business_recommendation_2"
    }

    # Reject missing keys AND unexpected extra keys
    if not isinstance(data, dict) or set(data.keys()) != required_keys:
        raise ValueError(
            "Response must contain exactly the two required recommendation fields."
        )

    for key in required_keys:
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"Invalid or empty field: {key}")

    forbidden_terms = [
        "high-margin",
        "low-margin",
        "strong loyalty",
        "minimal churn",
        "guaranteed",
        "100% fill rate",
        "rolling 30-day",
        "subscription model",
        "monthly recurring revenue",
        "industry average",
        "customer demographics",
        "age, gender",
        "renewal triggers",
        "premium features",
        "profitability",
        "churn reduction",
        "lifetime value",
        "conversion rate",
        "high repeat purchase rate",
        "strong recurring revenue",
        "recurring revenue",
        "customer acquisition cost",
        "premium prices",
        "pricing optimization",
        "latent segment",
        "onboarding workflow",
        "significantly improve",
        "high or strong",
        "average order value",
        "sales volume",
        "efficiently",
        "targeted digital campaigns",
        "purchasing power",
        "directly increasing",
        "guaranteed improvement",
        "will increase",
        "will improve"
    ]

    for key in required_keys:
        text = data[key].lower()

        for term in forbidden_terms:
            if term in text:
                raise ValueError(
                    f"Unsupported claim in {key}: {term}"
                )

    return data



def build_evidence_sections(kpi_data):

    high_revenue = kpi_data["high_value_revenue_brl"]
    mid_revenue = kpi_data["mid_value_revenue_brl"]
    low_revenue = kpi_data["low_value_revenue_brl"]

    total_revenue = high_revenue + mid_revenue + low_revenue

    measured_facts = [
        {
            "statement": (
                f"High-value customers generated "
                f"R${high_revenue:,.2f} in historical revenue."
            ),
            "supporting_metrics": {
                "high_value_revenue_brl": high_revenue,
                "share_of_segment_revenue_pct":
                    round(high_revenue / total_revenue * 100, 2)
            }
        },
        {
            "statement": (
                f"Mid-value customers generated "
                f"R${mid_revenue:,.2f} in historical revenue."
            ),
            "supporting_metrics": {
                "mid_value_revenue_brl": mid_revenue,
                "share_of_segment_revenue_pct":
                    round(mid_revenue / total_revenue * 100, 2)
            }
        },
        {
            "statement": (
                f"The repeat purchase rate was "
                f"{kpi_data['repeat_purchase_rate']:.2f}%."
            ),
            "supporting_metrics": {
                "unique_customers": kpi_data["unique_customers"],
                "repeat_customers": kpi_data["repeat_customers"],
                "repeat_purchase_rate":
                    kpi_data["repeat_purchase_rate"]
            }
        }
    ]

    possible_explanations = [
        {
            "hypothesis": (
                "There may be opportunities to improve customer retention."
            ),
            "supporting_evidence": (
                f"The observed repeat purchase rate was "
                f"{kpi_data['repeat_purchase_rate']:.2f}%."
            ),
            "limitation": (
                "The available metrics do not establish why customers "
                "do not make repeat purchases."
            )
        }
    ]

    return {
        "measured_facts": measured_facts,
        "possible_explanations": possible_explanations
    }


monthly_revenue = [
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


def answer_business_question(question, monthly_data):

    question = question.lower()

    if "revenue decline" in question or "revenue decrease" in question:

        current_month = monthly_data[-1]
        previous_month = monthly_data[-2]

        current_revenue = current_month["revenue"]
        previous_revenue = previous_month["revenue"]

        revenue_change = current_revenue - previous_revenue

        if previous_revenue == 0:
            growth_rate = None
        else:
            growth_rate = (
                revenue_change / previous_revenue
            ) * 100

        if revenue_change < 0:
            result = (
                f"Revenue declined from "
                f"R${previous_revenue:,.2f} in "
                f"{previous_month['month']} to "
                f"R${current_revenue:,.2f} in "
                f"{current_month['month']}."
            )
        elif revenue_change > 0:
            result = (
                f"Revenue increased from "
                f"R${previous_revenue:,.2f} in "
                f"{previous_month['month']} to "
                f"R${current_revenue:,.2f} in "
                f"{current_month['month']}."
            )
        else:
            result = "Revenue remained unchanged."

        if growth_rate is not None:
            result += f" The change was {growth_rate:.2f}%."

        result += (
            " The available monthly revenue data does not "
            "establish the cause of this change."
        )

        return {
            "question": question,
            "answer": result,
            "measured_metrics": {
                "previous_month": previous_month["month"],
                "previous_revenue_brl": previous_revenue,
                "current_month": current_month["month"],
                "current_revenue_brl": current_revenue,
                "revenue_change_brl": round(revenue_change, 2),
                "revenue_growth_percentage": (
                    round(growth_rate, 2)
                    if growth_rate is not None else None
                )
            },
            "limitation": (
                "Monthly revenue figures alone cannot explain "
                "why revenue changed."
            )
        }

    return {
        "question": question,
        "answer": (
            "This question is not supported by the currently "
            "implemented question types."
        )
    }


def generate_insights(kpi_data):

    evidence = build_evidence_sections(kpi_data)
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

    # Python generates evidence-based recommendations
    recommendations = {
        "business_recommendation_1": (
            f"Investigate opportunities to encourage repeat purchases, "
            f"considering the current repeat purchase rate of "
            f"{kpi_data['repeat_purchase_rate']:.2f}%."
        ),

        "business_recommendation_2": (
            "Review the revenue contribution of high-value, mid-value, "
            "and low-value customer segments when prioritizing "
            "future customer engagement initiatives."
        )
    }
    
    # Combine verified observations and AI recommendations
    insights.update(recommendations)
    insights.update(evidence)
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
    question = "Why did revenue decline this month?"

    answer = answer_business_question(
        question,
        monthly_revenue
    )

    sample_output = {
        "business_insights": results,
        "business_question": answer
    }

    with open("docs/ai_insights_sample.json", "w", encoding="utf-8") as file:
        json.dump(sample_output, file, indent=4, ensure_ascii=False)

    print("\nSample insights saved to docs/ai_insights_sample.json")

    print("\nBusiness Question")
    print("=" * 40)
    print(json.dumps(answer, indent=4))
