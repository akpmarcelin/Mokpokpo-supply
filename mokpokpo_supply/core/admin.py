# core/admin.py
from django.contrib import admin
from .models import (
    Role, Utilisateur, Produit, HistoriquePrix,
    Entrepot, Emplacement, Lot, MouvementStock,
    Livraison, LigneLivraison, PrevisionDemande
)

# --------------------
# ROLE
# --------------------
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')

# --------------------
# UTILISATEUR
# --------------------
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'prenoms', 'email', 'role', 'actif')
    list_filter = ('role', 'actif')
    search_fields = ('username', 'prenoms', 'email')

# --------------------
# PRODUIT
# --------------------
@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_produit', 'unite', 'prix_reference')
    list_filter = ('type_produit',)
    search_fields = ('nom',)

@admin.register(HistoriquePrix)
class HistoriquePrixAdmin(admin.ModelAdmin):
    list_display = ('produit', 'prix', 'date')
    list_filter = ('produit',)

# --------------------
# ENTREPOT / EMPLACEMENT
# --------------------
@admin.register(Entrepot)
class EntrepotAdmin(admin.ModelAdmin):
    list_display = ('nom', 'localisation')

@admin.register(Emplacement)
class EmplacementAdmin(admin.ModelAdmin):
    list_display = ('entrepot', 'code_emplacement')
    list_filter = ('entrepot',)

# --------------------
# LOT
# --------------------
@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('code_lot', 'produit', 'quantite_initiale', 'quantite_restante', 'date_production', 'emplacement')
    list_filter = ('produit',)
    search_fields = ('code_lot',)

# --------------------
# MOUVEMENT STOCK
# --------------------
@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('lot', 'type_mouvement', 'quantite', 'source_emplacement', 'destination_emplacement', 'utilisateur', 'date')
    list_filter = ('type_mouvement',)
    search_fields = ('lot__code_lot',)

# --------------------
# LIVRAISON
# --------------------
@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'grossiste',
        'statut',
        'date_livraison',
        'date_creation',
    )
    list_filter = ('statut',)
    search_fields = ('numero',)

@admin.register(LigneLivraison)
class LigneLivraisonAdmin(admin.ModelAdmin):
    list_display = ('livraison', 'lot', 'quantite')

# --------------------
# PREVISION DEMANDE
# --------------------
@admin.register(PrevisionDemande)
class PrevisionDemandeAdmin(admin.ModelAdmin):
    list_display = ('produit', 'periode', 'quantite_prevue', 'date_calcul')

