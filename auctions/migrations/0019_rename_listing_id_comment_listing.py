# Generated by Django 5.0.6 on 2024-05-28 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0018_rename_listing_comment_listing_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="listing_id",
            new_name="listing",
        ),
    ]
