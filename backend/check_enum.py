from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT unnest(enum_range(NULL::userrole));")
    )

    for row in result:
        print(row[0])