#!/usr/bin/env python3
import os
from argparse import ArgumentParser
parser = ArgumentParser(description="""rsync - a fast, versatile,
                                    remote (and local) file-copying tool""")

def parse_argument()


def rsync(source, destination):
    if os.path.islink(source):
        linkto = os.readlink(source)
        os.symlink(linkto, destination)
    else:
        copy_file(source, destination)


def copy_file(source, destination):
    stat_source = os.stat(source)
    source_size = stat_source.st_size

    from_file = os.open(source, os.O_RDONLY)
    to_file = os.open(destination, os.O_RDWR | os.O_CREAT)
    os.sendfile(to_file, from_file, 0, source_size)
    os.close(from_file)
    os.close(to_file)

    os.utime(destination, (stat_source.st_atime, stat_source.st_mtime))
    os.chmod(destination, stat_source.st_mode)


if __name__ == "__main__":
    rsync("100pass", "new")
