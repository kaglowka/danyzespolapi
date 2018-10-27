from mcod.searchhistories.tasks import create_search_history


class SearchHistoryMiddleware:
    def process_response(self, req, resp, resource, req_succeeded):
        if hasattr(req, 'user') and 'q' in req.params:
            create_search_history.delay(req.url, req.params['q'], req.user.id)
