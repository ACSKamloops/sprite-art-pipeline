#!/usr/bin/env python3
"""Loopback-only range-capable video server; no external publication."""
import argparse, functools, re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.remaining=None
        requested=self.headers.get('Range')
        path=Path(self.translate_path(self.path))
        if not requested or not path.is_file():return super().send_head()
        total=path.stat().st_size
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',requested)
        if not match or (not match[1] and not match[2]):
            self.send_error(416);return None
        if match[1]:
            start=int(match[1]);end=min(int(match[2]) if match[2] else total-1,total-1)
        else:
            length=int(match[2]);start=max(0,total-length);end=total-1
        if start>=total or end<start:
            self.send_response(416);self.send_header('Content-Range',f'bytes */{total}');self.end_headers();return None
        file=path.open('rb');file.seek(start);self.remaining=end-start+1
        self.send_response(206);self.send_header('Content-Type',self.guess_type(str(path)))
        self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{total}')
        self.send_header('Content-Length',str(self.remaining));self.end_headers();return file
    def copyfile(self,source,outputfile):
        if self.remaining is None:return super().copyfile(source,outputfile)
        while self.remaining:
            chunk=source.read(min(65536,self.remaining))
            if not chunk:break
            outputfile.write(chunk);self.remaining-=len(chunk)

def main():
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--port',type=int,default=8153);a=p.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(Handler,directory=str(a.directory.resolve())))
    print(f'Local motion review: http://127.0.0.1:{a.port}/',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
