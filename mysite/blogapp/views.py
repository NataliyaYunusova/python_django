from django.contrib.syndication.views import Feed
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse, reverse_lazy

from .models import Article, Author, Category, Tag

import logging


logger = logging.getLogger(__name__)


class ArticlesListView(ListView):
    model = Article
    context_object_name = "articles"
    template_name = "blogapp/article_list.html"
    queryset = (
        Article.objects
        .filter(published_at__isnull=False)
        .order_by("-published_at")
        # .select_related("author")
        # .prefetch_related("tags")
        # .defer("content")
    )

    # def dispatch(self, request, *args, **kwargs):
    #     logger.info('Запрошена страница со списком статей')
    #     response = super().dispatch(request, *args, **kwargs)
    #     return response


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and additions blog articles"
    link = reverse_lazy("blogapp:article-list")

    def items(self):
        return (
            Article.objects
            .filter(published_at__isnull=False)
            .order_by("-published_at")[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.body[:200]

    # def item_link(self, item: Article):
    #     return reverse("blogapp:article", kwargs={"pk": item.pk})


class ArticleCreateView(CreateView):
    model = Article
    template_name = 'blogapp/create_article.html'
    fields = "title", "content", "pub_date", "author", "category", "tags",
    success_url = reverse_lazy("blogapp:article-list")


class AuthorCreateView(CreateView):
    model = Author
    template_name = 'blogapp/create_author.html'
    fields = "name", "bio"
    success_url = reverse_lazy("blogapp:authors-list")


class AuthorsListView(ListView):
    model = Author
    context_object_name = "authors"
    template_name = "blogapp/authors_list.html"

    def dispatch(self, request, *args, **kwargs):
        logger.info('Запрошена страница со списком авторов')
        response = super().dispatch(request, *args, **kwargs)
        return response


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'blogapp/create_category.html'
    fields = "name",
    success_url = reverse_lazy("blogapp:categories-list")


class CategoriesListView(ListView):
    model = Category
    context_object_name = "categories"
    template_name = "blogapp/categories_list.html"


class TagCreateView(CreateView):
    model = Tag
    template_name = 'blogapp/create_tag.html'
    fields = "name",
    success_url = reverse_lazy("blogapp:tags-list")


class TagsListView(ListView):
    model = Tag
    context_object_name = "tags"
    template_name = "blogapp/tags_list.html"
