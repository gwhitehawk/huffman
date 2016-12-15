import yaml

from collections import deque


class Node(object):
    def __init__(self, name, label="", parent=None, left_child=None, right_child=None):
        self.parent = parent
        self.left_child = left_child
        self.right_child = right_child
        self.name = name
        self.label = label


class RootTable(object):
    def __init__(self, root, table):
        self.root = root
        self.table = table


class Huffman(object):
    def __init__(self):
        with open("frequencies.yml", "r") as f:
            frequencies = yaml.load(f.read())
            self.trees = {}
            for key in frequencies:
                self.trees[key] = self.build_tree(frequencies[key])

    def build_tree(self, lang_freq):
        tree = sorted([(Node([key]), value) for key, value in lang_freq.iteritems()], key=lambda freq: freq[1], reverse=True)
        while len(tree) > 1:
            self.contract(tree)
        table = self.root_to_table(tree[0])
        return RootTable(tree[0], table)

    def contract(self, tree):
        left_node, left_freq = tree.pop()
        right_node, right_freq = tree.pop()
        new_node = Node(left_node.name + right_node.name, "", None, left_node, right_node)
        left_node.parent = new_node
        left_node.label = "0"
        right_node.parent = new_node
        right_node.label = "1"
        new_freq = left_freq + right_freq
        cur = 0
        while cur < len(tree) and tree[cur][1] >= new_freq:
            cur += 1
        tree.insert(cur, (new_node, new_freq))

    def root_to_table(self, root):
        browsed = deque([root[0]])
        visited = {}
        while browsed:
            top = browsed.popleft()
            if top.left_child is not None:
                top.left_child.label = top.label + top.left_child.label
                browsed.append(top.left_child)
            if top.right_child is not None:
                top.right_child.label = top.label + top.right_child.label
                browsed.append(top.right_child)
            if len(top.name) == 1:
                visited[top.name[0]] = top.label
        return visited

    def encode(self, lang, word):
        tree = self.trees[lang]
        encoded = ""
        for letter in word:
            if letter in tree.table:
                encoded += tree.table[letter]
            else:
                encoded += letter
        return encoded

    def decode(self, lang, word):
        decode = ""
        tree = self.trees[lang]
        current_node = tree.root[0]
        current_word = word
        unknown_char = False
        while current_word:
            while len(current_node.name) > 1 and not unknown_char:
                if current_node.left_child is not None and current_word.startswith(current_node.left_child.label):
                    current_node = current_node.left_child
                elif current_node.right_child is not None and current_word.startswith(current_node.right_child.label):
                    current_node = current_node.right_child
                else:
                    unknown_char = True

            if not unknown_char:
                decode += current_node.name[0]
                current_word = current_word[len(current_node.label):]
            else:
                decode += current_word[0]
                current_word = current_word[1:]
                unknown_char = False
            current_node = tree.root[0]
        return decode


def main():
    huffman = Huffman()
    language = raw_input('Choose language: eng, svk [eng]: ') or 'eng'
    print "Huffman encoding for language: " + language
    for k,v in huffman.trees[language].table.iteritems():
        print "{}: {}".format(k, v)
    cmd = ""
    while cmd != 'quit':
        cmd = raw_input('Choose action [(e)ncode, (d)ecode, quit]: ')
        if cmd not in ['e', 'd']:
            if cmd != 'quit':
                print 'Unrecognized option'
            continue
        word = raw_input('Type input: ').lower()
        if cmd == 'e':
            print huffman.encode(language, word)
        elif cmd == 'd':
            print huffman.decode(language, word)

if __name__ == '__main__':
    main()
