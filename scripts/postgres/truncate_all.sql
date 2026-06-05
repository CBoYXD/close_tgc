DO $$
DECLARE
    stmt TEXT;
BEGIN
    SELECT INTO stmt string_agg(format('TRUNCATE TABLE %I.%I CASCADE;', schemaname, tablename), ' ')
    FROM pg_tables
    WHERE schemaname = 'public'
      AND tablename != 'alembic_version';

    IF stmt IS NOT NULL THEN
        EXECUTE stmt;
    END IF;
END $$;
