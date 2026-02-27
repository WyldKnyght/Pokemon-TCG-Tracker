from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SetModel(Base):
    __tablename__ = 'sets'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    series = Column(String)
    printed_total = Column(Integer)
    release_date = Column(String)

    # Relationship
    cards = relationship('CardModel', back_populates='set_model')

    def __repr__(self):
        return f"<Set {self.name} ({self.id})>"


class CardModel(Base):
    __tablename__ = 'cards'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    set_id = Column(String, ForeignKey('sets.id'), nullable=False)
    number = Column(String)
    rarity = Column(String)
    supertype = Column(String)
    types = Column(String)  # JSON array stored as string
    hp = Column(Integer)
    regulation_mark = Column(String)
    illustrators = Column(Text)  # Comma-separated

    # Relationships
    set_model = relationship('SetModel', back_populates='cards')
    collection_entries = relationship('CollectionEntry', back_populates='card')

    def __repr__(self):
        return f"<Card {self.name} ({self.id})>"


class CollectionEntry(Base):
    __tablename__ = 'collection_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, ForeignKey('cards.id'), nullable=False)
    language = Column(String, default='EN')
    quantity = Column(Integer, default=1)
    condition = Column(String, default='NM')  # NM, LP, MP, HP, DMG
    location = Column(String)  # e.g., "Binder 1", "Box A"
    graded = Column(Integer, default=0)  # 0=False, 1=True
    grade_company = Column(String)  # e.g., "PSA", "BGS", "CGC"
    grade_value = Column(Float)  # e.g., 9.5

    # Relationship
    card = relationship('CardModel', back_populates='collection_entries')

    def __repr__(self):
        return f"<CollectionEntry {self.card_id} x{self.quantity} {self.condition}>"