import os


if os.path.isfile("new"):
    if os.path.islink("new"):
        if os.path.exists("test"):
            os.unlink("test")
        linkto = os.readlink("new")
        os.symlink(linkto, "test")
