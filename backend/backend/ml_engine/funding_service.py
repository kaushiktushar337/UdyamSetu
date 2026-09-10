from __future__ import annotations

import os
import re
from typing import Any


class FundingService:
    """Structured retrieval/ranking for scheme_rules and loan_plans.

    The service never invents eligibility rules. It only ranks rows that are
    actually present in the database and exposes their stored fields.
    """

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

    def _connect(self):
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is missing")
        import psycopg2
        return psycopg2.connect(self.database_url)

    @staticmethod
    def _money(value: Any) -> float | None:
        return float(value) if value is not None else None

    @staticmethod
    def _parse_amount(text: str) -> float | None:
        # Supports common Indian formats: 5 lakh, ₹500000, 2.5 crore, etc.
        match = re.search(r"(?:₹|rs\.?\s*)?([0-9]+(?:\.[0-9]+)?)\s*(crore|cr|lakh|lac|k)?", text.lower())
        if not match:
            return None
        value = float(match.group(1))
        unit = match.group(2)
        if unit in {"crore", "cr"}:
            value *= 10_000_000
        elif unit in {"lakh", "lac"}:
            value *= 100_000
        elif unit == "k":
            value *= 1_000
        return value

    @staticmethod
    def is_funding_query(text: str) -> bool:
        value = text.lower()
        return any(word in value for word in [
            "loan", "scheme", "subsidy", "funding", "finance", "borrow",
            "credit", "mudra", "interest rate", "emi", "bank loan", "government scheme",
        ])

    @staticmethod
    def _parse_integer(text: str, patterns: list[str]) -> int | None:
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        return None

    @staticmethod
    def detect_category(text: str) -> str | None:
        value = text.lower()
        groups = {
            "dairy": ["dairy", "milk", "cattle", "buffalo", "cow"],
            "retail": ["retail", "kirana", "grocery", "shop", "store"],
            "food processing": ["food processing", "pickle", "spice", "flour", "bakery", "food unit"],
            "textiles": ["textile", "tailoring", "garment", "cloth", "weaving"],
            "services": ["service", "repair", "salon", "consultancy", "digital service"],
            "agriculture": ["agriculture", "farm", "farming", "poultry", "goat", "livestock"],
        }
        for category, keywords in groups.items():
            if any(k in value for k in keywords):
                return category
        return None

    def list_schemes(self, *, project_cost: float | None = None, category: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, scheme_name, scheme_code, description, min_project_cost,
                              max_project_cost, margin_ratio, funding_ratio, max_loan_amount,
                              interest_rate, tenure_months, moratorium_months,
                              moratorium_interest_treatment, version, effective_from,
                              effective_until, is_active
                       FROM scheme_rules
                       WHERE is_active = true
                         AND effective_from <= CURRENT_DATE
                         AND (effective_until IS NULL OR effective_until >= CURRENT_DATE)
                       ORDER BY min_project_cost ASC, interest_rate ASC"""
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        category_l = (category or "").lower().strip()
        result = []
        for r in rows:
            min_cost, max_cost = float(r[4]), float(r[5])
            score = 50.0
            reasons: list[str] = ["Active and within its stored effective date range."]
            if project_cost is not None:
                if min_cost <= project_cost <= max_cost:
                    score += 45
                    reasons.append("Your project cost falls within the scheme's stored project-cost range.")
                elif project_cost < min_cost:
                    distance = (min_cost - project_cost) / max(min_cost, 1)
                    score += max(0, 20 - 20 * distance)
                    reasons.append("Your project cost is below the stored minimum project cost.")
                else:
                    distance = (project_cost - max_cost) / max(project_cost, 1)
                    score += max(0, 20 - 20 * distance)
                    reasons.append("Your project cost is above the stored maximum project cost.")
            text = f"{r[1]} {r[3] or ''}".lower()
            if category_l and category_l in text:
                score += 5
                reasons.append("The stored scheme name/description mentions your business category.")
            result.append({
                "id": r[0], "scheme_name": r[1], "scheme_code": r[2], "description": r[3],
                "min_project_cost": min_cost, "max_project_cost": max_cost,
                "margin_ratio": float(r[6]), "funding_ratio": float(r[7]),
                "max_loan_amount": float(r[8]), "interest_rate": float(r[9]),
                "tenure_months": r[10], "moratorium_months": r[11],
                "moratorium_interest_treatment": r[12], "version": r[13],
                "effective_from": r[14].isoformat() if r[14] else None,
                "effective_until": r[15].isoformat() if r[15] else None,
                "is_active": bool(r[16]), "match_score": round(min(score, 100), 1),
                "match_reasons": reasons,
                "source_type": "database.scheme_rules",
            })
        result.sort(key=lambda x: (-x["match_score"], x["interest_rate"], x["max_project_cost"]))
        return result[:limit]

    def list_loans(
        self,
        *,
        loan_amount: float | None = None,
        category: str | None = None,
        state: str | None = None,
        district: str | None = None,
        age: int | None = None,
        credit_score: int | None = None,
        business_vintage_months: int | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, loan_plan_id, bank_or_institution_name, plan_name,
                              institution_type, geographic_scope, geographic_focus,
                              target_segments, min_loan_amount, max_loan_amount,
                              interest_rate_min, interest_rate_max, interest_type,
                              tenure_min_months, tenure_max_months, moratorium_months,
                              processing_fee_pct, margin_money_pct, collateral_required,
                              scheme_guarantee, min_age, max_age, min_credit_score,
                              business_vintage_months, documentation, source_url,
                              key_features, is_active
                       FROM loan_plans
                       WHERE is_active = true"""
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        cat = (category or "").lower().strip()
        state_l = (state or "").lower().strip()
        district_l = (district or "").lower().strip()
        result = []
        for r in rows:
            min_loan = self._money(r[8])
            max_loan = self._money(r[9])
            score = 30.0
            reasons: list[str] = ["Active loan plan stored in the database."]
            eligible = True

            if loan_amount is not None and min_loan is not None and max_loan is not None:
                if min_loan <= loan_amount <= max_loan:
                    score += 45
                    reasons.append("Requested loan amount falls within the stored loan range.")
                else:
                    eligible = False
                    reasons.append("Requested loan amount is outside the stored loan range.")

            text = " ".join(str(x or "") for x in [r[3], r[5], r[6], r[7], r[26]]).lower()
            if cat and cat in text:
                score += 15
                reasons.append("The stored loan-plan data mentions your business category/segment.")
            if state_l or district_l:
                geographic = f"{r[5] or ''} {r[6] or ''}".lower()
                if (state_l and state_l in geographic) or (district_l and district_l in geographic) or "india" in geographic or "national" in geographic:
                    score += 10
                    reasons.append("The stored geographic scope/focus covers the requested area.")

            if age is not None:
                if r[21] is not None and age < r[21]:
                    eligible = False
                    reasons.append("Applicant age is below the stored minimum age.")
                if r[22] is not None and age > r[22]:
                    eligible = False
                    reasons.append("Applicant age is above the stored maximum age.")
            if credit_score is not None and r[23] is not None and credit_score < r[23]:
                eligible = False
                reasons.append("Credit score is below the stored minimum.")
            if business_vintage_months is not None and r[24] is not None and business_vintage_months < r[24]:
                eligible = False
                reasons.append("Business vintage is below the stored minimum.")

            result.append({
                "id": r[0], "loan_plan_id": r[1], "bank_or_institution_name": r[2], "plan_name": r[3],
                "institution_type": r[4], "geographic_scope": r[5], "geographic_focus": r[6],
                "target_segments": r[7], "min_loan_amount": min_loan, "max_loan_amount": max_loan,
                "interest_rate_min": self._money(r[10]), "interest_rate_max": self._money(r[11]),
                "interest_type": r[12], "tenure_min_months": r[13], "tenure_max_months": r[14],
                "moratorium_months": r[15], "processing_fee_pct": self._money(r[16]),
                "margin_money_pct": self._money(r[17]), "collateral_required": bool(r[18]),
                "scheme_guarantee": r[19], "min_age": r[20], "max_age": r[21],
                "min_credit_score": r[22], "business_vintage_months": r[23],
                "documentation": r[24], "source_url": r[25], "key_features": r[26],
                "is_active": bool(r[27]), "eligible_on_supplied_data": eligible,
                "match_score": round(min(score, 100), 1), "match_reasons": reasons,
                "source_type": "database.loan_plans",
            })
        result.sort(key=lambda x: (-int(x["eligible_on_supplied_data"]), -x["match_score"], x["interest_rate_min"] if x["interest_rate_min"] is not None else 999))
        return result[:limit]

    def recommend(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "schemes": self.list_schemes(
                project_cost=kwargs.get("project_cost"), category=kwargs.get("category"), limit=kwargs.get("limit", 5)
            ),
            "loans": self.list_loans(
                loan_amount=kwargs.get("loan_amount"), category=kwargs.get("category"),
                state=kwargs.get("state"), district=kwargs.get("district"),
                age=kwargs.get("age"), credit_score=kwargs.get("credit_score"),
                business_vintage_months=kwargs.get("business_vintage_months"), limit=kwargs.get("limit", 5)
            ),
        }

    def chat_context(self, message: str, location_text: str | None = None) -> str:
        category = self.detect_category(message)
        project_cost = self._parse_amount(message)
        loan_amount = None
        lower = message.lower()
        if "loan" in lower or "borrow" in lower or "finance" in lower:
            loan_amount = project_cost
        age = self._parse_integer(message, [r"(?:age|aged)\s*(?:is|:)?\s*(\d{1,3})", r"(\d{1,3})\s*(?:years old|yrs old)"])
        credit_score = self._parse_integer(message, [r"(?:credit score|cibil)\s*(?:is|:)?\s*(\d{3,4})"])
        vintage = self._parse_integer(message, [r"(?:business )?(?:vintage|age)\s*(?:is|:)?\s*(\d+)\s*(?:months?|month)"])
        state = district = None
        if location_text:
            parts = [p.strip() for p in location_text.split(",") if p.strip()]
            if len(parts) >= 2:
                state, district = parts[-1], parts[-2]
        data = self.recommend(
            category=category, project_cost=project_cost, loan_amount=loan_amount,
            state=state, district=district, age=age, credit_score=credit_score,
            business_vintage_months=vintage, limit=5,
        )
        lines = ["STRUCTURED FUNDING DATA FROM DATABASE (use only these stored facts):"]
        if data["schemes"]:
            lines.append("SCHEME OPTIONS:")
            for s in data["schemes"]:
                lines.append(
                    f"- {s['scheme_name']} [{s['scheme_code']}]: project ₹{s['min_project_cost']:,.0f}-₹{s['max_project_cost']:,.0f}; "
                    f"funding ratio {s['funding_ratio']}; max loan ₹{s['max_loan_amount']:,.0f}; interest {s['interest_rate']}%; "
                    f"tenure {s['tenure_months']} months; reasons: {' '.join(s['match_reasons'])}"
                )
        if data["loans"]:
            lines.append("LOAN OPTIONS:")
            for l in data["loans"]:
                lines.append(
                    f"- {l['plan_name']} ({l['bank_or_institution_name']}) [{l['loan_plan_id']}]: "
                    f"₹{l['min_loan_amount'] or 0:,.0f}-₹{l['max_loan_amount'] or 0:,.0f}; "
                    f"interest {l['interest_rate_min']}%-{l['interest_rate_max']}%; "
                    f"eligible_on_supplied_data={l['eligible_on_supplied_data']}; reasons: {' '.join(l['match_reasons'])}"
                )
        lines.append("Do not claim approval or eligibility beyond the stored fields. Tell the user when required eligibility data is missing.")
        return "\n".join(lines)
