from configs.postgres_config import get_db_session

with get_db_session('corpus') as session:
    session.execute("""
    DO $$ DECLARE
      r RECORD;
    BEGIN
      FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
        EXECUTE 'DROP TABLE ' || quote_ident(r.tablename) || ' CASCADE';
      END LOOP;
    END $$;
  """)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

print('All table dropped.')

from blueprints.dataApi.models import *

for BASE in BASES.values():
    BASE.metadata.create_all()

print('All table recreated.')
