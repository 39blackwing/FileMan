#!/usr/bin/python3.7

import filecmp
import os
import sys
import time


class Argument(object):
    path = ""
    move = rename = quiet = state = False

    def print_help(self):
        print("Run: Python3.7 fileman.py [Folder path] [Opinions]\n"
              "Opinions:\n"
              '    -m: Move duplicate files into "[Folder path]/duplicate"\n'
              "    -r: Rename files\n"
              "    -q: Quiet mode\n")

    def __init__(self):
        for i in range(1, len(sys.argv)):
            if (sys.argv[i].startswith("-")):
                for opinion in sys.argv[i][1:]:
                    if (opinion == "m"):
                        self.move = True
                    elif (opinion == "r"):
                        self.rename = True
                    elif (opinion == "q"):
                        self.quiet = True
                    else:
                        return
            else:
                if (len(self.path) == 0):
                    self.path = os.path.join(sys.argv[i])
                else:
                    return

        if ((self.rename or self.move) and len(self.path) != 0):
            self.state = True


def move_duplicate(filelist, argument):
    new_path = os.path.join(argument.path, "duplicate")
    last_name = filelist[0]
    new_list = [last_name]

    print(f"\nMoving duplicate files into \"{new_path}\" ...")
    if (not os.path.exists(new_path)):
        os.mkdir(new_path)

    for now_name in filelist[1:len(filelist)]:
        if (os.path.getsize(now_name) == os.path.getsize(last_name) and
                filecmp.cmp(now_name, last_name)):
            try:
                os.rename(
                    now_name,
                    os.path.join(new_path,
                                 now_name[len(argument.path):len(now_name)]))
            except PermissionError:
                print(f"Failed to move \"{now_name}\" : PermissionError")
                new_list.append(now_name)
                return []
        else:
            new_list.append(now_name)
            last_name = now_name

    print(f"Moved {len(filelist) - len(new_list)} duplicate files.")
    return new_list


def rename(filelist, argument):
    name_len = index = 0
    suffix = "*"

    print("\nRenaming files ...")
    if (not argument.quiet):
        index = int(input("Input the starting number: "))
        name_len = int(input("Input the length of filename: "))
        suffix = input(
            "Input the suffix of filename ('*' if keep the original): ")

    # Preprocess : Rename based on timestep.
    for i in range(0, len(filelist)):
        new_name = os.path.join(argument.path, f"{time.perf_counter_ns()}")
        if (filelist[i].rfind('.') != -1):
            new_name += filelist[i][filelist[i].rfind('.'):len(filelist[i])]
        try:
            os.rename(filelist[i], new_name)
        except PermissionError:
            print(f"Failed to rename \"{filelist[i]}\" : PermissionError")
            return False
        except FileExistsError:
            print(f"Failed to rename \"{filelist[i]}\" : FileExistsError")
            return False
        filelist[i] = new_name

    # Rename based on number.
    for old_name in filelist:
        new_name = os.path.join(argument.path, f"{index:0{name_len}}")
        if (suffix == "*"):
            if (old_name.rfind(".") != -1):
                new_name += old_name[old_name.rfind("."):len(old_name)]
        else:
            new_name += suffix
        os.rename(old_name, new_name)
        index += 1

    print(f"Renamed {len(filelist)} files.")
    return True


def main():
    arg = Argument()
    if (arg.state == False):
        arg.print_help()
        exit()

    if (not os.path.exists(arg.path)):
        print("Error: Folder does not exist.")
        exit()

    folder = os.listdir(arg.path)
    filelist = []

    for i in range(0, len(folder)):
        file = os.path.join(arg.path, folder[i])
        if (os.path.isfile(file)):
            filelist.append(file)

    filelist.sort(key=lambda x: (-os.path.getsize(x), x), reverse=True)

    if (arg.move):
        filelist = move_duplicate(filelist, arg)

    if (arg.rename and len(filelist)):
        rename(filelist, arg)

    print("\nDone.")


if __name__ == "__main__":
    main()
