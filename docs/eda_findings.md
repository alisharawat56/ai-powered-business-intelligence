# Initial Data Quality and EDA Findings

## Dataset Overview

Seven Olist datasets were inspected:

- Customers: 99,441 rows
- Orders: 99,441 rows
- Order items: 112,650 rows
- Payments: 103,886 rows
- Reviews: 99,224 rows
- Products: 32,951 rows
- Sellers: 3,095 rows

No exact duplicate rows were identified in these datasets.

## Missing Value Analysis

**Orders**
- Missing delivery timestamps are largely associated with orders that have not been delivered, were canceled, or became unavailable.
- Eight delivered orders have missing customer delivery timestamps and require investigation.
- Missing timestamps will be preserved rather than artificially populated.

**Reviews**
- Review titles are missing in 88.34% of records.
- Review messages are missing in 58.70% of records.
- Review scores have no missing values.
- Missing comments will be retained as null values.

**Products**
- 610 products have missing categories and related descriptive attributes.
- Two products have missing physical dimensions and weight.
- Missing categories will be labeled `unknown`.
- Missing physical measurements will remain null.

## Preliminary Business Insights

- 96,478 orders have a delivered status.
- 57,328 reviews have a score of 5.
- 11,424 reviews have a score of 1.
- Review scores are concentrated toward the positive end of the scale.

## Next Steps

- Investigate anomalous delivered orders.
- Validate relationships between orders, customers, products, and payments.
- Perform revenue and product-category analysis using SQL.
- Analyze repeat customer behavior and purchasing trends.


### Customer Segmentation Findings

Using NTILE(10), customers were divided into three revenue-based segments:

- **High Value:** 18,672 customers, average revenue R$400.93 per customer.
- **Mid Value:** 28,008 customers, average revenue R$126.00 per customer.
- **Low Value:** 46,678 customers, average revenue R$47.26 per customer.

The high-value segment represents approximately 20% of customers but contributes around 57% of total product revenue. This suggests that customer retention and personalized engagement with high-value customers could be important strategies for the marketplace.

The segmentation is based on historical revenue, not purchase frequency or predicted lifetime value.


### Payment Method Analysis

Credit cards are the dominant payment method, accounting for 74,304 delivered orders and R$12.10 million in recorded payment value.

Boleto is the second most common payment method, with 19,191 orders and R$2.77 million in payment value.

Vouchers have the lowest average payment value at R$62.45, while credit cards have the highest at R$162.24.

**Business implication:** Olist should maintain a smooth credit-card payment experience while investigating opportunities to improve adoption of other payment methods.

**Metric note:** Payment records are not necessarily equivalent to unique orders because an order can contain multiple payment records.


### Revenue Anomaly Analysis

A statistical outlier analysis was performed using the three-standard-deviation method on delivered order revenue.

- Average order revenue: R$137.04
- Standard deviation: R$209.05
- Anomaly threshold: R$764.19
- Number of flagged orders returned: 9

The highest-revenue order was R$13,440.

These transactions may represent legitimate high-value purchases rather than data-quality issues. Further investigation is recommended before excluding them from the analysis.

**Business implication:** Olist should monitor unusually high-value orders because they can influence revenue averages, customer segmentation, and business reporting.

### Customer Cohort Retention Analysis

Customer cohorts were created based on the month of their first delivered order, using `customer_unique_id`.

The October 2016 cohort contained 262 customers.

Some customers returned in later months, but observed monthly retention was very low. For example, one customer returned in month 6 (0.38% retention), while two returned in month 19 (0.76%).

**Business implication:** Olist has an opportunity to improve customer retention through personalized follow-ups, loyalty programs, and targeted repeat-purchase campaigns.

**Metric definition:** Monthly cohort retention measures the percentage of customers from an original acquisition cohort who placed another delivered order in a particular subsequent month.


### RFM Customer Segmentation

Customer segmentation was performed using Recency, Frequency, and Monetary (RFM) analysis.

Six customer segments were identified: Champions, Loyal Customers, Potential Loyalists, At Risk, Hibernating, and Needs Attention.

Key findings:
- At-Risk customers generated the highest historical segment revenue at approximately R$4.70 million.
- Champions had the highest average historical customer revenue at R$274.05.
- Hibernating customers had the lowest average historical customer revenue at R$41.08.
- The At-Risk segment represents an opportunity for targeted customer re-engagement campaigns.
- Champions represent an opportunity for loyalty programs and personalized marketing.

The segmentation uses historical transactions and rule-based RFM scoring. It does not predict future churn or customer lifetime value.


### Order Value and Freight Analysis

An analysis of delivered orders revealed an inverse relationship between order value and the percentage of revenue spent on freight.

Key findings:
- Orders below R$50 had an average freight-to-product-value ratio of 48.38%.
- Orders above R$500 had an average ratio of 6.19%.
- The three lowest order-value groups accounted for approximately 88.3% of analyzed orders.
- Average freight charges increased with order value, but at a slower rate than product value.

Business implication:

The marketplace could investigate free-shipping thresholds, product bundling, and targeted shipping incentives to improve the attractiveness of low-value purchases. These strategies should be tested before implementation.


### High-Value and At-Risk Customer Analysis

A comparison of Champions and At-Risk customers revealed:

- At-Risk customers: 22,026 customers, R$4.70 million in historical revenue, and average recency of 394.3 days.
- Champions: 15,108 customers, R$4.14 million in historical revenue, and average recency of 92 days.
- Champions had higher average historical revenue per customer (R$274.06) than At-Risk customers (R$213.23).
- Both segments had average purchase frequencies close to one order per customer.

Business recommendations:
1. Develop targeted re-engagement campaigns for At-Risk customers.
2. Introduce loyalty initiatives for Champions.
3. Investigate why previously valuable customers have not returned.
4. Monitor repeat-purchase rates to evaluate retention campaign effectiveness.

RFM scores are relative customer rankings based on historical transactions and should not be interpreted as predictive churn scores.