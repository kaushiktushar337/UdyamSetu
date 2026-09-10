-- UdyamSetu location ID alignment
-- Use only when location_business_metrics.location_id is integer and
-- location_reference.location_id is UUID, and location_reference is still empty.
-- This changes only the new location_reference table and preserves its primary key.

BEGIN;

DO $$
DECLARE
    ref_type text;
    metric_type text;
    ref_rows bigint;
BEGIN
    SELECT COUNT(*) INTO ref_rows FROM public.location_reference;

    IF ref_rows <> 0 THEN
        RAISE EXCEPTION
            'Aborted: location_reference already contains % row(s).',
            ref_rows;
    END IF;

    SELECT data_type INTO ref_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'location_reference'
      AND column_name = 'location_id';

    SELECT data_type INTO metric_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'location_business_metrics'
      AND column_name = 'location_id';

    IF metric_type <> 'integer' THEN
        RAISE EXCEPTION
            'Aborted: location_business_metrics.location_id is %, expected integer.',
            metric_type;
    END IF;

    IF ref_type = 'integer' THEN
        RAISE NOTICE 'No change needed: location_reference.location_id is already integer.';
    ELSIF ref_type = 'uuid' THEN
        ALTER TABLE public.location_reference
            ALTER COLUMN location_id DROP DEFAULT;

        ALTER TABLE public.location_reference
            ALTER COLUMN location_id TYPE integer
            USING NULL::integer;

        RAISE NOTICE 'location_reference.location_id changed from UUID to integer.';
    ELSE
        RAISE EXCEPTION
            'Aborted: unsupported location_reference.location_id type: %.',
            ref_type;
    END IF;
END
$$;

COMMIT;
