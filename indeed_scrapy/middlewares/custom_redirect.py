from urlparse import urljoin
from scrapy import log
from scrapy.contrib.downloadermiddleware.redirect import BaseRedirectMiddleware

allow_redirect_urls = [
    'nl.conv.indeed.com',
]


def allow_redirect(location):
    for url in allow_redirect_urls:
        if url in location:
            return True
    return False


class CustomRedirectMiddleware(BaseRedirectMiddleware):
    """Handle redirection of requests based on response status and meta-refresh html tag"""

    def process_response(self, request, response, spider):
        if 'dont_redirect' in request.meta:
            if response.status in [301, 302, 303, 307] and 'Location' in response.headers:
                location = urljoin(request.url, response.headers['location'])

                if allow_redirect(location):
                    redirected = request.replace(url=location)
                    return self._redirect(redirected, request, spider, response.status)
            return response

        if request.method == 'HEAD':
            if response.status in [301, 302, 303, 307] and 'Location' in response.headers:
                redirected_url = urljoin(request.url, response.headers['location'])
                redirected = request.replace(url=redirected_url)
                return self._redirect(redirected, request, spider, response.status)
            else:
                return response

        if response.status in [302, 303] and 'Location' in response.headers:
            redirected_url = urljoin(request.url, response.headers['location'])
            redirected = self._redirect_request_using_get(request, redirected_url)
            return self._redirect(redirected, request, spider, response.status)

        if response.status in [301, 307] and 'Location' in response.headers:
            redirected_url = urljoin(request.url, response.headers['location'])
            redirected = request.replace(url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)

        return response