import os


homeDir = os.path.expanduser('~')
saveDir = homeDir + "/.quota-scanner/"
scanFile = saveDir + "scan.dat"
filterDir = saveDir + "filter/"


def humanReadable(size):
    if size > 1_000_000_000:
        return f"{size/1024**3:.2f}Go"
    if size > 1_000_000:
        return f"{size/1024**2:.2f}Mo"
    if size > 1_000:
        return f"{size/1024:.2f}Ko"
    return f"{size}o"



def scan():
    explored = 0
    folders = {}
    for root, _, files in os.walk(homeDir):
        for filename in files:
            file = os.path.join(root, filename)
            if os.path.isfile(file):
                path = ""
                for folder in file.split("/")[4:-1]:
                    folders[path + folder] = folders.get(path + folder, 0) + os.path.getsize(file)
                    path += folder + "/"
            explored += 1
            if not explored & 0b0001_1111_1111:
                print(f" {explored} files scanned\r", end='')

    print("\n\n--- 10 biggest folders ---")

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

    with open(scanFile, "w") as f:
        f.write("".join(fout))


def topSearch(amount):
    with open(scanFile, "r") as file:
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
    with open(scanFile, "r") as file:
        lines = []
        for line in file:
            if not line:
                continue
            line = line.split()
            folder = "".join(line[:-1])
            if string in folder:
                size = int(line[-1])
                lines.append((folder, size))

    print(f"\n--- Folders containing {string} ---")
    index = 0
    while index < len(lines):
        stdo = ""
        for folder, size in lines[index:index+50]:
            start = folder.find(string)
            end = start + len(string)
            stdo += f"\033[94m{folder[:start]}\033[91m{folder[start:end]}\033[94m{folder[end:]}\033[0m {humanReadable(size)}\n"
        print(stdo)

        index += 50
        if index >= len(lines):
            print(f"{len(lines)}/{len(lines)} matches")
            break

        print(f"{index}/{len(lines)} matches")
        userInput = input("Press 'ENTER' to continue\nOr 'q' to exit\n")
        if userInput.lower() == 'q':
            return


def filter(args):
    filterHeader = """# Filters can be used to make a selection of folders
# that can be used for visualization or deletion
#
# If your filter doesn't work, you can debug it using 'filter debug %n' (feature not implemented yet)
#
# In order to configure this filter
# write a script using the folowing commands:
#
#
"""

    match args[0]:
        case "create":
            if not args[1]:
                print("Incorect usage: filter create <name>")
                return
            with open(filterDir + args[1], "w") as file:
                file.write(filterHeader % args[1])
            print(f"Created filter {args[1]}\n'filter edit {args[1]}' to edit")
        case "list":
            if os.path.exists(filterDir):
                filters = []
                for elem in os.listdir(filterDir):
                    if os.path.isfile():
                        filters.append(elem)
                print("\n".join(filters))
            else:
                print("No filters found")
        case "edit":
            if os.path.exists(filterDir):
                if not args[1]:
                    print("Incorect usage: filter edit <name>")
                    return
                if not os.path.exists(filterDir + args[1]):
                    print(f"This filter does not exists. You can create it using 'filter create {args[1]}'")
                    return
                os.system(f"nano {filterDir + args[1]}")
            else:
                print("No filters found")
        case "delete":
            if not args[1]:
                print("Incorect usage: filter delete <name>")
                return
            if not os.path.exists(filterDir + args[1]):
                print(f"This filter does not exists.")
                return
            os.remove(filterDir + args[1])
        case "explorer":
            if not os.path.exists(filterDir):
                if not os.path.exists(saveDir):
                    os.mkdir(saveDir)
                os.mkdir(filterDir)
            os.system("exo-open --launch FileManager " + filterDir)
        case "debug":
            if not args[1]:
                print("Incorect usage: filter debug <name>")
                return
            if not os.path.exists(filterDir + args[1]):
                print(f"This filter does not exists.")
                return
            #TODO
            print("Feature not implemented yet.")




#* Menu
COMMANDS = [
    #? "run" key will later be used to directly call the command's code
    {
        "name": "help",
        "usage": "help [<command>]",
        "aliases": ["h", "hp"],
        "description": "display this menu",
        "run": lambda *args:... #TODO
    },
    {
        "name": "scan",
        "usage": "scan",
        "aliases": ["sc"],
        "description": "deep scan your home directory",
        "run": lambda *args:... #TODO
    },
    {
        "name": "top",
        "usage": "top <amount>",
        "aliases": ["tp"],
        "description": "show the <amount> biggest folders",
        "run": lambda *args:... #TODO
    },
    {
        "name": "search",
        "usage": "search <word>",
        "aliases": ["sr"],
        "description": "show all the folders containing <word> in their path",
        "run": lambda *args:... #TODO
    },
    {
        "name": "filter",
        "usage": "filter <option> [<name>]",
        "aliases": ["ft"],
        "description": "manage filters; type 'help filter' for more informations",
        "run": lambda *args:... #TODO
    },
    {
        "name": "quit",
        "usage": "quit",
        "aliases": ["q", "exit"],
        "description": "quit the app",
        "run": lambda *args:... #TODO
    }
]

def displayHelp():
    menu = "--- All commands ---\n"
    for command in COMMANDS:
        menu += f"    {command["usage"]:<15}"
        if len(command["usage"] > 15):
            menu += "\n"
        menu += f" - ({"|".join(command["aliases"])}) {command["description"]}\n"
    print(menu)

    print(f"""--- All commands ---
    {"help":<15} - (h|hp) display this menu
    {"scan":<15} - (sc) deep scan you home directory
    {"top <amount>":<15} - (tp) show the <amount> biggest folders
    {"search <word>":<15} - (sr) show all the folders containing <word> in their path
    filter <option> [<name>]
    {" "*15} - (ft) manage filters; type 'help filter' for more informations
    {"quit":<15} - (q|exit) quit the app
""")

if __name__ == "__main__":
    if not os.path.exists(saveDir):
        os.mkdir(saveDir)
    if not os.path.exists(filterDir):
        os.mkdir(filterDir)

    displayHelp()
    while True:
        userInput = input("\033[95m~>\033[0m ")
        userInput = userInput.strip().split()
        if not userInput:
            continue
        match userInput[0]:
            case "help"|"hp"|"h":
                if not len(userInput) == 1:
                    match userInput[1]:
                        case "filter":
                            #TODO
                            print("Page not implemented yet.")
                            continue
                displayHelp()
            case "quit"|"q"|"exit":
                break
            case "scan"|"sc":
                scan()
            case "top"|"tp":
                if len(userInput) == 1:
                    print("Incorect usage: top <amount>")
                    continue
                try:
                    qte = int(userInput[1])
                except:
                    print("Incorect usage: top <amount>; <amount> must be a number")
                    continue
                topSearch(qte)
            case "search"|"sr":
                if len(userInput) == 1:
                    print("Incorect usage: search <word>")
                    continue
                strSearch(userInput[1])
            case "filter"|"ft":
                if len(userInput) == 1:
                    print("Incorect usage: filter <option>")
                    continue
                filter(userInput[1:])


