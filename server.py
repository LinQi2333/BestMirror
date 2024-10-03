import requests
import os
from urllib import request

localProxy = request.getproxies()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

best_url = "https://storage.sekai.best/sekai-jp-assets/"
test_path = "event_story/event_ashiato_2021/scenario_rip/event_39_08.asset"

cache_dir = "./cache/"

# a = requests.get(best_url + test_path, headers=headers, proxies=localProxy).text
# print(a)

from http.server import HTTPServer, BaseHTTPRequestHandler
 
class SimpleHTTPGetHandler(BaseHTTPRequestHandler):
 
    def do_GET(self):
        url = self.path[1:] # Obtain paths without initial "/"
        print(url)

        cache_path = os.path.join(cache_dir, url)
        if os.path.isdir(cache_path):
            self.send_response(404)
            self.wfile.write(b"Cannot process directory")
            return
        
        # Check if url exists
        if not os.path.exists(cache_path):

            res = requests.get(best_url + url, headers = headers, proxies = localProxy)
            if not res:
                self.send_response(res.status_code)
                return
            
            dir_path = os.path.dirname(cache_path)
            os.makedirs(dir_path, exist_ok = True)
            with open(cache_path, 'w') as f:
                f.write(res.text)

        if os.path.exists(cache_path):

            with open(cache_path) as f:
                contents = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(contents, encoding='utf-8'))

            return

        self.send_response(404)
        self.wfile.write(b"Cannot process request.")

if __name__ == '__main__':
    httpd = HTTPServer(('0.0.0.0', 51234), SimpleHTTPGetHandler)
    print("Serving at http://0.0.0.0:51234")
    httpd.serve_forever()

