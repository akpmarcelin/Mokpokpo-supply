# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('dashboard/livreur/', views.dashboard_livreur, name='dashboard_livreur'),
    path('dashboard/livreur/livree/<int:livraison_id>/', views.livreur_marquer_livree, name='livreur_marquer_livree'),
    
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_grossiste, name='register'),

    # Dashboard gestionnaire
    path('dashboard/stock/', views.stock_manager_dashboard, name='dashboard_stock'),
    path('dashboard/stock/add_lot/', views.add_lot, name='add_lot'),
    path('dashboard/stock/move_lot/', views.move_lot, name='move_lot'),
    path('dashboard/stock/assign_lot/<int:livraison_id>/<int:ligne_id>/', views.assign_lot_and_livreur, name='assign_lot_to_livraison'),
    
    # Dashboard grossiste
    path('dashboard/grossiste/', views.grossiste_dashboard, name='dashboard_grossiste'),
    path('dashboard/grossiste/commander/', views.pass_order, name='pass_order'),
    
    # Dashboard gerant
    path('dashboard/gerant/', views.dashboard_gerant, name='dashboard_gerant'),
    path('dashboard/gerant/predictions/', views.gerant_predictions, name='gerant_predictions'),  # futur IA

    
]

