from pyramid.config import Configurator
from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import unauthenticated_userid, authenticated_userid
from pyramid.security import has_permission

from sqlalchemy import engine_from_config
import logging
import locale

from pyramid.authorization import ACLAuthorizationPolicy
#from pyramid.authentication import AuthTktAuthenticationPolicy
from votabo.lib.security import RootFactory
from votabo.lib.security import ShimmieAuthenticationPolicy
from votabo.lib import cache
from votabo.models import (
    DBSession,
    Base,
    User,
    )


logger = logging.getLogger(__name__)


def configure_routes(config):
    config.add_route('home', '/')

    config.add_route('posts', '/post')
    config.add_route('post', '/post/{id}')
    config.add_route('posts/upload', '/upload')

    config.add_route('aliases', '/alias')
    config.add_route('alias', '/alias/{id}')

    config.add_route('users', '/user')
    config.add_route('user', '/user/{name}')

    config.add_route('pms', '/pm')
    config.add_route('pm', '/pm/{id}')

    config.add_route('comments', '/comment')
    config.add_route('comment', '/comment/{id}')

    config.add_route('logs', '/log')
    config.add_route('tags', '/tags')
    config.add_route('docs', '/doc')

    config.add_route('wikis', '/wiki')
    config.add_route('wiki', '/wiki/{title}')

    config.add_route('ipbans', '/ip-bans')
    config.add_route('ipban', '/ip-bans/{id}')

    config.add_route('postbans', '/post-bans')
    config.add_route('postban', '/post-bans/{id}')

    config.add_route('session', '/login')
    config.add_route('session-delete', '/logout')

    config.scan("votabo.views")


def configure_templates(config):
    def add_renderer_globals(event):
        def _has_permission(name):
            return has_permission(name, RootFactory, event["request"])

        event['has_permission'] = lambda perm: True
        event['static_url'] = lambda name: event["request"].static_url('votabo:static/' + name)
        event['route_url'] = event["request"].route_url
        event['route_path'] = event["request"].route_path
        event['has_permission'] = _has_permission
    config.add_subscriber(add_renderer_globals, 'pyramid.events.BeforeRender')


def configure_locale(config):
    locale.setlocale(locale.LC_ALL, '')


def configure_cache(config, settings):
    cache.fast.configure_from_config(settings, "cache.fast.")
    cache.slow.configure_from_config(settings, "cache.slow.")


def configure_auth(config):
    #def principals(user_id, request):
    #    u = User.by_name(user_id)
    #    return ["u:"+u.username, "g:"+u.category]
    #config.set_authentication_policy(AuthTktAuthenticationPolicy('q34i5uandfga08', callback=principals, hashalg='sha512'))

    config.set_authentication_policy(ShimmieAuthenticationPolicy())
    config.set_authorization_policy(ACLAuthorizationPolicy())


def configure_user(config):
    def user(request):
        un = authenticated_userid(request)
        u = User.by_name(un)
        return u
    config.add_request_method(user, property=True, reify=True)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory='votabo.security.RootFactory')
    config.add_static_view(name='static', path='votabo:static', cache_max_age=3600)

    configure_routes(config)
    configure_templates(config)
    configure_locale(config)
    configure_cache(config, settings)
    configure_auth(config)
    configure_user(config)

    from .lib.hmom import HttpMethodOverrideMiddleware

    app = config.make_wsgi_app()
    app = HttpMethodOverrideMiddleware(app)
    return app
