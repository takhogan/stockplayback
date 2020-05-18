from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import requests
import ssl


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        print('here')
        # Get the Auth Code
        # path, _, query_string = self.path.partition('?')
        # print(self.path.partition('?'))
        # print(self.path)
        # print(path)
        # print(query_string)
        # code = parse_qs(query_string)['code'][0]
        code = 'stockplayback'

        # Post Access Token Request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'authorization_code', 'access_type': 'offline', 'code': code, 'client_id': 'Consumer Key',
                'redirect_uri': 'Redirect URI'}
        authReply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
        print(authReply)
        # returned just to test that it's working
        self.wfile.write(authReply.text.encode())


httpd = HTTPServer(('', 8080), Handler)
print('Started server on port 8080')

# # SSL cert
# httpd.socket = ssl.wrap_socket(httpd.socket,
#                                keyfile='key.pem',
#                                certfile='cert.pem', server_side=True)

httpd.serve_forever()