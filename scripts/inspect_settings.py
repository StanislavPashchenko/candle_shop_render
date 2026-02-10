import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import importlib
cfg = importlib.import_module('config.settings')
print('POSTGRES_DB=', cfg.POSTGRES_DB)
print('POSTGRES_USER=', cfg.POSTGRES_USER)
print('POSTGRES_PASSWORD=', cfg.POSTGRES_PASSWORD)
print('POSTGRES_HOST=', cfg.POSTGRES_HOST)
print('Condition:', bool(cfg.POSTGRES_DB and cfg.POSTGRES_USER and cfg.POSTGRES_PASSWORD and cfg.POSTGRES_HOST))
print('DATABASES=', cfg.DATABASES)
