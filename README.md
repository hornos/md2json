# Markdown 2 JSON

Infrastructure as Documentation as Markdown. No time for complex Infra managers? No team for IT? 
Some markdown documentation is the only think you can do. Fear not! Write markdown and parse to JSON.

## Installation
```bash
./mkvenv && ./install
```

## Usage Example
```bash
python md2json.py --md credentials.md | jq '."Networking Management"."tables"."Machines"'
```

```python
from md2json import MDParser

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--md', action="store", dest="md")
  args = parser.parse_args()
  md_parser = MDParser(args.markdown)
  raw_data = md_parser.parse()
```
