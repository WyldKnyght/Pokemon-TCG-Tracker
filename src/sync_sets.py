from pokemontcgsdk import Set
from db import SessionLocal
from models import SetModel

def sync_sets():
    """Fetch all sets from API and sync to database"""
    session = SessionLocal()

    try:
        print("Fetching sets from PokémonTCG API...")
        sets = Set.all()

        count = 0
        for api_set in sets:
            # Map API fields to model
            set_model = session.query(SetModel).filter_by(id=api_set.id).first()

            if not set_model:
                set_model = SetModel()
                session.add(set_model)

            set_model.id = api_set.id
            set_model.name = api_set.name
            set_model.series = getattr(api_set, 'series', None)
            set_model.printed_total = getattr(api_set, 'printedTotal', None)
            set_model.release_date = getattr(api_set, 'releaseDate', None)

            count += 1

        session.commit()
        print(f"Successfully synced {count} sets!")

    except Exception as e:
        session.rollback()
        print(f"Error syncing sets: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    sync_sets()