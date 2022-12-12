from werkzeug import Request
from werkzeug.datastructures import Headers


class Middleware:
    def __init__(self, app, **kwargs):
        self.prefix = kwargs.get('url_prefix') or ""
        self.app = app

        self.cors_origins = kwargs.get('cors_origins') or []
        # self.cors_origins = ", ".join(self.cors_origins)

        self.cors_methods = kwargs.get('cors_methods') or ["GET", "POST", "PUT", "DELETE"]
        self.cors_methods = ", ".join(self.cors_methods)

    def __call__(self, environ, start_response):
        # request = Request(environ)

        # App urls prefix
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix

        # CORS
        def add_cors_headers(status, headers, exc_info=None):
            headers = Headers(headers)
            if environ.get('HTTP_ORIGIN') and environ['HTTP_ORIGIN'] in self.cors_origins:
                headers.add("Access-Control-Allow-Origin", environ['HTTP_ORIGIN'])
            headers.add("Access-Control-Allow-Headers", "Content-type, X-CSRF-Token, Authorization")
            headers.add("Access-Control-Allow-Credentials", "true")
            headers.add("Access-Control-Allow-Methods", self.cors_methods)
            headers.add("Access-Control-Expose-Headers", "Set-Cookie")
            return start_response(status, list(headers), exc_info)

        if environ.get("REQUEST_METHOD") == "OPTIONS":
            add_cors_headers("200 Ok", [("Content-Type", "text/plain")])
            return [b'200 Ok']

        # End
        return self.app(environ, add_cors_headers)
