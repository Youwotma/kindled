import settings
from sqlitedict import SqliteDict
from gmail import GMail, Message
import os
from os.path import join, splitext, expanduser
from subprocess import check_call, CalledProcessError


processed = SqliteDict(expanduser('~/.processed_books.sqlite'), autocommit=True)


def send_ebook(book, convert=False):
    print('sending %r' % book)
    gm = GMail(*settings.GMAIL_AUTH)
    m = Message("convert" if convert else "regular",
                to=settings.KINDLE_EMAIL, text="foo",
                attachments=[book])
    gm.send(m)


for root, dirs, files in os.walk(settings.FOLDER):
    for file in files:
        fp = join(root, file)
        name, ext = splitext(file)
        if ext in (".pdf", ".movi", '.epub', '.azw3') and fp not in processed:
            if ext == ".pdf":
                send_ebook(join(root, file), True)
                send_ebook(join(root, file), False)
            elif ext == '.movi':
                send_ebook(join(root, file), False)
            elif ext in ('.epub', '.azw3'):
                dst = join('/tmp', '%s.pdf' % name)
                try:
                    check_call(['ebook-convert', join(root, file), dst])
                except CalledProcessError as e:
                    print(e)
                else:
                    send_ebook(dst, False)
                    send_ebook(dst, True)
            processed[join(root, file)] = True
