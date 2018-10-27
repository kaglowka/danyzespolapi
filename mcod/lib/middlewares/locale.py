from django.utils.translation import activate
from django.utils.translation.trans_real import (
    get_supported_language_variant,
    language_code_re,
    parse_accept_lang_header
)

from mcod import settings


class LocaleMiddleware(object):
    def get_language_from_header(self, header):
        for accept_lang, unused in parse_accept_lang_header(header):
            if accept_lang == '*':
                break

            if not language_code_re.search(accept_lang):
                continue

            try:
                return get_supported_language_variant(accept_lang)
            except LookupError:
                continue

        try:
            return get_supported_language_variant(settings.LANGUAGE_CODE)
        except LookupError:
            return settings.LANGUAGE_CODE

    def process_request(self, req, resp):
        # 'pl,en-US;q=0.8,en;q=0.6' --> ['pl', 'en-US;q=0.8', 'en;q=0.6']
        accept_header = req.headers.get('ACCEPT-LANGUAGE', '')
        lang = self.get_language_from_header(accept_header)
        req.language = lang.lower()
        activate(req.language)

    def process_response(self, req, resp, resource, params):
        resp.append_header('Content-Language', req.language)
