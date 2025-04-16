import subprocess
import sysconfig
import os
import sys

library_path = sysconfig.get_config_var('LIBDIR')
library_name = sysconfig.get_config_var('INSTSONAME')

if library_path and library_name:
    full_path = os.path.join(library_path, library_name)
else:
    raise RuntimeError("Could not determine the libpython library path.")


prefix = 'GLIBC_'
cmd=['objdump', '-T', full_path]
out = subprocess.run(cmd, capture_output=True, check=True)
stdout = out.stdout.decode()
for line in stdout.splitlines():
    if not line: continue
    line = line.split()
    if len(line) < 5: continue
    glibc = line[4]
    if not glibc.startswith(prefix): continue
    glibc = glibc[len(prefix):]
    glibc = glibc.replace('.', '_')
    print(glibc)
