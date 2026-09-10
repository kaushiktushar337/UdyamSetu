# Database Files

`ml_schema.sql` is the schema reference for the ML and Decision Engine tables.

The live application also expects the database team's existing application tables and these UdyamSetu integrations:

- `scheme_rules`
- `loan_plans`
- `location_reference`
- `location_business_metrics`
- `user_locations`
- chatbot conversation/message tables

`seed_reference_data.py` is a development/reference-data loader. It does not seed user conversations, analyses, or user locations.
