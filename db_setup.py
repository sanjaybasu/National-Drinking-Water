
def setup(engine):
    engine.execute("""
        CREATE TABLE IF NOT EXISTS suppliers(
            id serial primary key,
            zipcode int,
            supplier_name text,
            locations_served text,
            number_of_people_served int,
            href text unique
        );
    """)

    engine.execute("""
        CREATE TABLE IF NOT EXISTS violation_summary(
            id int,
            violation text,
            date_of_violation text
        )
    """)

    engine.execute("""
        CREATE TABLE IF NOT EXISTS contaminants(
            id int,
            contaminant text,
            average_result text,
            max_result text,
            health_limit_exceeded text,
            legal_limit_exceeded text
        )
    """)
