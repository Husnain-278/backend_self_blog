from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from api.models import Category, Comment, Post


class Command(BaseCommand):
    help = "Seed fake categories, posts, comments, and demo users using Faker"

    def add_arguments(self, parser):
        parser.add_argument(
            "--categories",
            type=int,
            default=5,
            help="Number of categories to create",
        )
        parser.add_argument(
            "--posts",
            type=int,
            default=20,
            help="Number of posts to create",
        )
        parser.add_argument(
            "--comments",
            type=int,
            default=50,
            help="Number of comments to create",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=5,
            help="Minimum number of demo users to ensure exist",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing posts, comments, and categories before seeding",
        )

    def handle(self, *args, **options):
        fake = Faker()

        with transaction.atomic():
            if options["clear"]:
                Comment.objects.all().delete()
                Post.objects.all().delete()
                Category.objects.all().delete()

            users = list(User.objects.all())
            if len(users) < options["users"]:
                for _ in range(options["users"] - len(users)):
                    username = fake.unique.user_name()
                    User.objects.create_user(
                        username=username,
                        email=fake.unique.email(),
                        password="password123",
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                    )
                users = list(User.objects.all())

            if not users:
                self.stdout.write(self.style.WARNING("No users available to seed content"))
                return

            categories = []
            for _ in range(options["categories"]):
                title = fake.unique.sentence(nb_words=2).replace(".", "")
                categories.append(Category.objects.create(title=title))

            posts = []
            for _ in range(options["posts"]):
                post = Post.objects.create(
                    user=fake.random_element(users),
                    category=fake.random_element(categories),
                    title=fake.unique.sentence(nb_words=6).rstrip("."),
                    description="\n\n".join(fake.paragraphs(nb=fake.random_int(min=2, max=5))),
                )
                posts.append(post)

            for _ in range(options["comments"]):
                Comment.objects.create(
                    post=fake.random_element(posts),
                    user=fake.random_element(users),
                    comment=fake.sentence(nb_words=fake.random_int(min=6, max=18)),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(categories)} categories, {len(posts)} posts, and {options['comments']} comments"
            )
        )