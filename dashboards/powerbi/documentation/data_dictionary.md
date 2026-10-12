# NEXUS-M Power BI Data Dictionary

## Transaction Metrics

| Field | Meaning |
|---|---|
| transaction_count | Number of payment transactions |
| transaction_value | Total monetary value of transactions |
| successful_transactions | Transactions successfully authorized |
| failed_transactions | Transactions that failed |
| success_rate | Percentage of successful transactions |
| failure_rate | Percentage of failed transactions |
| average_latency_ms | Average payment processing latency |
| p95_latency_ms | 95th percentile processing latency |
| p99_latency_ms | 99th percentile processing latency |

## Merchant Metrics

| Field | Meaning |
|---|---|
| merchant_key | Internal merchant identifier |
| transaction_count | Merchant transaction volume |
| transaction_value | Merchant transaction value |
| success_rate | Merchant authorization success rate |
| failure_rate | Merchant failure rate |
| value_at_risk | Transaction value exposed to failure |
| business_segment | Rule-based merchant segment |
| cluster | ML-derived merchant cluster |

## Partner Metrics

| Field | Meaning |
|---|---|
| partner_key | Payment partner identifier |
| transaction_count | Partner transaction volume |
| success_rate | Partner success rate |
| failure_rate | Partner failure rate |
| latency | Partner processing latency |

## Opportunity Metrics

| Field | Meaning |
|---|---|
| value_at_risk | Value associated with failed transactions |
| recoverable_value | Estimated value that could potentially be recovered |
| priority | Opportunity priority |
| opportunity_score | Relative prioritization score |

## Reconciliation Metrics

| Field | Meaning |
|---|---|
| settlement_found | Whether settlement exists |
| amount_difference | Transaction vs settlement difference |
| timing_mismatch | Settlement timing exception |
| exception_type | Classification of reconciliation exception |