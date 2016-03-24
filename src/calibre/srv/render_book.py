#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import sys, re, os, json
from functools import partial
from future_builtins import map
from urlparse import urlparse

from cssutils import replaceUrls
from lxml.etree import Comment, tostring

from calibre.ebooks.oeb.base import (
    OEB_DOCS, escape_cdata, OEB_STYLES, rewrite_links, XPath, urlunquote, XLINK, XHTML)
from calibre.ebooks.oeb.iterator.book import extract_book
from calibre.ebooks.oeb.polish.container import Container as ContainerBase
from calibre.ebooks.oeb.polish.cover import set_epub_cover, find_cover_image
from calibre.ebooks.oeb.polish.toc import get_toc
from calibre.ebooks.oeb.polish.utils import guess_type
from calibre.utils.short_uuid import uuid4
from calibre.utils.logging import default_log

RENDER_VERSION = 1  # Also change this in read_book.ui.pyj
BLANK_JPEG = b'\xff\xd8\xff\xdb\x00C\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\t\x08\n\n\t\x08\t\t\n\x0c\x0f\x0c\n\x0b\x0e\x0b\t\t\r\x11\r\x0e\x0f\x10\x10\x11\x10\n\x0c\x12\x13\x12\x10\x13\x0f\x10\x10\x10\xff\xc9\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xcc\x00\x06\x00\x10\x10\x05\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xd2\xcf \xff\xd9'  # noqa

def encode_component(x):
    return x.replace(',', ',c').replace('|', ',p')

def decode_component(x):
    return x.replace(',p', '|').replace(',c', ',')

def encode_url(name, frag=''):
    name = encode_component(name)
    if frag:
        name += ',,' + encode_component(frag)
    return name

def decode_url(x):
    parts = list(map(decode_component, re.split(',,', x, 1)))
    if len(parts) == 1:
        parts.append('')
    return parts

class Container(ContainerBase):

    tweak_mode = True

    def __init__(self, path_to_ebook, tdir, log=None, book_hash=None):
        log = log or default_log
        book_fmt, opfpath, input_fmt = extract_book(path_to_ebook, tdir, log=log)
        ContainerBase.__init__(self, tdir, opfpath, log)
        excluded_names = {
            name for name, mt in self.mime_map.iteritems() if
            name == self.opf_name or mt == guess_type('a.ncx') or name.startswith('META-INF/') or
            name == 'mimetype'
        }
        raster_cover_name, titlepage_name = self.create_cover_page(input_fmt.lower())

        self.book_render_data = data = {
            'version': RENDER_VERSION,
            'toc':get_toc(self).as_dict,
            'spine':[name for name, is_linear in self.spine_names],
            'link_uid': uuid4(),
            'book_hash': book_hash,
            'is_comic': input_fmt.lower() in {'cbc', 'cbz', 'cbr', 'cb7'},
            'raster_cover_name': raster_cover_name,
            'title_page_name': titlepage_name,
        }
        # Mark the spine as dirty since we have to ensure it is normalized
        for name in data['spine']:
            self.parsed(name), self.dirty(name)
        self.inject_script(data['spine'])
        self.virtualized_names = set()
        self.virtualize_resources()
        def manifest_data(name):
            return {'size':os.path.getsize(self.name_path_map[name]), 'is_virtualized': name in self.virtualized_names, 'mimetype':self.mime_map.get(name)}
        data['files'] = {name:manifest_data(name) for name in set(self.name_path_map) - excluded_names}
        self.commit()
        for name in excluded_names:
            os.remove(self.name_path_map[name])
        with lopen(os.path.join(self.root, 'calibre-book-manifest.json'), 'wb') as f:
            f.write(json.dumps(self.book_render_data, ensure_ascii=False).encode('utf-8'))

    def create_cover_page(self, input_fmt):
        if input_fmt == 'epub':
            def cover_path(action, data):
                if action == 'write_image':
                    data.write(BLANK_JPEG)
            return set_epub_cover(self, cover_path, (lambda *a: None))
        raster_cover_name = find_cover_image(self, strict=True)
        if raster_cover_name is None:
            item = self.generate_item(name='cover.jpeg', id_prefix='cover')
            raster_cover_name = self.href_to_name(item.get('href'), self.opf_name)
        with self.open(raster_cover_name, 'wb') as dest:
            dest.write(BLANK_JPEG)
        item = self.generate_item(name='titlepage.html', id_prefix='titlepage')
        titlepage_name = self.href_to_name(item.get('href'), self.opf_name)
        self.dirty(self.opf_name)
        return raster_cover_name, titlepage_name

    def inject_script(self, spine):
        src = 'injected-script-' + self.book_render_data['link_uid']
        for name in spine:
            root = self.parsed(name)
            head = tuple(root.iterchildren(XHTML('head')))
            head = head[0] if head else root.makeelement(XHTML('head'))
            root.insert(0, head)
            script = root.makeelement(XHTML('script'))
            script.set('type', 'text/javascript')
            script.set('src', src)
            script.set('data-secret', 'secret-key-' + self.book_render_data['link_uid'])
            head.insert(0, script)
            self.dirty(name)

    def virtualize_resources(self):

        changed = set()
        link_uid = self.book_render_data['link_uid']
        resource_template = link_uid + '|{}|'
        xlink_xpath = XPath('//*[@xl:href]')
        link_xpath = XPath('//h:a[@href]')

        def link_replacer(base, url):
            if url.startswith('#'):
                frag = urlunquote(url[1:])
                if not frag:
                    return url
                changed.add(base)
                return resource_template.format(encode_url(base, frag))
            purl = urlparse(url)
            if purl.netloc or purl.query:
                return url
            if purl.scheme and purl.scheme != 'file':
                return url
            if not purl.path or purl.path.startswith('/'):
                return url
            url, frag = purl.path, purl.fragment
            name = self.href_to_name(url, base)
            if name:
                frag = urlunquote(frag)
                url = resource_template.format(encode_url(name, frag))
                changed.add(base)
            return url

        for name, mt in self.mime_map.iteritems():
            if mt in OEB_STYLES:
                replaceUrls(self.parsed(name), partial(link_replacer, name))
                self.virtualized_names.add(name)
            elif mt in OEB_DOCS:
                self.virtualized_names.add(name)
                root = self.parsed(name)
                rewrite_links(root, partial(link_replacer, name))
                for a in link_xpath(root):
                    href = a.get('href')
                    if href.startswith(link_uid):
                        a.set('href', 'javascript:void(0)')
                        a.set('data-' + link_uid, href.split('|')[1])
                    else:
                        a.set('target', '_blank')
                    changed.add(name)
            elif mt == 'image/svg+xml':
                self.virtualized_names.add(name)
                changed = False
                xlink = XLINK('href')
                for elem in xlink_xpath(self.parsed(name)):
                    elem.set(xlink, link_replacer(name, elem.get(xlink)))

        tuple(map(self.dirty, changed))

    def serialize_item(self, name):
        mt = self.mime_map[name]
        if mt not in OEB_DOCS:
            return ContainerBase.serialize_item(self, name)
        # Normalize markup
        root = self.parsed(name)
        for comment in tuple(root.iterdescendants(Comment)):
            comment.getparent().remove(comment)
        escape_cdata(root)
        return tostring(root, encoding='utf-8', xml_declaration=True, with_tail=False, doctype='<!DOCTYPE html>')

def render(pathtoebook, output_dir, book_hash=None):
    Container(pathtoebook, output_dir, book_hash=book_hash)

if __name__ == '__main__':
    c = Container(sys.argv[-2], sys.argv[-1])