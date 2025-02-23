import sys
import re
import os
import binascii
import zlib

def print_tree(entries):
    for entry in entries:
        print(f"{entry['type']} {entry['hash']}    {entry['filename']}")


def git_obj_info(path, hash):
    obj_path = path + '/' + ".git" + "/" + "objects" + '/' + hash[:2] + '/' + hash[2:]

    f = open(obj_path, "rb")
    obj = zlib.decompress(f.read())
    header, _, body = obj.partition(b'\x00')
    kind = header.split()[0]
    f.close()

    if kind == b'commit':
        return body.decode()
    else:
        output = ""
        i = 0
        while i < len(body):
            mode_end = body.find(b' ', i)

            name_end = body.find(b'\x00', mode_end)
            name = body[mode_end + 1:name_end].decode()

            sha = body[name_end + 1:name_end + 21]
            hash = sha.hex()

            obj_path = path + '/' + ".git" + "/" + "objects" + '/' + hash[:2] + '/' + hash[2:]

            f = open(obj_path, "rb")
            compr = zlib.decompress(f.read())
            typ = compr.split(b' ')[0].decode()
            f.close()

            output += typ + " " + hash + " " + name + '\n'
            i = name_end + 21

        return output.strip()

def last_commit_hash(repo, branch):
    path_to_branch = repo + '/' + ".git" + "/" + "refs" + '/' + "heads" + '/' + branch
    f = open(path_to_branch, 'r')
    hash = f.read()
    f.close()
    return hash.strip()

def read_object(repo, obj_hash):
    path = os.path.join(repo, ".git", "objects", obj_hash[:2], obj_hash[2:])
    try:
        f = open(path, "rb")
        compressed = f.read()
        f.close()
    except FileNotFoundError:
        sys.exit(f"Объект {obj_hash} не найден")
    data = zlib.decompress(compressed)
    header, _, content = data.partition(b'\x00')
    header = header.decode()
    obj_type, _ = header.split(" ", 1)
    return obj_type, content


def parse_commit(content):
    text = content.decode("utf-8", errors="replace")
    header_part, _, message = text.partition("\n\n")
    commit_data = {}
    commit_data["message"] = message.strip()
    commit_data["parents"] = []
    for line in header_part.splitlines():
        if line.startswith("tree "):
            commit_data["tree"] = line[len("tree "):].strip()
        elif line.startswith("parent "):
            commit_data["parents"].append(line[len("parent "):].strip())
        elif line.startswith("author "):
            m = re.match(r"^(author\s+)(.+ <[^>]+>)", line)
            if m:
                commit_data["author"] = m.group(2)
            else:
                commit_data["author"] = line[len("author "):].strip()
        elif line.startswith("committer "):
            m = re.match(r"^(committer\s+)(.+ <[^>]+>)", line)
            if m:
                commit_data["committer"] = m.group(2)
            else:
                commit_data["committer"] = line[len("committer "):].strip()
    return commit_data

def traverse_history(repo, initial_commit_hash):
    commit_hash = initial_commit_hash
    while commit_hash:
        obj_type, commit_content = read_object(repo, commit_hash)
        if obj_type != "commit":
            sys.exit(f"Объект {commit_hash} не является commit-объектом.")
        commit_data = parse_commit(commit_content)

        tree_hash = commit_data.get("tree")
        if not tree_hash:
            sys.exit(f"В коммите {commit_hash} отсутствует ссылка на дерево.")
        obj_type, tree_content = read_object(repo, tree_hash)
        if obj_type != "tree":
            sys.exit(f"Объект {tree_hash} не является tree-объектом.")
        entries = parse_tree(tree_content)
        print(f"TREE for commit {commit_hash}")
        print_tree(entries)

        parents = commit_data.get("parents", [])
        commit_hash = parents[0] if parents else None

def tree(path, branch):
    check = git_obj_info(path, last_commit_hash(path, branch))
    check = check.split('\n')
    print(check)
    for el in check:
        print('EL = ', el)
        if el.startswith('tree'):
            return git_obj_info(path, el.split(" ")[1])

def parse_tree(content):
    entries = []
    i = 0
    while i < len(content):
        j = content.find(b' ', i)
        mode = content[i:j].decode()
        i = j + 1
        j = content.find(b'\x00', i)
        filename = content[i:j].decode()
        i = j + 1
        # Следующие 20 байт – бинарный SHA1
        sha = content[i:i+20]
        hex_sha = binascii.hexlify(sha).decode()
        i += 20
        typ = "tree" if mode == "40000" else "blob"
        entries.append({
            "mode": mode,
            "type": typ,
            "filename": filename,
            "hash": hex_sha
        })
    return entries

path = sys.argv[1]
if len(sys.argv) == 2:
    full_path = path + '/' + ".git" + "/" + "refs" + '/' + "heads"
    for br in os.listdir(full_path):
        print(br)

else:
    branch = sys.argv[2]
    print('Chose option. Input 2, 3 or 4')
    check = int(input())
    if check == 2:
        hash = last_commit_hash(path, branch)
        print(git_obj_info(path, hash))
    elif check == 3:
        obj_type, commit_content = read_object(path, last_commit_hash(path, branch))
        commit_data = parse_commit(commit_content)
        tree_hash = commit_data.get("tree")
        if not tree_hash:
            sys.exit("В коммите отсутствует ссылка на дерево.")
        obj_type, tree_content = read_object(path, tree_hash)
        if obj_type != "tree":
            sys.exit("Объект не является tree-объектом.")
        entries = parse_tree(tree_content)
        print_tree(entries)
    else:
        # check 4
        traverse_history(path, last_commit_hash(path, branch))

    