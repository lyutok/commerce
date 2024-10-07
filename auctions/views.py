from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.core.validators import MaxLengthValidator

from .models import User, Listing, Bid, Watchlist, Comment
from django.db.models import Max

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


def custom_500_view(request, exception):
    return render(request, '500.html', status=500)


def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
    })


# create add comment form from Django forms for liting view
class CommentForm(forms.Form):
    comment = forms.CharField(
        label="Comment",
        required=False,
        validators=[MaxLengthValidator(500)],
        widget=forms.Textarea(attrs={'style': 'width: 100%;', 'placeholder': 'Enter your comment here'})
        )


# create add listing form from Django forms
class AddListing(forms.Form):
    name = forms.CharField(
        label="Name",
        required=True,
        validators=[MaxLengthValidator(64)],
        widget=forms.TextInput(attrs={'style': 'width: 100%;'})
        )

    category = forms.CharField(
        label="Category",
        required=True,
        validators=[MaxLengthValidator(64)],
        widget=forms.TextInput(attrs={'style': 'width: 100%;'})
        )

    is_active = forms.BooleanField(
        label="Is Active",
        required=True,
        initial=True
    )

    description = forms.CharField(
        label="Description",
        required=False,
        validators=[MaxLengthValidator(64)],
        widget=forms.Textarea()
        )

    price = forms.FloatField(
        label="Price",
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'style': 'width: 100px;'})
        )

    image_url = forms.URLField(
        label='Image URL',
        required=False,
        widget=forms.TextInput(attrs={'style': 'width: 100%;'})
        )

@login_required
def add(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = float(request.POST.get('price'))
        category = request.POST.get('category')
        is_active = request.POST.get('is_active') == 'on'
        user = request.user

        default_url = 'https://as2.ftcdn.net/v2/jpg/04/70/29/97/1000_F_470299797_UD0eoVMMSUbHCcNJCdv2t8B2g1GVqYgs.jpg'
        image_url=request.POST.get('image_url')
        if not image_url:  # Checks if there is no image provided
                image_url = default_url

        listing = Listing(name=name, description=description, category=category,
                          image_url=image_url, price=price, is_active=is_active, user=user)
        listing.save()

        return redirect("index")

    return render(request, "auctions/add.html", {
        "form": AddListing()
    })


def listing_view(request, id):
    # initial values for Get
    listing = Listing.objects.get(id=id)
    message = ""
    comments = Comment.objects.filter(listing=id).order_by('-created')

    if listing.is_active:
        visibility = "active" # buttons, input field visibility depending on acive/inactive listing status
    else:
        visibility = "disabled"
        if request.user == listing.highest_bidder: # checks if the currect user is a winner of deactivated listing
            message = "Auction closed. You won this auction."
        else:
            message = "Auction closed."

    # buttons logic for Post
    if request.method == "POST":
        # Bid button pressed
        if "bid" in request.POST:
            try:
                bid_price = float(request.POST.get('bid_price'))
            except ValueError:
                return redirect("listing", id)
            else:
                max_bid = (Bid.objects.filter(listing_id=id).aggregate(Max("bid_price")))['bid_price__max']

                if (max_bid is None and bid_price >= listing.price) or (max_bid is not None and bid_price > max_bid):
                    message = "Bid is placed."
                    bid = Bid(bid_price=bid_price, user=request.user, listing_id=id)
                    bid.save()
                else:
                    if max_bid is None:
                        message = f"Bid should be greater, than $ {round(listing.price, 2)}"
                    else:
                        message = f"Bid should be greater, than $ {round(max_bid, 2)}"

        # Add to watch button pressed
        elif "watchlist" in request.POST:
            watchlist_ids = [] # get all listings ids in watchlist for the current user
            for list in Watchlist.objects.filter(user=request.user).all():
                watchlist_ids.append(list.listing_id)

            if id not in (watchlist_ids):
                watchlist = Watchlist(user=request.user, listing_id=id)
                watchlist.save()
                message="Added to watchlist."
            else:
                message="Already in watchlist."

        # Close Auction button pressed, listing Inactivated
        elif "close" in request.POST:
            # find the highest bid owner and place it's username in Listind table and deactivate listing
            winner = find_winner(closed_listing_id=id)
            if winner != None:
                Listing.objects.filter(id=id).update(is_active=False, highest_bidder=winner)
                message = "Auction closed."
                visibility = "disabled"
            else:
                message = "No bids yet."

        # Add Comment button pressed
        elif "comment_button" in request.POST:
            comment = request.POST.get('comment')
            # user, listing, comment - save in batabase
            if comment != "":
                comment_db = Comment(user=request.user, listing_id=id, comment=comment)
                comment_db.save()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "message": message,
        "visibility": visibility,
        "form": CommentForm(),
        "comments": comments
    })


@login_required
def watchlist(request):
    if request.method == "POST":
        to_remove_id = request.POST.get('remove')
        listing = Watchlist.objects.get(user=request.user, listing_id=to_remove_id)
        listing.delete()

    watchlist_ids = []
    for list in Watchlist.objects.filter(user=request.user).all():
        watchlist_ids.append(list.listing_id)

    listings = Listing.objects.filter(id__in=watchlist_ids)
    return render(request, "auctions/watchlist.html", {
        "watchlist": listings
    })


def categories(request):
    categories_form_db = Listing.objects.values('category').distinct()
    categories_list = []
    for category in categories_form_db:
        categories_list.append(category['category'])

    return render(request, "auctions/categories.html", {
            "categories": categories_list
        })


def category_filtered(request, category):
    listings = Listing.objects.filter(category=category, is_active=True)

    return render(request, "auctions/category_filtered.html", {
        "category": category,
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# additional functions
def find_winner (closed_listing_id):
    max_bid = (Bid.objects.filter(listing_id=closed_listing_id).aggregate(Max("bid_price")))['bid_price__max']

    if max_bid is not None:
        bid_owner = Bid.objects.get(listing_id=closed_listing_id, bid_price=max_bid).user
    else:
        bid_owner = None

    return bid_owner

