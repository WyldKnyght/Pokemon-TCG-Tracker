from pokemontcgsdk import Card
from db import SessionLocal
from models import CardModel
import time


def sync_cards(page_size=250, max_pages=None):
    """
    Fetch all English cards from API and sync to database

    Args:
        page_size: Number of cards per page (max 250)
        max_pages: Maximum number of pages to fetch (None = all)
    """
    session = SessionLocal()

    try:
        page = 1
        total_synced = 0

        while not (max_pages and page > max_pages):
            print(f"Fetching page {page} (size={page_size})...")

            # Query for English cards only
            cards = Card.where(q="language:en", page=page, pageSize=page_size)

            if not cards:
                print("No more cards to fetch.")
                break

            for api_card in cards:
                # Check if card exists
                card_model = session.query(CardModel).filter_by(id=api_card.id).first()

                if not card_model:
                    card_model = CardModel()
                    session.add(card_model)

                # Map API fields to model
                card_model.id = api_card.id
                card_model.name = api_card.name
                card_model.set_id = api_card.set.id
                card_model.number = getattr(api_card, "number", None)
                card_model.rarity = getattr(api_card, "rarity", None)
                card_model.supertype = getattr(api_card, "supertype", None)

                # Handle types array
                types = getattr(api_card, "types", [])
                card_model.types = ",".join(types) if types else None

                # Handle HP (convert to int if present)
                hp = getattr(api_card, "hp", None)
                card_model.hp = int(hp) if hp and hp.isdigit() or None else None

                card_model.regulation_mark = getattr(api_card, "regulationMark", None)

                # Handle illustrators
                illustrators = getattr(api_card, "artist", None)
                card_model.illustrators = illustrators or None

                total_synced += 1

            session.commit()
            print(f"Page {page} complete. Total cards synced: {total_synced}")

            # Check if we got fewer cards than page_size (last page)
            if len(cards) < page_size:
                print("Reached last page.")
                break

            page += 1

            # Brief pause to respect rate limits (30 requests per minute without key)
            time.sleep(0.5)

        print(f"\\nSync complete! Total cards synced: {total_synced}")

    except Exception as e:
        session.rollback()
        print(f"Error syncing cards: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    # Sync all cards (this may take several minutes)
    sync_cards(page_size=250)
