import os


directory = os.path.expanduser('~')


def humanReadable(size):
    if size > 1_000_000_000:
        return f"{size/1024**3:.2f}G"
    if size > 1_000_000:
        return f"{size/1024**2:.2f}M"
    if size > 1_000:
        return f"{size/1024:.2f}K"



def scan():
    explored = 0
    folders = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            file = os.path.join(root, filename)
            if os.path.isfile(file):
                path = ""
                for folder in file.split("/")[4:-1]:
                    folders[path + folder] = folders.get(path + folder, 0) + os.path.getsize(file)
                    path += folder + "/"
            explored += 1
            if not explored & 0b0001_1111_1111:
                print(f"{explored} files scanned")

    print("\n--- 10 biggest folders ---")

    flist = list(folders.items())
    flist = sorted(flist, key=lambda x: x[1])[::-1]
    stdo = ""
    for folder, size in flist[:10]:
        stdo += f"\033[94m{folder}\033[0m {humanReadable(size)}\n"
    print(stdo)


    fout = []
    for fo, si in flist:
        fout.append(fo)
        fout.append(" ")
        fout.append(str(si))
        fout.append("\n")

    with open("scan.dat", "w") as f:
        f.write("".join(fout))


def topSearch(amount):
    with open("scan.dat", "r") as file:
        lines = []
        for i in range(amount):
            line = file.readline()
            if not line:
                continue
            line = line.split()
            folder = "".join(line[:-1])
            size = int(line[-1])
            lines.append((folder, size))
    
    print(f"\n--- {amount} biggest folders ---")
    stdo = ""
    for folder, size in lines:
        stdo += f"\033[94m{folder}\033[0m {humanReadable(size)}\n"
    print(stdo)


def strSearch(string):
    with open("scan.dat", "r") as file:
        lines = []
        for line in file:
            print(line)
            if not line:
                continue
            line = line.split()
            folder = "".join(line[:-1])
            if string in folder:
                size = int(line[-1])
                lines.append((folder, size))

    print(f"\n--- Folders containing {string} ---")
    stdo = ""
    for folder, size in lines:
        stdo += f"\033[94m{folder}\033[0m {humanReadable(size)}\n"
    print(stdo)

strSearch(".vs")