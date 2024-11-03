"""
Copy files recursively from various folders into one target folder.

rcopy.py <glob_pattern> <source_root> <destination_folder>

/src/1/a.txt
/src/2/b.txt
/src/3/a.txt
/src/4/1/c.txt

rcopy *.txt /src /dest --move

/dest/a.txt
/dest/b.txt
/dest/a(1).txt
/dest/c.txt
"""
import argparse
import shutil
from pathlib import Path
import fnmatch
from typing import Generator



def copyfile(
        src: Path, 
        dst: Path, 
        move: bool = False,
        quiet: bool = False, 
        dryrun: bool = False, 
        ) -> bool:
    """Copy (or move) a file from src to dst."""
    if dst.exists():
        return False
    if move:
        if not quiet:
            print(f"Move {src} -> {dst}")
        if not dryrun:
            shutil.move(src, dst)
    else:
        if not quiet:
            print(f"Copy {src} -> {dst}")
        if not dryrun:
            shutil.copyfile(src, dst)
    return True


def filenames_with_index(
        name: Path | str, 
        max_index: int | None = None,
        ) -> Generator[Path, None, None]:
    """
    Generating filenames with incrementing index to avoid collisions.

    :param name: The filename.
    :param max_index: (optional) Stop the generator at this index.
    :return: The generator object.
    
    >>> fn = filenames_with_index(Path("abc.txt"))
    >>> str(next(fn))
    'abc.txt'
    >>> str(next(fn))
    'abc(1).txt'
    >>> str(next(fn))
    'abc(2).txt'
    >>> for fn in filenames_with_index(Path("abc"), max_index=2): print(fn)
    'abc'
    'abc(1)'
    'abc(2)'
    """
    if isinstance(name, str):
        name = Path(name)
    index: int = 0
    while True:
        yield Path(name.stem + (f"({index})" if index else "") + name.suffix)
        if max_index is not None and index == max_index:
            return
        index += 1


def rcopy(
        pattern: str,
        src: Path | str, 
        dst: Path | str, 
        move: bool = False,
        quiet: bool = False, 
        dryrun: bool = False, 
        ) -> int:
    """
    Copy all files matching shell pattern from src recursively into dst.

    :param pattern: Only files which names matches this shell pattern are 
        copied.
    :param src: The source directory. This directory is traversed recursively.
    :param dst: The destination directory. All files within src which match 
        pattern are copied into this directory.
    :param move: If true, move files instead of copy.
    :param quiet: No prints to stdout.
    :param dryrun: If true, no copying takes place.
    :return: The number of files copied.
    """
    if isinstance(src, str):
        src = Path(src)
    if isinstance(dst, str):
        dst = Path(dst)
    count: int = 0
    for root, _, filenames in src.walk(top_down=False):
            for filename in fnmatch.filter(filenames, pattern):
                for dst_filename in filenames_with_index(filename):
                    if copyfile(
                            root / filename, 
                            dst / dst_filename,
                            move=move,
                            quiet=quiet,
                            dryrun=dryrun,
                            ):
                        count += 1
                        break
    return count


def main() -> int:
    """"""
    parser = argparse.ArgumentParser(prog="rcopy", description="Copy files recursively from a dirtree to a common folder.")
    parser.add_argument("-m", "--move", action="store_true", help="Move instead of copy.")
    parser.add_argument("-n", "--dryrun", action="store_true", help="Do not actually copy or move the files.")
    parser.add_argument("-q", "--quiet", action="store_true", help="No output on console.")
    parser.add_argument("pattern", type=str, help="The filename pattern.")
    parser.add_argument("src", type=str, help="The source directory.")
    parser.add_argument("dest", type=str, help="The destination directory.")
    args = parser.parse_args()
    rcopy(args.pattern, args.src, args.dest, args.move, args.quiet, args.dryrun)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
