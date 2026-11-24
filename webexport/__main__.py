"""python -m webexport            # write web/public/data (needs the simulator build)
python -m webexport parity     # reference outputs for the JavaScript parity test"""
import sys

from .export import WEB_DATA, export_all
from .parity import write_parity
from pipelines import config


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "parity":
        print(write_parity(WEB_DATA, config.ROOT / "web" / "test" / "parity.json"))
    else:
        print(export_all())


if __name__ == "__main__":
    main()
