from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add", views.add, name="add"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category_filtered, name="categories_filtered"),
    path("listing/<int:id>", views.listing_view, name="listing"),
]
