# The initial trial producer is retained as historical provenance in
# rejected/initial-trial-producer.py. It includes the rejected03 paint.
# Current construction is the frozen literal recipe/source map; this entry
# point verifies it or exports only to a fresh --output folder.
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('replay_source.py')),run_name='__main__')
