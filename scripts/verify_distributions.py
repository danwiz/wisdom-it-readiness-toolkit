"""Install each built distribution in a fresh environment and verify its CLI."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import venv

root = Path(__file__).resolve().parents[1]
packages = sorted((root/'dist').glob('*.whl')) + sorted((root/'dist').glob('*.tar.gz'))
if len(packages) != 2:
    raise SystemExit('Expected exactly one wheel and one source distribution in dist/')
for package in packages:
    with tempfile.TemporaryDirectory() as folder:
        environment = Path(folder)/'venv'
        venv.EnvBuilder(with_pip=True).create(environment)
        scripts = environment/('Scripts' if os.name == 'nt' else 'bin')
        python = scripts/('python.exe' if os.name == 'nt' else 'python')
        cli = scripts/('witrt.exe' if os.name == 'nt' else 'witrt')
        subprocess.run([str(python),'-m','pip','install',str(package)],check=True,cwd=folder)
        subprocess.run([sys.executable,str(root/'scripts/verify_installed.py'),str(cli)],check=True,cwd=folder)
        print(f'Verified {package.name}', flush=True)
