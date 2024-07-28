#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: jianxiah
#
# Description:
# This script recursively scans a specified directory for files with specific
# extensions and formats them using clang-format.
#
# Usage:
#   python clang_format_dir.py <path_to_directory>

from pathlib import Path
from tqdm import tqdm
import subprocess
import sys
import threading
import queue

nthread = 8
exts = [
    ".h",
    ".hh",
    ".hpp",
    ".cl",
    ".cu",
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".vert",
    ".frag",
    ".comp",
    ".hlsl",
    ".glsl",
]


def format_func(cwd, shared_queue, pbar):
    while True:
        try:
            pth = shared_queue.get_nowait()
        except queue.Empty:
            break

        try:
            cmd_list = ["clang-format", "-style=file", "-i", str(pth)]
            subprocess.run(cmd_list, shell=True, cwd=cwd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to format {pth}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while formatting {pth}: {e}")
        finally:
            shared_queue.task_done()
            pbar.update(1)


def main():
    cwd = Path(sys.argv[1])
    if not (cwd / ".clang-format").exists():
        print(f"No .clang-format found in {cwd}")
        return

    shared_queue = queue.Queue()
    for p in cwd.glob("**/*"):
        if p.suffix in exts:
            shared_queue.put(p.resolve())

    total_items = shared_queue.qsize()
    with tqdm(total=total_items, desc="clang-format processing") as pbar:
        threads = []
        for _ in range(nthread):
            thread = threading.Thread(target=format_func, args=(cwd, shared_queue, pbar))
            threads.append(thread)
            thread.start()

        # for thread in threads:
        #     thread.join()

        shared_queue.join()


if __name__ == "__main__":
    main()
