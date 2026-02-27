from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from db import SessionLocal, init_db
from models import SetModel, CardModel, CollectionEntry

app = Flask(__name__)

# Initialize database on startup
with app.app_context():
    init_db()


def get_db():
    """Get database session for Flask routes"""
    return SessionLocal()


@app.route("/")
def dashboard():
    """Dashboard with summary statistics"""
    db = get_db()
    try:
        set_count = db.query(func.count(SetModel.id)).scalar()
        card_count = db.query(func.count(CardModel.id)).scalar()
        collection_count = db.query(func.sum(CollectionEntry.quantity)).scalar() or 0
        unique_collected = db.query(func.count(CollectionEntry.id.distinct())).scalar()

        stats = {
            "sets": set_count,
            "cards": card_count,
            "collection_total": collection_count,
            "unique_collected": unique_collected,
        }
        return render_template("dashboard.html", stats=stats)
    finally:
        db.close()


@app.route("/sets")
def sets():
    """List all sets"""
    db = get_db()
    try:
        all_sets = db.query(SetModel).order_by(SetModel.release_date.desc()).all()
        return render_template("sets.html", sets=all_sets)
    finally:
        db.close()


@app.route("/cards")
def cards():
    """List all cards with filtering and sorting"""
    db = get_db()
    try:
        # Get filter parameters
        set_id = request.args.get("set_id")
        rarity = request.args.get("rarity")
        name = request.args.get("name")
        supertype = request.args.get("supertype")
        card_type = request.args.get("type")
        sort_by = request.args.get("sort", "set_id")

        # Build query
        query = db.query(CardModel)

        # Apply filters
        if set_id:
            query = query.filter(CardModel.set_id == set_id)
        if rarity:
            query = query.filter(CardModel.rarity == rarity)
        if name:
            query = query.filter(CardModel.name.ilike(f"%{name}%"))
        if supertype:
            query = query.filter(CardModel.supertype == supertype)
        if card_type:
            query = query.filter(CardModel.types.like(f"%{card_type}%"))

        # Apply sorting
        if sort_by == "name":
            query = query.order_by(CardModel.name)
        else:  # default: set_id or number
            query = query.order_by(CardModel.set_id, CardModel.number)

        cards_list = query.all()

        # Get unique values for filter dropdowns
        sets_list = db.query(SetModel).order_by(SetModel.name).all()
        rarities = (
            db.query(CardModel.rarity)
            .distinct()
            .filter(CardModel.rarity.isnot(None))
            .all()
        )
        supertypes = (
            db.query(CardModel.supertype)
            .distinct()
            .filter(CardModel.supertype.isnot(None))
            .all()
        )

        return render_template(
            "cards.html",
            cards=cards_list,
            sets=sets_list,
            rarities=[r[0] for r in rarities],
            supertypes=[s[0] for s in supertypes],
            filters={
                "set_id": set_id,
                "rarity": rarity,
                "name": name,
                "supertype": supertype,
                "type": card_type,
                "sort": sort_by,
            },
        )
    finally:
        db.close()


@app.route("/card/<card_id>")
def card_detail(card_id):
    """Show detailed card information"""
    db = get_db()
    try:
        card = db.query(CardModel).filter_by(id=card_id).first()
        if not card:
            return "Card not found", 404

        # Get collection entries for this card
        entries = db.query(CollectionEntry).filter_by(card_id=card_id).all()

        return render_template("card_detail.html", card=card, entries=entries)
    finally:
        db.close()


@app.route("/collection")
def collection():
    """List all collection entries with filtering"""
    db = get_db()
    try:
        # Get filter parameters
        set_id = request.args.get("set_id")
        rarity = request.args.get("rarity")
        language = request.args.get("language")
        condition = request.args.get("condition")

        # Build query
        query = db.query(CollectionEntry).join(CardModel)

        # Apply filters
        if set_id:
            query = query.filter(CardModel.set_id == set_id)
        if rarity:
            query = query.filter(CardModel.rarity == rarity)
        if language:
            query = query.filter(CollectionEntry.language == language)
        if condition:
            query = query.filter(CollectionEntry.condition == condition)

        entries = query.all()

        # Get unique values for filters
        sets_list = db.query(SetModel).order_by(SetModel.name).all()
        languages = db.query(CollectionEntry.language).distinct().all()
        conditions = ["NM", "LP", "MP", "HP", "DMG"]

        return render_template(
            "collection.html",
            entries=entries,
            sets=sets_list,
            languages=[l[0] for l in languages],
            conditions=conditions,
            filters={
                "set_id": set_id,
                "rarity": rarity,
                "language": language,
                "condition": condition,
            },
        )
    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
