from app.engines.base_engine import BaseEngine

INDUSTRY_BENCHMARKS = {
    "healthcare": {
        "efficiency_gain_pct": 25,
        "cost_reduction_pct": 20,
        "error_reduction_pct": 35,
        "revenue_impact_pct": 15,
        "payback_months": 10,
    },
    "erp": {
        "efficiency_gain_pct": 30,
        "cost_reduction_pct": 25,
        "error_reduction_pct": 40,
        "revenue_impact_pct": 20,
        "payback_months": 14,
    },
    "crm": {
        "efficiency_gain_pct": 20,
        "cost_reduction_pct": 15,
        "error_reduction_pct": 20,
        "revenue_impact_pct": 25,
        "payback_months": 8,
    },
    "hrms": {
        "efficiency_gain_pct": 35,
        "cost_reduction_pct": 30,
        "error_reduction_pct": 45,
        "revenue_impact_pct": 10,
        "payback_months": 9,
    },
    "manufacturing": {
        "efficiency_gain_pct": 28,
        "cost_reduction_pct": 22,
        "error_reduction_pct": 30,
        "revenue_impact_pct": 18,
        "payback_months": 15,
    },
    "retail": {
        "efficiency_gain_pct": 22,
        "cost_reduction_pct": 18,
        "error_reduction_pct": 25,
        "revenue_impact_pct": 22,
        "payback_months": 9,
    },
    "logistics": {
        "efficiency_gain_pct": 32,
        "cost_reduction_pct": 28,
        "error_reduction_pct": 35,
        "revenue_impact_pct": 15,
        "payback_months": 12,
    },
    "education": {
        "efficiency_gain_pct": 25,
        "cost_reduction_pct": 20,
        "error_reduction_pct": 30,
        "revenue_impact_pct": 12,
        "payback_months": 11,
    },
    "government": {
        "efficiency_gain_pct": 20,
        "cost_reduction_pct": 15,
        "error_reduction_pct": 25,
        "revenue_impact_pct": 5,
        "payback_months": 18,
    },
    "finance": {
        "efficiency_gain_pct": 30,
        "cost_reduction_pct": 25,
        "error_reduction_pct": 40,
        "revenue_impact_pct": 20,
        "payback_months": 12,
    },
}


class ROIEngine(BaseEngine):
    name = "roi"

    def run(self, context: dict) -> dict:
        industry = (context.get("industry_data") or {}).get("industry", "custom")
        pricing = context.get("pricing_data", {})
        automation = context.get("automation_data", {})

        benchmarks = INDUSTRY_BENCHMARKS.get(industry, {
            "efficiency_gain_pct": 20,
            "cost_reduction_pct": 15,
            "error_reduction_pct": 20,
            "revenue_impact_pct": 10,
            "payback_months": 12,
        })

        total_cost = pricing.get("one_time_cost", 50000)
        monthly_cost = pricing.get("monthly_cost", 1500)
        annual_cost = pricing.get("annual_cost", total_cost + monthly_cost * 12)

        annual_operating_cost = monthly_cost * 12
        estimated_salary_burden = 120000
        annual_savings = round(estimated_salary_burden * benchmarks["efficiency_gain_pct"] / 100)
        error_savings = round(total_cost * benchmarks["error_reduction_pct"] / 100)
        total_annual_benefit = annual_savings + error_savings

        net_annual_benefit = total_annual_benefit - annual_operating_cost
        roi_pct = round((net_annual_benefit / total_cost) * 100, 1) if total_cost > 0 else 0
        payback_months = round((total_cost / max(total_annual_benefit, 1)) * 12, 1)

        three_year_roi = round(((total_annual_benefit * 3 - annual_operating_cost * 3 - total_cost) / total_cost) * 100, 1)

        return {
            "roi_percentage": roi_pct,
            "three_year_roi_pct": three_year_roi,
            "payback_period_months": payback_months,
            "annual_savings": annual_savings,
            "error_reduction_savings": error_savings,
            "total_annual_benefit": total_annual_benefit,
            "total_investment": total_cost,
            "annual_operating_cost": annual_operating_cost,
            "net_annual_benefit": net_annual_benefit,
            "efficiency_gain_pct": benchmarks["efficiency_gain_pct"],
            "cost_reduction_pct": benchmarks["cost_reduction_pct"],
            "error_reduction_pct": benchmarks["error_reduction_pct"],
            "industry_benchmark": benchmarks,
            "roi_metrics": [
                {"metric": "Payback Period", "value": f"{payback_months} months"},
                {"metric": "1-Year ROI", "value": f"{roi_pct}%"},
                {"metric": "3-Year ROI", "value": f"{three_year_roi}%"},
                {"metric": "Annual Efficiency Gain", "value": f"{benchmarks['efficiency_gain_pct']}%"},
                {"metric": "Annual Cost Reduction", "value": f"${annual_savings:,}"},
            ],
        }
