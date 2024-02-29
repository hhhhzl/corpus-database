from configs.mysql_config import get_db_session_sql

# with get_db_session_sql('corpus') as session:
#     session.execute("""
#     SELECT CONCAT('DROP TABLE ', TABLE_NAME, ';')
#     FROM INFORMATION_SCHEMA.tables
#     WHERE TABLE_SCHEMA = 'Corpus_STA_DB';
#   """)
#     try:
#         session.commit()
#         print('All table dropped.')
#     except Exception as e:
#         session.rollback()
#         raise e

from blueprints.dataApi.models import *

for BASE in BASES.values():
    BASE.metadata.create_all()

print('All table recreated.')
