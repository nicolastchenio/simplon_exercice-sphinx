"""
Contexte
--------
On souhaite suivre les performances de différents utilisateurs sur plusieurs modèles d'IA.
Pour chaque association entre un utilisateur et un modèle, on doit stocker :
- la probabilité de succès obtenue lors du dernier test
- la date de l'essai.

Objectif
--------
Mettre en place une table d'association complexe (Association Object)
et réaliser une insertion de données incluant des métadonnées sur la relation.

Énoncé
------
1) Définition du schéma
Créer trois classes : User, AIModel et Prediction.

La classe Prediction sert de table pivot et contient :
- une clé étrangère vers User
- une clé étrangère vers AIModel
- un champ probability de type Float
- un champ timestamp de type DateTime avec une valeur par défaut lors de l'insertion

2) Relations
Configurer les relationships dans les trois classes pour permettre
une navigation bidirectionnelle.

3) Manipulation de données
Créer :
- un utilisateur nommé "DataScientist_01"
- un modèle nommé "EfficientNet_V3"
- une relation entre les deux avec une probabilité de 0.85

4) Vérification
Afficher le nom de l'utilisateur, le modèle utilisé et la probabilité
associée via une requête sur la table Prediction.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, select
from typing import List
from datetime import datetime


"""
Création du moteur de base de données.

Le moteur permet à SQLAlchemy de communiquer avec la base SQLite
et d'afficher les requêtes SQL générées grâce au paramètre echo=True.
"""
engine = create_engine("sqlite:///ia_data.db", echo=True)


"""
Création du gestionnaire de session.

SessionLocal servira à ouvrir des sessions de communication
avec la base de données afin d'exécuter des transactions.
"""
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """
    Classe de base utilisée par SQLAlchemy pour la déclaration
    des modèles ORM. Toutes les tables héritent de cette classe.
    """
    pass


class Prediction(Base):
    """
    Table d'association entre User et AIModel.

    Cette table stocke également des métadonnées sur la relation :
    - la probabilité prédite
    - la date du test effectué.
    """

    __tablename__ = "prediction"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id"),
        primary_key=True
    )

    model_id: Mapped[int] = mapped_column(
        ForeignKey("ai_model.id"),
        primary_key=True
    )

    """
    Probabilité de succès calculée par le modèle pour l'utilisateur.
    """
    probability: Mapped[float] = mapped_column(nullable=False)

    """
    Date et heure de la prédiction.
    La valeur par défaut correspond au moment de l'insertion.
    """
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    """
    Relation vers l'utilisateur associé à la prédiction.
    """
    user: Mapped["User"] = relationship(back_populates="predictions")

    """
    Relation vers le modèle d'IA utilisé pour la prédiction.
    """
    model: Mapped["AIModel"] = relationship(back_populates="predictions")


class User(Base):
    """
    Représente un utilisateur réalisant des tests sur des modèles d'IA.
    """

    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    """
    Liste des prédictions associées à cet utilisateur.
    """
    predictions: Mapped[List["Prediction"]] = relationship(
        back_populates="user"
    )


class AIModel(Base):
    """
    Représente un modèle d'intelligence artificielle utilisé
    pour effectuer des prédictions.
    """

    __tablename__ = "ai_model"

    id: Mapped[int] = mapped_column(primary_key=True)

    """
    Version ou nom du modèle d'IA.
    """
    version: Mapped[str] = mapped_column(default="v1.0")

    """
    Liste des prédictions réalisées avec ce modèle.
    """
    predictions: Mapped[List["Prediction"]] = relationship(
        back_populates="model"
    )


"""
Création physique des tables dans la base SQLite.

SQLAlchemy utilise les métadonnées de la classe Base
pour générer automatiquement les tables si elles n'existent pas.
"""
Base.metadata.create_all(bind=engine)


"""
Manipulation de données.

Création :
- d'un utilisateur
- d'un modèle
- d'une prédiction reliant les deux entités.
"""
with SessionLocal() as session:

    new_user = User(name="DataScientist_01")
    session.add(new_user)

    new_model = AIModel(version="EfficientNet_V3")
    session.add(new_model)

    prediction = Prediction(
        probability=0.85,
        user=new_user,
        model=new_model
    )
    session.add(prediction)

    session.commit()


"""
Requête de vérification.

Une requête est effectuée sur la table Prediction afin
de récupérer les informations liées à l'utilisateur,
au modèle et à la probabilité associée.
"""
with SessionLocal() as session:

    stmt = (
        select(Prediction)
        .join(Prediction.user)
        .join(Prediction.model)
    )

    result = session.execute(stmt).scalars().first()

    print(f"User: {result.user.name}")
    print(f"Model: {result.model.version}")
    print(f"Probability: {result.probability}")


print("----- Fin du programme nicolas tchenio ---------")