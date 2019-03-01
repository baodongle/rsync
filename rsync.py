#!/usr/bin/env python3
import os
from argparse import ArgumentParser

"""./rsync.py [OPTIONS] SRC_FILE DESTINATION"""
def parse_argument():
    parser = ArgumentParser(description="""rsync - a fast, versatile, remote
                                        (and local) file-copying tool""")
    parser.add_argument('-c', '--checksum', action='store_true',
                        help="skip based on checksum, not mod-time & size")
    parser.add_argument('-u', '--update', action='store_true',
                        help="skip files that are newer on the receiver")
    parser.add_argument("source", type=str)
    parser.add_argument("destination", type=str)

def create_destination_file(file):
    if not os.path.exists(file):
        with open(file, 'w'):
            pass


def need_update(source, destination):
    src_stat = os.stat(source)
    dst_stat = os.stat(destination)
    return not (src_stat.st_mtime == dst_stat.st_mtime and
                src_stat.st_size == dst_stat.st_size)


def copy_symlink(source, destination):
    if os.path.exists(destination):
        os.unlink(destination)
    linkto = os.readlink(source)
    os.symlink(linkto, destination)


def copy_file(source, destination):
    source_size = os.path.getsize(source)
    from_file = os.open(source, os.O_RDONLY)
    to_file = os.open(destination, os.O_RDWR | os.O_CREAT)
    os.sendfile(to_file, from_file, 0, source_size)
    os.close(from_file)
    os.close(to_file)


def preserve(source, destination):
    # preserve permissions and modification times:
    stat_source = os.stat(source)
    os.utime(destination, (stat_source.st_atime, stat_source.st_mtime))
    os.chmod(destination, stat_source.st_mode)


def sync_file(source, destination):
    if os.path.islink(source):
        copy_symlink(source, destination)
    else:
        copy_file(source, destination)
        preserve(source, destination)


def copy_tree(source, destination):
    list_dir = [f.name for f in os.scandir(destination)]
    for item in list_dir:
        src = os.path.join(source, item)
        dst = os.path.join(destination, item)
        if os.path.islink(src):
            if os.path.lexists(dst):
                os.unlink(dst)
            os.symlink(os.readlink(src), dst)
            preserve(src, dst)
        elif os.path.isdir(src):
            copy_tree(src, dst)
        else:
            copy_file(source, destination)


def rsync(source, destination):
    if os.path.isfile(source):
        # 1 file source:
        create_destination_file(destination)  # if the destination isn't exists

        if os.path.isfile(destination):
            # 1 file -> 1 file:
            if need_update(source, destination):
                sync_file(source, destination)
        elif os.path.isdir(destination):
            # 1 file -> 1 dir
            target = os.path.join(destination, source)
            create_destination_file(target)
            sync_file(source, target)
        else:
            raise FileNotFoundError("No such file or directory: \
                                    '%s'" % destination)

    # else:
    #     if os.path.isdir(destination):
    #         copy_tree(source, destination)
    #     else:
    #         copy_file(source, destination)


if __name__ == "__main__":
    rsync("new", "dir2")
