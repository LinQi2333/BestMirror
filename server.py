import requests
import os
import time
from urllib import request

import pickle # TODO: Potential security problems?

import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler

localProxy = request.getproxies()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

best_url = "https://storage.sekai.best/sekai-jp-assets/"
bestDBurl = "http://sekai-world.github.io/sekai-master-db-diff/"

cache_dir = "./cache/"

cache_expiration_time = 100

ignore_headers = [
    "Content-Encoding",
    "Content-Length",
    "expires",
    "Cache-Control",
    "Connection",
]
 
class SimpleHTTPGetHandler(BaseHTTPRequestHandler):
 
    def do_GET(self):
        file_name_with_ext = self.path[1:].split('/')[0]

        if file_name_with_ext[-5:] == ".json":
            self.handle_request(bestDBurl, file_name_with_ext)
        else:
            self.handle_request(best_url, self.path[1:])

    def handle_request(self, base_url, url):
        # url = self.path[1:] # Obtain paths without initial "/"
        # print(url)

        print("Origin - %s%s" % (base_url, url))

        cache_path = os.path.join(cache_dir, url)
        if os.path.isdir(cache_path):
            self.send_response(404)
            self.wfile.write(b"Cannot process directory")
            return

        # Path not exists or expired, then update
        if not (os.path.exists(cache_path) and not self.is_cache_expired(cache_path)):

            if os.path.exists(cache_path):
                os.remove(cache_path)

            res = requests.get(base_url + url, headers = headers, proxies = localProxy)
            # content_type = res.headers.get('Content-Type', 'text/plain')
            if not res:
                self.send_response(res.status_code)
                return
            
            # breakpoint()

            dir_path = os.path.dirname(cache_path)
            os.makedirs(dir_path, exist_ok = True)
            with open(cache_path, 'wb') as f:
                pickle.dump(res, f)

        # Path exists and not expired
        # if os.path.exists(cache_path) and not self.is_cache_expired(cache_path):
        if os.path.exists(cache_path): # Do not check cache expiry as we checked above; It may expire in between
            with open(cache_path, "rb") as f:
                contents = pickle.load(f)

            self.send_response(200)

            # breakpoint()

            # Copy all headers
            for header in contents.headers:
                if header in ignore_headers: # Disable compression
                    continue
                # print("%s - %s" % (header, contents.headers[header]))
                self.send_header(header, contents.headers[header])

            self.end_headers()
            self.wfile.write(contents.content)
            return

       #  else: # Path exists but expired
       #      if os.path.exists(cache_path):
       #          os.remove(cache_path)
       #          # Update
       #          res = requests.get(base_url + url, headers = headers, proxies = localProxy)
       #          content_type = res.headers.get('Content-Type', 'text/plain')
       #          if not res:
       #              self.send_response(res.status_code)
       #              return
       #      
       #          dir_path = os.path.dirname(cache_path)
       #          os.makedirs(dir_path, exist_ok = True)
       #          with open(cache_path, 'w', encoding='utf-8') as f:
       #              f.write(res.text)

    def is_cache_expired(self, cache_path):
        file_mtime = os.path.getmtime(cache_path)
        current_time = time.time()
        return (current_time - file_mtime) > cache_expiration_time

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog = 'BestMirror', description = 'A Simple mirror for various purposes')
    parser.add_argument('-p', '--port', type = int, default = 51234)
    args = parser.parse_args()

    httpd = HTTPServer(('0.0.0.0', args.port), SimpleHTTPGetHandler)
    print("Serving at http://0.0.0.0:%s" % (args.port))
    httpd.serve_forever()

