# -*- coding: utf-8 -*-
import json
import logging
import magic
import os
import rdflib
import re
import requests
import xml

from chardet import UniversalDetector
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from goodtables.validate import _parse_arguments
from io import BytesIO
from lxml import etree, html
from mimeparse import parse_mime_type
from mimetypes import MimeTypes
from tabulator import Stream
from tabulator.exceptions import FormatError
from urllib import parse
from zipfile import BadZipFile
from xlrd.biffh import XLRDError

from mcod.lib.hacks.goodtables import patch
from mcod.lib.inspector import NonThreadedInspector as Inspector

patch.apply()  # noqa: E402

mime = MimeTypes()

GUESS_FROM_BUFFER = [
    "application/octetstream",
    "application/octet-stream",
    "octet-stream",
    "octetstream",
    "application octet-stream"
]

logger = logging.getLogger('mcod')


class InvalidUrl(Exception):
    pass


class InvalidResponseCode(Exception):
    pass


class InvalidContentType(Exception):
    pass


def guess_file_encoding(path):
    _detector = UniversalDetector()
    with open(path, 'rb') as f:
        for line in f.readlines():
            _detector.feed(line)
            if _detector.done:
                break
    _detector.close()
    return _detector.result.get('encoding', 'utf-8')


def guess_spreadsheet_file_format(path, encoding):  # noqa: C901
    def _xls():
        _s = Stream(path, format='xls', encoding=encoding)
        try:
            _s.open()
            _s.close()
            return 'xls'
        except (FormatError, BadZipFile, ValueError, XLRDError, FileNotFoundError, NotImplementedError):
            return None

    def _xlsx():
        _s = Stream(path, format='xlsx', encoding=encoding)
        try:
            _s.open()
            _s.close()
            return 'xlsx'
        except ValueError:
            return 'xlsx'
        except (FormatError, BadZipFile, OSError, FileNotFoundError, KeyError):
            return None

    def _ods():
        _s = Stream(path, format='ods', encoding=encoding)
        try:
            _s.open()
            _s.close()
            return True

        except (FormatError, OSError, BadZipFile, FileNotFoundError, TypeError):
            return False

    encoding = encoding or 'utf-8'
    for func in [_xls, _xlsx, _ods]:
        res = func()
        if res:
            return res

    return None


def guess_text_file_format(path, encoding):  # noqa: C901
    def _json():
        try:
            with open(path, encoding=encoding) as f:
                json.load(f)
            return 'json'
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            return None

    def _csv():
        _s = Stream(path, format='csv', encoding=encoding)
        try:
            _s.open()
            _s.close()
            return 'csv'
        except (FormatError, UnicodeDecodeError, FileNotFoundError, BadZipFile):
            return None

    def _xml():
        try:
            etree.parse(path, etree.XMLParser())
            return 'xml'
        except etree.XMLSyntaxError:
            return None

    def _html():
        try:
            with open(path, 'rb') as fp:
                _res = html.fromstring(fp.read()).find('.//*')
                if _res:
                    _res.head
            return 'html' if res else None
        except (etree.XMLSyntaxError, IndexError):
            return None

    def _rdf():
        _extension = path.split('.')[-1]
        _format = 'xml' if _extension not in ('rdf', 'n3', 'nt', 'trix', 'rdfa', 'xml') else _extension
        try:
            _g = rdflib.Graph()
            _g.parse(path, format=_format)
            return 'rdf'
        except (TypeError, rdflib.exceptions.ParserError, xml.sax._exceptions.SAXParseException):
            return None

    encoding = encoding or 'utf-8'
    for func in [_json, _rdf, _xml, _html, _csv]:
        res = func()
        if res:
            return res

    return None


def file_format_from_content_type(content_type, family=None, extension=None):
    if family:
        results = list(filter(
            lambda x: x[0] == family and x[1] == content_type,
            settings.SUPPORTED_CONTENT_TYPES))
    else:
        results = list(filter(
            lambda x: x[1] == content_type,
            settings.SUPPORTED_CONTENT_TYPES))

    if not results:
        return None

    content_item = results[0]

    if extension and extension in content_item[2]:
        return extension

    return content_item[2][0]


def content_type_from_file_format(file_format):
    results = list(filter(lambda x: file_format in x[2], settings.SUPPORTED_CONTENT_TYPES))
    if not results:
        return None, None

    return results[0][0], results[0][1]


# def content_type_from_filename(filename):
#     format = filename.split('.')[-1]
#     return content_type_from_file_format(format)


def filename_from_url(url, content_type=None):
    f, ext = os.path.splitext(os.path.basename(parse.urlparse(url).path))
    f = f.strip('.') if f else ''
    ext = ext.strip('.') if ext else ''

    if not ext and content_type:
        ext = file_format_from_content_type(content_type)
        if not ext:
            ext = mime.guess_extension(content_type)
            ext = ext.strip('.') if ext else ''

    return f or 'unknown', ext


def _get_resource_type(response):
    family, content_type, options = parse_mime_type(response.headers.get('Content-Type'))

    if content_type == 'html':
        return 'website'

    if content_type == 'xml' or content_type == 'json':
        return 'api'

    return 'file'


def download_file(url, allowed_content_types=None):  # noqa: C901
    logger.debug(f"download_file({url}, {allowed_content_types})")
    try:
        URLValidator()(url)
    except ValidationError:
        raise InvalidUrl('Invalid url address: %s' % url)

    filename, format = None, None

    supported_content_types = allowed_content_types or [ct[1] for ct in settings.SUPPORTED_CONTENT_TYPES]

    r = requests.get(url, stream=True, allow_redirects=True, verify=False, timeout=180)

    if r.status_code != 200:
        raise InvalidResponseCode('Invalid response code: %s' % r.status_code)

    family, content_type, options = parse_mime_type(r.headers.get('Content-Type'))
    logger.debug(f'  Content-Type: {family}/{content_type};{options}')

    if content_type not in ('octet-stream', 'octetstream') and content_type not in supported_content_types:
        raise InvalidContentType('Unsupported type: %s' % r.headers.get('Content-Type'))

    resource_type = _get_resource_type(r)
    logger.debug(f'  resource_type: {resource_type}')

    if resource_type == 'file':
        content_disposition = r.headers.get('Content-Disposition', None)
        logger.debug(f'  content_disposition: {content_disposition}')
        if content_disposition:
            # Get filename from header
            res = re.findall("filename=(.+)", content_disposition)
            filename = res[0][:100] if res else None
            logger.debug(f'  filename: {filename}')
            if filename:
                filename = filename.replace('"', '')
                format = filename.split('.')[-1]
                logger.debug(f'  filename: {filename}, format: {format}')

        if not filename:
            name, format = filename_from_url(url, content_type)
            filename = '.'.join([name, format])
            logger.debug(f'  filename: {filename}, format: {format} - from url')

        filename = filename.strip('.')

        if content_type in ('octet-stream', 'octetstream'):
            family, content_type = content_type_from_file_format(format)
            logger.debug(f'  {family}/{content_type} - from file format')

        format = file_format_from_content_type(content_type, family=family, extension=format)
        logger.debug(f'  format:{format} - from content type')

        content = BytesIO(r.content)
        return resource_type, {
            'filename': filename,
            'format': format,
            'content': content
        }
    else:
        format = file_format_from_content_type(content_type, family)
        logger.debug(f'  format: {format} - from content type')
        if resource_type == 'api':
            return resource_type, {
                'format': format
            }
        else:
            if r.url != url:
                if r.history and r.history[-1].status_code == 301:
                    raise InvalidResponseCode('Resource location has been moved!')
            return resource_type, {
                'format': format
            }


def analyze_resource_file(path, extension=None):
    def isnt_msdoc_text(content_type):
        extensions = list(filter(
            lambda x: x[1] == content_type,
            settings.SUPPORTED_CONTENT_TYPES))[0][2]
        return len({'doc', 'docx'} & set(extensions)) == 0
    logger.debug(f"analyze_resource_file({path}, {extension})")
    m = magic.Magic(mime=True, mime_encoding=True)
    result = m.from_file(path)
    family, content_type, options = parse_mime_type(result)
    logger.debug(f"  parsed mimetype: {family}/{content_type});{options}")
    file_info = magic.from_file(path)
    logger.debug(f"  file info: {file_info}")
    encoding = options.get('charset', 'unknown')
    logger.debug(f"  encoding: {encoding}")
    extension = file_format_from_content_type(content_type, family=family, extension=extension)
    logger.debug(f"  extension: {extension}")
    if family == 'text' and content_type == 'plain':
        if encoding.startswith('unknown'):
            encoding = guess_file_encoding(path)
            logger.debug(f" encoding (guess-plain): {encoding}")
        extension = guess_text_file_format(path, encoding)
        logger.debug(f"  extension (guess-plain): {extension}")

    if extension in ('doc', 'docx', 'xls', 'xlsx', 'ods', 'odt') or content_type == 'msword':
        if encoding.startswith('unknown'):
            encoding = guess_file_encoding(path)
            logger.debug(f"  encoding (guess-spreadsheet): {encoding}")
        spreadsheet_format = guess_spreadsheet_file_format(path, encoding)
        if any((extension in ('xls', 'xlsx', 'ods'),
                isnt_msdoc_text(content_type),
                spreadsheet_format)):
            extension = spreadsheet_format
            logger.debug(f"  extension (guess-spreadsheet): {extension}")

    logger.debug(f'  finally: extension = {extension}, file_info = {file_info}, encoding = {encoding}')
    return extension, file_info, encoding


def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


# Module API

def validate_file_data(source, **options):
    source, options, inspector_settings = _parse_arguments(source, **options)

    # Validate
    inspector = Inspector(**inspector_settings)
    report = inspector.inspect(source, **options)

    return report


# def get_unique_slug(model_instance,  slug_field_name):
#     """
#     """
#     slug = getattr(model_instance, slug_field_name)
#     if slug:
#         unique_slug = slug
#         extension = 1
#         ModelClass = model_instance.__class__
#
#         while ModelClass.raw.filter(
#                 **{slug_field_name: slug}
#         ).exists():
#             unique_slug = '{}-{}'.format(slug, extension)
#             extension += 1
#
#         return unique_slug
