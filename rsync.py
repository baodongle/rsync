#!/usr/bin/env python3
import os
import difflib
from argparse import ArgumentParser


def parse_argument():
    parser = ArgumentParser(description="""rsync - a fast, versatile, remote
                                        (and local) file-copying tool""")
    parser.add_argument('-c', '--checksum', action='store_true',
                        help="skip based on checksum, not mod-time & size")
    parser.add_argument('-u', '--update', action='store_true',
                        help="skip files that are newer on the receiver")
    parser.add_argument('-r', '--recursive', action='store_true',
                        help="recurse into directories")
    parser.add_argument("source", nargs='+', metavar="SRC_FILE", type=str)
    parser.add_argument("destination", metavar="DESTINATION", type=str)
    args = parser.parse_args()
    return args


def create_destination_file(file):
    # if the destination isn't exists
    if not os.path.exists(file):
        with open(file, 'w'):
            pass


def get_checksum(file):
    """Sums the ASCII character values mod256 and returns
    the lower byte of the two's complement of that value"""
    sum = 0
    with open(file, 'r') as f:
        data = f.read()
        for i in range(len(data)):
            sum = sum + ord(data[i])
    temp = sum % 256
    rem = -temp
    return '%2X' % (rem & 0xFF)


def need_update(args, source, destination):
    src_stat = os.stat(source)
    dst_stat = os.stat(destination)
    if args.update:
        # With '-u' option:
        if dst_stat.st_mtime > src_stat.st_mtime:
            return False
    if args.checksum:
        # With '-c' option:
        return not get_checksum(source) == get_checksum(destination)
    else:
        # Default:
        return not (src_stat.st_mtime == dst_stat.st_mtime and
                    src_stat.st_size == dst_stat.st_size)


def copy_symlink(source, destination):
    if os.path.exists(destination):
        os.unlink(destination)
    linkto = os.readlink(source)
    os.symlink(linkto, destination)


def copy_hardlink(source, destination):
    if os.path.exists(destination):
        os.unlink(destination)
    os.link(source, destination)


def copy_file(source, destination):
    src_size = os.path.getsize(source)
    dst_size = os.path.getsize(destination)

    from_file = os.open(source, os.O_RDONLY)
    to_file = os.open(destination, os.O_RDWR)
    context_src = os.read(from_file, src_size).decode()
    context_dst = os.read(to_file, dst_size).decode()

    position_diff = None
    diffs = list(difflib.ndiff(context_src, context_dst))
    for i in range(len(diffs)):
        if diffs[i][0] in ['+', '-']:
            position_diff = i
            break

    if position_diff:
        count = src_size - position_diff
    else:
        count = src_size

    os.sendfile(to_file, from_file, position_diff, count)
    os.close(from_file)
    os.close(to_file)


def sync_file(source, destination):
    if os.path.islink(source):
        copy_symlink(source, destination)
    elif os.stat(source).st_nlink > 1:
        copy_hardlink(source, destination)
    else:
        stat_source = os.stat(source)
        os.chmod(destination, stat_source.st_mode)
        copy_file(source, destination)
        os.utime(destination, (stat_source.st_atime, stat_source.st_mtime))


def copy_tree(source, destination):
    list_dir = [f.name for f in os.scandir(source)]
    for item in list_dir:
        src = os.path.join(source, item)
        dst = os.path.join(destination, item)
        create_destination_file(dst)
        sync_file(src, dst)


def rsync(args, source, destination):
    if os.path.isfile(source):
        try:
            # 1 file source:
            create_destination_file(destination)

            if os.path.isfile(destination):
                # 1 file -> 1 file:
                if need_update(args, source, destination):
                    sync_file(source, destination)
            elif os.path.isdir(destination):
                # 1 file -> 1 dir
                target = os.path.join(destination, os.path.basename(source))
                create_destination_file(target)
                sync_file(source, target)
        except PermissionError:
            print(("rsync: send_files failed to open \"%s\": "
                   "Permission denied (13)" % os.path.realpath(source)))

    elif os.path.isdir(source):
        dst_path = os.path.join(destination, source)
        if not os.path.exists(dst_path):
            os.mkdir(dst_path)
        copy_tree(source, dst_path)
    else:
        print("rsync: link_stat \"%s\" failed: No such file or directory (2)"
              % os.path.realpath(source))


if __name__ == "__main__":
    args = parse_argument()
    if isinstance(args.source, list):
        for source in args.source:
            rsync(args, source, args.destination)
    else:
        rsync(args, args.source, args.destination)
