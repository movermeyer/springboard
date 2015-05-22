import os

from elasticgit.search import SM

from springboard.utils import parse_repo_name

from unicore.content.models import Category, Page

from slugify import slugify


class SpringboardViews(object):

    def __init__(self, request):
        self.request = request
        self.language = request.locale_name
        self.settings = request.registry.settings
        es_host = self.settings.get('es.host', 'http://localhost:9200')
        self.es_settings = {
            'urls': [es_host]
        }

        repo_dir = self.settings.get('unicore.repos_dir', 'repos')
        repo_names = map(
            lambda repo_url: parse_repo_name(repo_url),
            self.settings['unicore.content_repo_urls'].strip().split('\n'))
        self.all_repo_paths = map(
            lambda repo_name: os.path.join(repo_dir, repo_name),
            repo_names)
        self.all_index_prefixes = map(
            lambda repo_name: slugify(repo_name),
            repo_names)

        search_config = {
            'in_': self.all_repo_paths,
            'index_prefixes': self.all_index_prefixes
        }
        self.all_categories = SM(Category, **search_config).es(
            **self.es_settings)
        self.all_pages = SM(Page, **search_config).es(**self.es_settings)

    def context(self, **context):
        defaults = {
            'user': self.request.user,
            'language': self.language,
            'all_categories': self.all_categories,
            'all_pages': self.all_pages,
        }
        defaults.update(context)
        return defaults