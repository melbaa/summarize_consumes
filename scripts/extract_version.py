import sys
from pathlib import Path
from melbalabs.summarize_consumes.package import VERSION

if len(sys.argv) != 2:
    print("Usage: extract_version.py <output_file>")
    sys.exit(1)

output_file = Path(sys.argv[1])
output_file.write_bytes(VERSION.encode())
