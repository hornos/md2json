import sys
import mistune
from mistune.plugins import plugin_table
import json
import argparse

# https://mistune.readthedocs.io/en/latest/advanced.html
# https://www.markdownguide.org/extended-syntax/
# https://github.com/lepture/mistune-contrib/blob/master/mistune_contrib/meta.py

# TODO: custom id -> lookup table

import re

INDENTATION = re.compile(r'\n\s{2,}')
META = re.compile(r'^(\w+):\s*(.+?)\n')

DESCRIPTION = '''
Usage:

  python md2json.py --md credentials.md | jq '."Networking Management"."tables"."Machines"'

'''

def preparse_remove_latex_control(text):
  return text.replace('\\tiny', "").replace('\\normalsize', "")
# def

def preparse_metadata(text):
  """Parse the given text into metadata and strip it for a Markdown parser.
  :param text: text to be parsed
  """
  rv = {}
  m = META.match(text)

  while m:
    key = m.group(1)
    value = m.group(2)
    value = INDENTATION.sub('\n', value.strip())
    rv[key] = value
    text = text[len(m.group(0)):]
    m = META.match(text)

  # print('TEXT', text)
  # print('RV', rv)

  return rv, text
# def


class StopError(Exception):
  """Base class for exceptions in this module."""
  pass

class JSONRenderer(mistune.HTMLRenderer):
  def __init__(self, escape=True, allow_harmful_protocols=None):
    super().__init__(escape, allow_harmful_protocols)
    # defaults
    self._data = { 'Root': { 'level': 0, 'paragraphs': [], 'tables': {} } }
    self._caption = 'Root'
    self._table = 'Undefined'
    self._stop = False
  # inline level
  # def codespan(self, text):
  #   return json.dumps({'type':'codepsan', 'data': text})
  # def text(self, text):
  #   return text
  # link(self, link, text=None, title=None)
  # image(self, src, alt="", title=None)
  # emphasis(self, text)
  # strong(self, text)
  # linebreak(self)
  # newline(self)
  # inline_html(self, html)

  def set_args(self, args):
    self._args = args

#  # block level
  def paragraph(self, text):
    self._data[self._caption]['paragraphs'].append(text)
    if(self._args.debug): print('PARAGRAPH:' + text + '\n')
    return 'PARAGRAPH:' + text + '\n'
    # return text
#
  def heading(self, text, level):
    if text.startswith('STOP'):
      raise StopError
      # STOP processing

    if text.startswith('Table:'):
      caption = text.replace('Table:', '').strip()
      self._data[self._caption]['tables'][caption] = []
      self._table = caption
      if(self._args.debug): print('Table:' + caption + '\n')
      return 'Table:' + caption + '\n'
    # fi
    # Section
    self._table = 'Undefined'
    self._caption = text
    self._data[text] = { 'level': level, 'paragraphs': [], 'tables': {} }
    return 'HEADING:' + text + '\n'
#
#  def thematic_break(self):
#    pass
#
#  def block_text(self, text):
#    return text
#
#  def block_code(self, code, info=None):
#    pass
#
#  def block_quote(self, text):
#    pass
#
#  def block_html(self, html):
#    pass
#
#  def block_error(self, html):
#    pass
#
  def list(self, text, ordered, level, start=None):
    return text
#
  def list_item(self, text, level):
    return text

#  # provide by table plugin
  def table(self, text):
    if(self._args.debug): print('table text:' + text + '\n')
    return text
#
  def table_head(self, text):
    row = text.split('|')
    del row[-1]
    self._data[self._caption]['tables'][self._table].append(row)
    return 'THEAD' + text + '\n'
#
  def table_body(self, text):
    return 'TBODY' + text + '\n'
#  
  def table_row(self, text):
    row = text.split('|')
    del row[-1]
    self._data[self._caption]['tables'][self._table].append(row)
    return 'TROW' + text + '\n'
#
  def table_cell(self, text, align=None, is_head=False):
    return text + '|'

# class

class MDParser():
  def __init__(self, args):
    self._markdown_input = args.markdown
    self._args = args

  def parse(self):
    with open(self._markdown_input, 'r') as file:
      renderer = JSONRenderer()
      renderer.set_args(self._args)
      raw_data = None
      try:
        # Run the parser
        markdown_parser = mistune.create_markdown( renderer=renderer, plugins=[plugin_table] )
        markdown_source = file.read()
        (rv, text) = preparse_metadata( markdown_source )
        text = preparse_remove_latex_control(text)
        markdown_parser( text )
      except StopError:
        pass
      except Exception as e:
        print(e)
        sys.exit(1)
      finally:
        # print(renderer._data)
        raw_data = renderer._data
        raw_data['Metadata'] = rv
        return raw_data  

def main():
  parser = argparse.ArgumentParser(description='Makdown 2 JSON Converter for easy Infra Docs')

  parser.add_argument('--debug', action='store_true', default=False )

  parser.add_argument( '--md', 
                       action="store", dest="markdown",
                       help="Markdown file to process" )

  args = parser.parse_args()
  if(args.markdown == None):
    parser.print_help()
    print(DESCRIPTION)
    sys.exit(0)

  md_parser = MDParser(args)
  raw_data = md_parser.parse()
  # print('RAW_DATA:', raw_data)
  print(json.dumps(raw_data))

if __name__ == "__main__":
  main()

  # python md2json.py --md credentials.md | jq '."Networking Management"."tables"."Machines"'
