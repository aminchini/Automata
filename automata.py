import os
import graphviz
import pydot

class NFA:
    def __init__(self, 
                states: list, 
                alphabet: list, 
                num_of_transitions: int, 
                transitions: list, 
                final_states: list):
        self.states = states
        self.alphabet = alphabet
        self.final_states = final_states
        self.nfa = {}
        for i in transitions:
            if i[0] not in self.nfa:
                if len(i[1::]) == 2:
                    self.nfa[i[0]] = [i[1::]]
                else:
                    self.nfa[i[0]] = [i[1::]+['&']]
            else:
                if len(i[1::]) == 2:
                    self.nfa[i[0]].append(i[1::])
                else:
                    self.nfa[i[0]].append(i[1::]+['&'])
        for j in states:
            if j not in self.nfa:
                self.nfa[j] = [['', '']]

    def IsAcceptByNFA(self, word):
        next_nodes = [self.states[0]]
        for i in range(len(word)):
            currrent_nodes = next_nodes
            next_nodes = []
            while len(currrent_nodes) != 0:
                element = currrent_nodes.pop(0)
                for k in self.nfa[element]:
                    if k[1] == word[i]:
                        next_nodes.append(k[0])
                    if k[1] == '&':
                        next_nodes = next_nodes + self._lambda(element, word[i])
            if len(next_nodes) == 0:
                return False
            next_nodes = list(set(next_nodes))
        
        if any([item for item in next_nodes if item in self.final_states]):
            return True
        else:
            for node in next_nodes:
                for destination in self.nfa[node]:
                    if destination[1] == '&' and destination[0] in self.final_states:
                        return True
            return False

    def _lambda(self, c_state, alpha):
        reached_by_lamda = [c_state]
        result = []
        seen = []
        while len(reached_by_lamda) != 0:
            node = reached_by_lamda.pop(0)
            for i in self.nfa[node]:
                if i[1] == alpha:
                    result.append(i[0])
                    seen.append(node)
                if i[1] == '&' and  i[0] not in seen:
                    reached_by_lamda.append(i[0])
                    seen.append(node)
        return result

    def Shape(self):
        g = graphviz.Digraph(format='png')
        g.node('fake', style='invisible')
        
        for nodes in self.nfa.keys():
            if nodes == self.states[0]:
                if nodes in self.final_states:
                    g.node(nodes, root='true',
                       shape='doublecircle')
                else:
                    g.node(nodes, root='true')
            elif nodes in self.final_states:
                g.node(nodes, shape='doublecircle')
            else:
                g.node(nodes)

        g.edge('fake', self.states[0], style='bold')
        for transition in self.nfa.keys():
            for destination in self.nfa[transition]:
                if destination[1] != '':
                    g.edge(transition, destination[0],
                        label=destination[1])

        g.render(filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'NFA'))
        
        

state = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6']
alph = ['a', 'b']
num = 9
tran = [['q0', 'q1','a'], ['q1', 'q1', 'b'], ['q1', 'q2', ], ['q2', 'q3','a'], ['q3', 'q2', 'a'], ['q3', 'q4', 'b'], ['q2', 'q5', 'b'], ['q5', 'q6', 'a'], ['q6', 'q1', 'b']]
final = ['q1', 'q3', 'q6']

nfa = NFA(state, alph, num, tran, final)
print(nfa.IsAcceptByNFA('ab'))
nfa.Shape()



class DFA:
    def __init__(self, 
                states: list, 
                alphabet: list, 
                num_of_transitions: int, 
                transitions: list, 
                final_states: list):

        self.states = states
        self.alphabet = alphabet
        self.dfa = {}
        self.final_states = final_states
        for i in transitions:
            if i[0] not in self.dfa:
                self.dfa[i[0]] = [i[1::]]
            else:
                self.dfa[i[0]].append(i[1::])


    def IsAcceptByDFA(self, word):
        currrent_state = self.states[0]
        for i in word:
            acceptance = False
            for j in self.dfa[currrent_state]:
                if j[1] == i:
                    acceptance = True
                    currrent_state = j[0]
                    break
            if not acceptance:
                return False
        if acceptance and currrent_state in self.final_states:
            return True
        else:
            return False
            
    def Shape(self):
        g = graphviz.Digraph(format='png')
        g.node('fake', style='invisible')
        
        for nodes in self.dfa.keys():
            if nodes == self.states[0]:
                if nodes in self.final_states:
                    g.node(nodes, root='true',
                       shape='doublecircle')
                else:
                    g.node(nodes, root='true')
            elif nodes in self.final_states:
                g.node(nodes, shape='doublecircle')
            else:
                g.node(nodes)
        
        g.edge('fake', self.states[0], style='bold')
        for transition in self.dfa.keys():
            for destination in self.dfa[transition]:
                if destination[1] != '':
                    g.edge(transition, destination[0],
                        label=destination[1])

        g.render(filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'DFA'))


d_state = ['q0', 'q1', 'q2']
d_alph = ['a', 'b']
d_num = 6
d_tran = [['q0', 'q1','a'], ['q1', 'q1', 'a'], ['q1', 'q1', 'b'], ['q0', 'q2', 'b'], ['q2', 'q2','a'], ['q2', 'q2', 'b']]
d_final = ['q1']

dfa = DFA(d_state, d_alph, d_num, d_tran, d_final)
print(dfa.IsAcceptByDFA('baabaab'))
dfa.Shape()