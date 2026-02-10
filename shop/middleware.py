from django.utils import translation
from django.conf import settings


class ForceDefaultLanguageMiddleware:
    """If user has no language in session or cookies, default to Ukrainian ('uk').

    This middleware should be placed after SessionMiddleware and before
    LocaleMiddleware so that LocaleMiddleware will pick up the session value.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # check explicit language set in session or cookie
        sess = getattr(request, 'session', None)
        cookie = request.COOKIES.get(getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language'))

        has_session_lang = bool(sess and sess.get('django_language'))
        set_cookie = False
        if not has_session_lang and not cookie:
            # set session language to Ukrainian so LocaleMiddleware uses it
            if sess is not None:
                try:
                    sess['django_language'] = 'uk'
                    sess.modified = True
                except Exception:
                    pass
            # also activate for this request
            translation.activate('uk')
            request.LANGUAGE_CODE = 'uk'
            set_cookie = True

        response = self.get_response(request)
        if set_cookie:
            try:
                cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
                # set long-lived cookie so subsequent visits default to Ukrainian
                response.set_cookie(cookie_name, 'uk', max_age=365*24*60*60)
            except Exception:
                pass
        return response
