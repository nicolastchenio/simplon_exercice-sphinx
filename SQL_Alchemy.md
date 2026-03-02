# SQL Alchemy

---

## I. Architecture et Connexion : L'Engine

SQLAlchemy repose sur un composant central appelé l'**Engine**. Il gère la communication entre votre code Python et le dialecte spécifique de la base de données (SQLite, PostgreSQL, etc.).

En 2026, l'usage de SQLite reste la norme pour le prototypage rapide en IA. On utilise une chaîne de connexion (URL) pour définir la localisation et le type de base de données.

```python
from sqlalchemy import create_engine

# Création de l'unité de contrôle
engine = create_engine("sqlite:///ia_data.db", echo=True)

```

L'argument `echo=True` est indispensable en phase d'apprentissage. Il affiche dans le terminal le SQL réel généré par l'ORM, permettant de vérifier l'efficacité des requêtes.

On distingue l'Engine (la connexion brute) de la Session (l'espace de travail). Pour manipuler les objets, on prépare une "fabrique" de sessions que l'on utilisera plus tard.

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)

```

**Note méthodologique :** L'Engine est créé une seule fois pour toute l'application. La Session, en revanche, est éphémère et doit être fermée après chaque transaction pour libérer les ressources.

---

## II. Modélisation : Schémas et Relations

Le passage de l'objet au relationnel nécessite une classe de base. On définit ensuite nos tables comme des classes héritant de `DeclarativeBase`.

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List

class Base(DeclarativeBase):
    pass

```

Prenons l'exemple d'un système de gestion de modèles d'IA. Un `Utilisateur` peut posséder plusieurs `Modeles`. C'est une relation **One-to-Many**.

### Définition des Tables

```python
class User(Base):
    __tablename__ = "user_account"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    
    # Lien vers les modèles de cet utilisateur
    models: Mapped[List["AIModel"]] = relationship(back_populates="owner")

class AIModel(Base):
    __tablename__ = "ai_model"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(default="v1.0")
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    
    # Lien retour vers l'utilisateur
    owner: Mapped["User"] = relationship(back_populates="models")

```

L'utilisation de `Mapped` et `mapped_column` permet une compatibilité parfaite avec les outils de type-checking de Python 3.11 comme Mypy ou Pyright.

### Création physique des tables

Une fois les classes définies, on demande à SQLAlchemy de générer les tables réelles dans le fichier SQLite via l'objet `Base`.

```python
# Cette commande crée toutes les tables définies ci-dessus
Base.metadata.create_all(bind=engine)

```

**Note méthodologique :** `create_all` ne met pas à jour les tables si vous modifiez une colonne plus tard. Pour cela, on utilise généralement un outil de migration comme **Alembic**.

---

### Typage des Colonnes

L'ORM SQLAlchemy utilise des types Python pour définir le format des données stockées. On utilise principalement `int`, `str`, `float`, `bool` et `datetime`.

Chaque colonne peut recevoir des contraintes : `primary_key` pour l'identifiant unique, `nullable=False` pour les champs obligatoires, ou `unique=True` pour éviter les doublons (comme un email).

En 2026, l'usage de `Mapped` permet à votre IDE de détecter immédiatement si vous tentez d'insérer une chaîne de caractères dans une colonne configurée en entier.

---

### Gestion des Clés Étrangères

Une clé étrangère (**ForeignKey**) est une colonne qui contient l'identifiant d'une ligne située dans une autre table. Elle sert de "pont" logique entre deux entités.

Le rôle de la clé étrangère est de garantir l'intégrité référentielle : on ne peut pas créer un modèle lié à un utilisateur qui n'existe pas dans la table parente.

---

### Les 4 Types de Relations

* **One-to-Many (1 à N) :** C'est le cas le plus fréquent. Un utilisateur possède plusieurs modèles d'IA. La clé étrangère est placée du côté "Many" (dans la table du modèle).
* **Many-to-One (N à 1) :** C'est simplement la vue inverse du One-to-Many. Plusieurs modèles pointent vers le même utilisateur unique.
* **One-to-One (1 à 1) :** Un utilisateur possède un seul profil de configuration. On place une clé étrangère d'un côté et on configure l'ORM pour qu'il ne renvoie qu'un objet unique, pas une liste.
* **Many-to-Many (N à N) :** Plusieurs modèles utilisent plusieurs jeux de données (Datasets). Cela nécessite une **table d'association** intermédiaire qui stocke uniquement les couples d'identifiants.

**Note méthodologique :** La relation dans l'ORM (`relationship`) est une abstraction Python pour naviguer entre les objets. Elle est distincte de la `ForeignKey` qui est la contrainte réelle en base de données.

---

### 1. Relation One-to-One (1 à 1)

Cas d'usage : Un `Utilisateur` a un seul `Profil` de configuration.

```python
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    # L'objet unique côté Profil
    profile: Mapped["Profile"] = relationship(back_populates="user")

class Profile(Base):
    __tablename__ = "user_profile"
    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    # L'objet unique côté User
    user: Mapped["User"] = relationship(back_populates="profile")

```

---

### 2. Relation One-to-Many (1 à N)

Cas d'usage : Un `Utilisateur` possède plusieurs `Modeles` d'IA.

```python
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    # Une liste d'objets Modeles
    models: Mapped[List["AIModel"]] = relationship(back_populates="owner")

class AIModel(Base):
    __tablename__ = "ai_model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    # Référence vers l'unique propriétaire
    owner: Mapped["User"] = relationship(back_populates="models")

```

---

### 3. Relation Many-to-Many (N à N)

Cas d'usage : Un `Modele` utilise plusieurs `Dataset`, et un `Dataset` peut servir à plusieurs `Modeles`. On utilise une table d'association "muette".

```python
from sqlalchemy import Table, Column

# Table technique de liaison
model_dataset_assoc = Table(
    "model_dataset",
    Base.metadata,
    Column("model_id", ForeignKey("ai_model.id"), primary_key=True),
    Column("dataset_id", ForeignKey("dataset.id"), primary_key=True),
)

class AIModel(Base):
    __tablename__ = "ai_model"
    id: Mapped[int] = mapped_column(primary_key=True)
    # Relation via la table secondaire
    datasets: Mapped[List["Dataset"]] = relationship(secondary=model_dataset_assoc)

class Dataset(Base):
    __tablename__ = "dataset"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

```

**Note méthodologique :** Dans le cas N à N, la table d'association n'est pas une classe Python (sauf si vous avez besoin d'y ajouter des colonnes de données spécifiques). Elle sert uniquement de pivot pour SQL.

---

## III. Opérations CRUD et Jointures

Le **CRUD** (Create, Read, Update, Delete) est le socle de toute interaction avec une base de données. Toutes ces opérations s'effectuent via un objet `Session`.

On utilise un **Context Manager** (`with`) pour garantir que la session est bien fermée, même en cas d'erreur dans votre script d'entraînement ou d'inférence.

### 1. Create (Insertion)

Pour ajouter des données, on instancie nos classes Python comme des objets classiques, puis on les "ajoute" à la session avant de valider (**commit**).

```python
with SessionLocal() as session:
    new_user = User(name="Alice")
    new_model = AIModel(name="GPT-X", owner=new_user) # Liaison automatique
    
    session.add(new_user)
    session.commit() # Les données sont envoyées en base ici

```

### 2. Read (Lecture et Jointures)

La lecture utilise la fonction `select()`. Pour récupérer des données liées (jointures), SQLAlchemy propose deux approches majeures.

**Approche explicite (Join) :** On demande explicitement de joindre les tables pour filtrer sur des attributs du parent.

```python
from sqlalchemy import select

with SessionLocal() as session:
    stmt = select(AIModel).join(AIModel.owner).where(User.name == "Alice")
    models = session.scalars(stmt).all()

```

**Approche implicite (Eager Loading) :** Pour éviter le problème de performance "N+1 queries", on force le chargement des relations dès la première requête avec `selectinload`.

```python
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.models))
users = session.scalars(stmt).all()
# Les modèles sont déjà chargés en mémoire, pas de nouvelle requête SQL.

```

### 3. Update (Mise à jour)

Pour modifier une donnée, il suffit de récupérer l'objet, de modifier son attribut Python, et de valider la session.

```python
with SessionLocal() as session:
    model = session.get(AIModel, 1) # Récupère le modèle avec l'ID 1
    model.name = "GPT-X-Turbo"
    session.commit()

```

### 4. Delete (Suppression)

La suppression suit la même logique : on cible l'objet, puis on utilise la méthode `delete`.

```python
with SessionLocal() as session:
    model_to_del = session.get(AIModel, 1)
    session.delete(model_to_del)
    session.commit()

```

**Note méthodologique :** Attention à la "suppression en cascade". Si vous supprimez un utilisateur, vous devez décider si ses modèles doivent être supprimés (cascade) ou si leur champ `user_id` doit devenir nul.

---

## Exercice : Enregistrement des performances de prédiction

### Contexte

On souhaite suivre les performances de différents utilisateurs sur plusieurs modèles d'IA. Pour chaque association entre un utilisateur et un modèle, on doit stocker la probabilité de succès obtenue lors du dernier test ainsi que la date de l'essai.

### Objectif

Mettre en place une table d'association complexe (Association Object) et réaliser une insertion de données incluant des métadonnées sur la relation.

### Énoncé

1. **Définition du Schéma** :
Créez trois classes : `User`, `AIModel` et `Prediction`. La classe `Prediction` servira de pivot et devra contenir :
* Une clé étrangère vers `User`.
* Une clé étrangère vers `AIModel`.
* Un champ `probability` de type Float.
* Un champ `timestamp` de type DateTime (avec une valeur par défaut au moment de l'insertion).


2. **Relations** :
Configurez les `relationship` dans les trois classes pour permettre une navigation bidirectionnelle.
3. **Manipulation de données** :
* Instanciez un utilisateur nommé "DataScientist_01".
* Instanciez un modèle nommé "EfficientNet_V3".
* Créez une liaison entre cet utilisateur et ce modèle en fixant une probabilité de `0.85`.
* Enregistrez le tout en base de données.


4. **Requête de vérification** :
Affichez le nom de l'utilisateur, le nom du modèle et la probabilité associée en effectuant une seule requête sur la table `Prediction`.


