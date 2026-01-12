from .models import Lot, LigneLivraison, Produit
import pandas as pd
import numpy as np
# Si ton modèle est scikit-learn
import joblib

def calculer_predictions():
    # --- Préparer les données ---
    # Exemple : quantités commandées par produit
    lignes = LigneLivraison.objects.all()
    data = []
    for l in lignes:
        data.append({
            'produit': l.produit.nom,
            'quantite': l.quantite,
            'date': l.livraison.date_livraison
        })
    df = pd.DataFrame(data)

    # Quantité totale commandée par produit
    commandes_par_produit = df.groupby('produit')['quantite'].sum()

    # Lots à faible stock
    lots = Lot.objects.all()
    lots_df = pd.DataFrame([{
        'code_lot': lot.code_lot,
        'produit': lot.produit.nom,
        'quantite_restante': lot.quantite_restante
    } for lot in lots])
    lot_faible_stock = lots_df.sort_values('quantite_restante').iloc[0]['code_lot'] if not lots_df.empty else None

    # Produit le plus populaire
    produit_populaire = commandes_par_produit.idxmax() if not commandes_par_produit.empty else None

    # --- Exemple de prédiction avec un modèle ML existant ---
    # model = joblib.load('path_to_model.pkl')
    # X = préparer_features(df, lots_df)
    # y_pred = model.predict(X)
    # pour l’instant, on peut juste sommer les quantités prédites
    quantite_prevue = int(commandes_par_produit.sum() * 1.1)  # simple exemple: +10% pour prévision

    return {
        'produit_populaire': produit_populaire,
        'lot_faible_stock': lot_faible_stock,
        'quantite_prevue_prochaine_semaine': quantite_prevue
    }

