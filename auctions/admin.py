from django.contrib import admin
from .models import User, Listing, Bid, Watchlist, Comment

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "description", "price", "user", "highest_bidder", "is_active", "created", "image_url")

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name")

class BidAdmin(admin.ModelAdmin):
    list_display = ("bid_price", "listing", "user")

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "listing")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "comment", "user", "created")


admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Comment, CommentAdmin)
