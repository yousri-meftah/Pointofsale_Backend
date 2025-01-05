ALTER USER postgres WITH PASSWORD 'yousri';
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pointofsale_db') THEN
        CREATE DATABASE pointofsale_db OWNER postgres;
    END IF;
END
$$;
