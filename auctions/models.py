from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(blank=True, max_length=64)
    category = models.CharField(max_length=64)
    price = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    is_active = models.BooleanField(default=True)
    highest_bidder = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(default='https://as2.ftcdn.net/v2/jpg/04/70/29/97/1000_F_470299797_UD0eoVMMSUbHCcNJCdv2t8B2g1GVqYgs.jpg')

    def __str__(self):
        return f"{self.user}: {self.name} {self.description} {self.price}."


class Bid(models.Model):
    bid_price = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_owner")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_id")

    def __str__(self):
        return f"{self.user} bided {self.bid_price} to listing id {self.id}."


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watched_id")

    def __str__(self):
        return f"{self.user} watches {self.listing}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_owner", blank=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment_listing_id")
    comment = models.TextField(blank=True, max_length=500)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comment} - {self.listing}, {self.user}, {self.created}"
