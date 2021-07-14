import sys

from engine.duitang_album import DuiTangAlbum
from lib import common


if __name__ == '__main__':
    target = common.Target(sys.argv[1], sys.argv[2])
    common.invoke(DuiTangAlbum, target)
