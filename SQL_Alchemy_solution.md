### III. B. La Table d'Association avec Attributs

Pour stocker des métadonnées sur la relation (ex: la probabilité d'une prédiction faite par un utilisateur sur un modèle), on utilise le motif **Association Object**.

```python
from datetime import datetime
from sqlalchemy import ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Prediction(Base):
    __tablename__ = "user_model_prediction"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("ai_model.id"), primary_key=True)
    
    # Attributs spécifiques à la liaison
    probability: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Liens vers les entités
    user: Mapped["User"] = relationship(back_populates="predictions")
    model: Mapped["AIModel"] = relationship(back_populates="user_links")

```

### Mise à jour des classes User et AIModel

Les classes parentes ne pointent plus l'une vers l'autre directement, mais vers la classe de liaison `Prediction`.

```python
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    
    predictions: Mapped[List["Prediction"]] = relationship(back_populates="user")

class AIModel(Base):
    __tablename__ = "ai_model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    
    user_links: Mapped[List["Prediction"]] = relationship(back_populates="model")

```

### Insertion de données avec attributs

Pour insérer une donnée, on instancie directement l'objet de liaison. C'est ici que l'on définit la probabilité.

```python
with Session(engine) as session:
    u1 = User(name="Expert_IA")
    m1 = AIModel(name="ResNet50")
    
    # On crée la liaison explicitement pour ajouter la probabilité
    assoc = Prediction(probability=0.98, user=u1, model=m1)
    
    session.add(assoc)
    session.commit()

```

**Note méthodologique :** Cette approche est plus rigoureuse. Elle permet de traiter la "relation" comme une entité à part entière, ce qui est indispensable pour tracer les performances des modèles par utilisateur.
