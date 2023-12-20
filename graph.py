from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from ui.graph_ui import Ui_MainWindow

import networkx as nx
import matplotlib.pyplot as plt


class Graph(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.alphabet = ['a', 'b']
        self.max_pow = {'a': 2, 'b': 2}
        self.relation = ['ab', 'ba']
        self.elements = []
        self.table = {}

    def relation_slot(self, text):
        self.relation = ['ab', text.lower()]

    def pow_a_slot(self, pow_a):
        self.max_pow['a'] = pow_a

    def pow_b_slot(self, pow_b):
        self.max_pow['b'] = pow_b

    def prepare_relation(self):
        # приведение отношения relation к виду 'ba = a...ab...b' == 'left = right'
        left, right = self.relation
        for ch in self.alphabet:
            left = left.replace(ch * self.max_pow[ch], '')
            right = right.replace(ch * self.max_pow[ch], '')

        if left.index('b'):
            right, left = left, right

        count_b = left.count('b')
        if count_b > 1:
            left = left.replace('b' * count_b, 'b')
            right = 'b' * (self.max_pow['b'] - count_b + 1) + right

            if right.index('b') == 0:
                right = right.replace('ba', right)
                right = right.replace('b' * self.max_pow['b'], '')

        count_a = left.count('a')
        if count_a > 1:
            left = left.replace('a' * count_a, 'a')
            right = right + 'a' * (self.max_pow['a'] - count_a + 1)

            if right.index('a') == 0:
                right = right.replace('ba', right)
                right = right.replace('a' * self.max_pow['a'], '')

        self.relation = [left, right]

    def define_base_elements(self):
        self.elements.clear()
        for i in range(self.max_pow[self.alphabet[1]]):
            for j in range(self.max_pow[self.alphabet[0]]):
                self.elements.append(self.alphabet[0] * j + self.alphabet[1] * i)

        self.elements[0] = 'e'

    def define_table(self):
        """
        построение таблицы умножения
        :return: None
        """
        self.table = {ch: [] for ch in self.alphabet}
        for ch in self.table:
            for base_elem in self.elements:
                elem = base_elem + ch
                while elem not in self.elements:
                    if elem == '':
                        elem = 'e'

                    # remove 'e'
                    elif elem.count('e'):
                        elem = elem.replace('e', '')

                    # swap: ba --> a*...*ab
                    elif elem.count('ba'):
                        elem = elem.replace('ba', self.relation[1])

                    # simplify powers 'a', 'b' with mod
                    else:
                        for ch_ in self.alphabet:
                            elem = elem.replace(ch_ * self.max_pow[ch_], 'e')
                self.table[ch].append(elem)

    def print_info(self):
        print('Alphabet:', *self.alphabet)
        print('Relations:', *[ch * self.max_pow[ch] for ch in self.max_pow],
              ';', self.relation[0], '=', self.relation[1])
        print('Base elements:', *self.elements)
        print('Table:')
        for ch in self.alphabet:
            for i in range(len(self.elements)):
                print(f'\t{self.elements[i]}*{ch} = {self.table[ch][i]}')
            print()

    def show_graph(self):
        plt.clf()

        a_edges = []
        for i in range(len(self.elements)):
            a_edges.append((self.elements[i], self.table['a'][i]))

        b_edges = []
        for i in range(len(self.elements)):
            b_edges.append((self.elements[i], self.table['b'][i]))

        G = nx.DiGraph(a_edges + b_edges)

        edge_labels = dict([((u, v,), '')
                            for u, v, d in G.edges(data=True)])
        red_edges = a_edges
        edge_colors = ['black' if not edge in red_edges else 'red' for edge in G.edges()]

        node_labels = {node: node for node in G.nodes()}

        pos = nx.spring_layout(G)

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(G, pos, labels=node_labels)
        nx.draw(G, pos, node_size=1200, edge_color=edge_colors, edge_cmap=plt.cm.Reds)
        plt.savefig('foo.png')

        pixmap = QPixmap('foo.png')
        self.label_3.clear()
        self.label_3.setPixmap(pixmap)


    def run_slot(self):
        self.prepare_relation()
        self.define_base_elements()
        self.define_table()
        self.show_graph()


if __name__ == '__main__':
    app = QApplication([])
    graph = Graph()
    graph.show()
    app.exec_()
