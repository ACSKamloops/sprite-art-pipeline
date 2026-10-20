#!/usr/bin/env python3
"""Quiet loopback-only review server; bulk PNG requests do not fill tool logs."""
import argparse
import functools
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_head(self):
        # Browser media seeking needs byte ranges; SimpleHTTPRequestHandler
        # otherwise advertises only the initial playable position.
        request_range=self.headers.get('Range')
        path=Path(self.translate_path(self.path))
        if not request_range or not path.is_file():
            self.remaining=None
            return super().send_head()
        size=path.stat().st_size
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',request_range.strip())
        if match and any(match.groups()):
            a,b=match.groups()
            if a:
                start=int(a); end=min(int(b) if b else size-1,size-1)
            else:
                count=int(b);start=max(0,size-count);end=size-1
            valid=0<=start<=end<size
        else:
            valid=False
        if not valid:
            self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers()
            return None
        f=path.open('rb');f.seek(start);self.remaining=end-start+1
        self.send_response(206)
        self.send_header('Content-Type',self.guess_type(str(path)))
        self.send_header('Accept-Ranges','bytes')
        self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length',str(self.remaining))
        self.end_headers();return f

    def copyfile(self, source, outputfile):
        if getattr(self,'remaining',None) is None:
            return super().copyfile(source,outputfile)
        remaining=self.remaining
        while remaining:
            block=source.read(min(65536,remaining))
            if not block:break
            outputfile.write(block);remaining-=len(block)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--port',type=int,default=8144);a=p.parse_args()
    ThreadingHTTPServer.request_queue_size=128
    server=ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(Handler,directory=str(a.root.resolve())))
    print(f'Local review: http://127.0.0.1:{a.port}/pilot/review-player/final.html',flush=True)
    server.serve_forever()
