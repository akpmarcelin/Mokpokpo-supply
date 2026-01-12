# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import Utilisateur, Role, Lot, Emplacement, MouvementStock, Produit, Livraison, LigneLivraison
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import UtilisateurCreationForm
from .models import Role
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import *
from .forms import *
from django.contrib.auth import login, logout


def index(request):
    return render(request, 'index.html')
    
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        
        # Redirection selon rôle
        role = user.role.nom if user.role else ''
        if role == 'GROSSISTE':
            return redirect('dashboard_grossiste')
        elif role == 'STOCK':
            return redirect('dashboard_stock')
        elif role == 'GERANT':
            return redirect('dashboard_gerant')
        elif role == 'LIVREUR':
            return redirect('dashboard_livreur')  # à créer plus tard
        else:
            return redirect('index')  # fallback

    return render(request, 'login.html', {'form': form})

def register_grossiste(request):
    if request.method == 'POST':
        # Ne pas déconnecter l'utilisateur ici, cela pourrait causer des problèmes
        form = UtilisateurCreationForm(request.POST)
        if form.is_valid():
            try:
                # Récupérer ou créer le rôle GROSSISTE
                role, created = Role.objects.get_or_create(nom='GROSSISTE')
                
                # Créer l'utilisateur avec commit=False pour pouvoir ajouter des champs supplémentaires
                user = form.save(commit=False)
                user.role = role
                user.is_active = True
                
                # S'assurer que le nom d'utilisateur est en minuscules
                user.username = user.username.lower()
                
                # Sauvegarder l'utilisateur
                user.save()
                
                # Connecter l'utilisateur
                login(request, user)
                
                # Rediriger vers le tableau de bord
                return redirect('dashboard_grossiste')
                
            except Exception as e:
                # En cas d'erreur, ajouter un message d'erreur
                messages.error(request, f"Une erreur est survenue lors de l'inscription : {str(e)}")
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}" if field in form.fields else error)
    else:
        form = UtilisateurCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def stock_manager_dashboard(request):
    lots = Lot.objects.all().order_by('-date_production')
    mouvements = MouvementStock.objects.all().order_by('-date')
    emplacements = Emplacement.objects.all()
    produits = Produit.objects.all()
    livraisons = Livraison.objects.filter(statut='PREPARATION').order_by('date_livraison')
    livreurs = Utilisateur.objects.filter(role__nom='LIVREUR', actif=True)
    return render(request, 'dashboard_stock.html', {
        'lots': lots,
        'mouvements': mouvements,
        'emplacements': emplacements,
        'produits': produits,
        'livraisons': livraisons,
        'livreurs': livreurs,
    })

@login_required
def add_lot(request):
    if request.method == 'POST':
        produit = Produit.objects.get(id=request.POST.get('produit'))
        emplacement = Emplacement.objects.get(id=request.POST.get('emplacement'))
        quantite = float(request.POST.get('quantite'))
        date_prod = request.POST.get('date_production')
        Lot.objects.create(
            code_lot=f"{produit.nom[:3].upper()}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            produit=produit,
            quantite_initiale=quantite,
            quantite_restante=quantite,
            date_production=date_prod,
            emplacement=emplacement
        )
    return redirect('dashboard_stock')

@login_required
def move_lot(request):
    if request.method == 'POST':
        lot = Lot.objects.get(id=request.POST.get('lot'))
        destination = Emplacement.objects.get(id=request.POST.get('destination'))

        MouvementStock.objects.create(
            lot=lot,
            type_mouvement='TRANSFERT',
            quantite=lot.quantite_restante,
            source_emplacement=lot.emplacement,
            destination_emplacement=destination,
            utilisateur=request.user,
            date=timezone.now()
        )
        lot.emplacement = destination
        lot.save()
    return redirect('dashboard_stock')

# Vue pour affecter un lot et un livreur à une ligne de livraison
@login_required
def assign_lot_and_livreur(request, livraison_id, ligne_id):
    if request.method == 'POST':
        try:
            # Récupération des objets
            ligne = LigneLivraison.objects.get(id=ligne_id)
            livraison = Livraison.objects.get(id=livraison_id)
            
            # Validation des données du formulaire
            lot_id = request.POST.get('lot')
            quantite_str = request.POST.get('quantite')
            livreur_id = request.POST.get('livreur')
            
            if not all([lot_id, quantite_str, livreur_id]):
                messages.error(request, "Tous les champs sont obligatoires")
                return redirect('dashboard_stock')
            
            try:
                quantite = float(quantite_str)
                if quantite <= 0:
                    raise ValueError("La quantité doit être positive")
            except (TypeError, ValueError):
                messages.error(request, "Quantité invalide")
                return redirect('dashboard_stock')
            
            # Vérification du lot
            try:
                lot = Lot.objects.get(id=lot_id, produit=ligne.produit)
                if lot.quantite_restante < quantite:
                    messages.error(request, f"Quantité insuffisante en stock. Il reste {lot.quantite_restante} kg")
                    return redirect('dashboard_stock')
            except Lot.DoesNotExist:
                messages.error(request, "Lot invalide ou ne correspond pas au produit")
                return redirect('dashboard_stock')
            
            # Vérification du livreur
            try:
                livreur = Utilisateur.objects.get(id=livreur_id, role__nom='LIVREUR')
            except Utilisateur.DoesNotExist:
                messages.error(request, "Livreur invalide")
                return redirect('dashboard_stock')
            
            # Mise à jour de la ligne de livraison
            ligne.lot = lot
            ligne.quantite = quantite
            ligne.save()
            
            # Mise à jour du stock
            lot.quantite_restante -= quantite
            lot.save()
            
            # Création du mouvement de stock
            MouvementStock.objects.create(
                lot=lot,
                type_mouvement='SORTIE',
                quantite=quantite,
                source_emplacement=lot.emplacement,
                destination_emplacement=None,
                utilisateur=request.user,
                date=timezone.now()
            )
            
            # Mise à jour de la livraison
            livraison.livreur = livreur
            
            # Vérifier si toutes les lignes sont affectées
            if all(l.lot for l in livraison.lignelivraison_set.all()):
                livraison.statut = 'EN_ROUTE'
            livraison.save()
            
            messages.success(request, "Lot et livreur affectés avec succès")
            
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {str(e)}")
    
    return redirect('dashboard_stock')

@login_required
def dashboard_livreur(request):
    if not request.user.role or request.user.role.nom != "LIVREUR":
        return redirect('index')
    # Récupérer les livraisons avec les informations du grossiste
    livraisons = Livraison.objects.filter(livreur=request.user).select_related('grossiste').order_by('-date_livraison')
    return render(request, 'dashboard_livreur.html', {'livraisons': livraisons})

@login_required
def livreur_marquer_livree(request, livraison_id):
    if request.method == 'POST':
        livraison = Livraison.objects.get(id=livraison_id, livreur=request.user)
        livraison.statut = 'LIVREE'
        livraison.save()
    return redirect('dashboard_livreur')

@login_required
def grossiste_dashboard(request):
    if not request.user.role or request.user.role.nom != "GROSSISTE":
        return redirect('index')

    produits = Produit.objects.all()
    livraisons = Livraison.objects.filter(grossiste=request.user)

    return render(request, 'dashboard_grossiste.html', {
        'produits': produits,
        'livraisons': livraisons,
    })

@login_required
def pass_order(request):
    if not request.user.role or request.user.role.nom != "GROSSISTE":
        return redirect('index')

    if request.method == 'POST':
        produit_id = request.POST.get('produit')
        quantite = float(request.POST.get('quantite'))
        date_livraison = request.POST.get('date_livraison')
        notes = request.POST.get('notes', '')

        produit = Produit.objects.get(id=produit_id)

        # ✅ DÉFINITION DU NUMÉRO
        numero = f"LIV-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        livraison = Livraison.objects.create(
            numero=numero,
            grossiste=request.user,
            statut='PREPARATION',
            date_livraison=date_livraison
        )

        LigneLivraison.objects.create(
            livraison=livraison,
            produit=produit,
            quantite=quantite
        )

        return redirect('dashboard_grossiste')

    return redirect('dashboard_grossiste')
    
@login_required
def dashboard_gerant(request):
    if not request.user.role or request.user.role.nom != "GERANT":
        return redirect('index')

    # Tous les mouvements de stock
    mouvements = MouvementStock.objects.all().order_by('-date')

    # Tous les employés (STOCK et LIVREUR)
    employes = Utilisateur.objects.filter(role__nom__in=['STOCK', 'LIVREUR']).order_by('role', 'nom')

    return render(request, 'dashboard_gerant.html', {
        'mouvements': mouvements,
        'employes': employes
    })

from core.ia.model import StockPredictor

@login_required
def gerant_predictions(request):
    if not request.user.role or request.user.role.nom != "GERANT":
        return redirect('index')

    predictor = StockPredictor()
    predictions = predictor.predict_from_db()  # récupère directement depuis la base

    return render(request, 'gerant_predictions.html', {'predictions': predictions})

    

