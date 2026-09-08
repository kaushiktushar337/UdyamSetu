"""
Quick integration demo.

Requires DATABASE_URL and the 40 business profiles to be imported into
business_reference_profiles.
"""

from ml_engine.profile_loader import BusinessProfileLoader
from ml_engine.business_matcher import BusinessMatcher, build_user_business_query

loader = BusinessProfileLoader()
profiles = loader.load_profiles()

matcher = BusinessMatcher().fit(profiles)

query = build_user_business_query(
    interests="food processing and locally available agricultural products",
    skills="basic food preparation and small business management",
    preferences="small business with manageable startup cost",
    location_context="semi-urban India",
)

matches = matcher.match(
    user_text=query,
    available_capital=500000,
    top_k=5,
)

for index, match in enumerate(matches, 1):
    print(f"\n{index}. {match.profile.business_name}")
    print(f"   Final match score: {match.final_score}/100")
    print(f"   Semantic score: {match.semantic_score}/100")
    print(f"   Capital score: {match.capital_score}/100")
    for reason in match.reasons:
        print(f"   - {reason}")
