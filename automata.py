import os
import graphviz

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


    def CreateEqeulvantDFA(self):
        initial_state = self.states[0]

        def name_state(name):
            return str(set(sorted(name)))

        dfa_alphabet = self.alphabet
        dfa_states = [name_state([initial_state])]
        dfa_transitions = []
        dfa_final_states = []

        
        temp_states = [[initial_state]]
        next_nodes = [[initial_state]]

        while next_nodes:
            current_nodes = next_nodes.pop(0)
            for a in dfa_alphabet:
                next_set = self._next_available_nodes(current_nodes, a)
                if len(next_set) == 0:
                    continue
                if next_set not in temp_states:
                    temp_states.append(next_set)
                    next_nodes.append(next_set)
                    dfa_states.append(name_state(next_set))
                    if any([item for item in next_set if item in self.final_states]):
                        dfa_final_states.append(name_state(next_set))
                dfa_transitions.append([name_state(current_nodes), name_state(next_set), a])

        #create trap state
        temp = {}
        for trans in dfa_transitions:
            if trans[0] not in temp:
                temp[trans[0]] = [trans[1::]]
            else:
                temp[trans[0]].append(trans[1::])
        for tmp in dfa_states:
            if tmp not in temp.keys():
                for the_alphabets in self.alphabet:
                    dfa_transitions.append([tmp, 'trap', the_alphabets])
            elif (len(temp[tmp]) < len(self.alphabet)):
                temp_alphabet = self.alphabet.copy()
                for used_alphabet in temp[tmp]:
                    temp_alphabet.remove(used_alphabet[1])
                for new_alphabet in temp_alphabet:
                    dfa_transitions.append([tmp, 'trap', new_alphabet])
        for alphab in self.alphabet:
            dfa_transitions.append(['trap', 'trap', alphab])

        return [dfa_states, dfa_alphabet, len(dfa_transitions), dfa_transitions, dfa_final_states]


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

    def _next_available_nodes(self, current_nodes, alpha):
        result = set()
        for current_node in current_nodes:
            for des in self.nfa[current_node]:
                if des[1] == alpha:
                    result.add(des[0])
                    next_lambda = [i for i in self.nfa[des[0]] if i[1] == '&']
                    while next_lambda:
                        items = next_lambda.pop(0)
                        result.add(items[0])
                        next_lambda += [i for i in self.nfa[items[0]] if i[1] == '&']
                elif des[1] == '&':
                    for reachables in self._lambda(current_node, alpha):
                        result.add(reachables)
                    next_lambda = [i for i in self.nfa[des[0]] if i[1] == '&']
                    while next_lambda:
                        items = next_lambda.pop(0)
                        result.add(items[0])
                        next_lambda += [i for i in self.nfa[items[0]] if i[1] == '&']
        return result

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
        if len(word) == 0:
            if self.states[0] in self.final_states:
                return True
            else:
                return False
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


    def MakeSimpleDFA(self):
        pass


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

        
"""create NFA"""

state = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6']
alph = ['a', 'b']
num = 9
tran = [['q0', 'q1', 'a'], 
        ['q1', 'q1', 'b'], 
        ['q1', 'q2', ], 
        ['q2', 'q3', 'a'], 
        ['q3', 'q2', 'a'], 
        ['q3', 'q4', 'b'], 
        ['q2', 'q5', 'b'], 
        ['q5', 'q6', 'a'], 
        ['q6', 'q1', 'b']]

final = ['q1', 'q3', 'q6']

nfa = NFA(state, alph, num, tran, final)

print(nfa.IsAcceptByNFA(''))
print(nfa.IsAcceptByNFA('abb'))
print(nfa.IsAcceptByNFA('abaa'))
print(nfa.IsAcceptByNFA('abab'))

# nfa.Shape()

result_dfa = nfa.CreateEqeulvantDFA()
dfa_of_nfa = DFA(result_dfa[0], result_dfa[1], result_dfa[2], result_dfa[3], result_dfa[4])

print(dfa_of_nfa.IsAcceptByDFA(''))
print(dfa_of_nfa.IsAcceptByDFA('abb'))
print(dfa_of_nfa.IsAcceptByDFA('abaa'))
print(dfa_of_nfa.IsAcceptByDFA('abab'))

# dfa_of_nfa.Shape()

"""create DFA separately"""

d_state = ['q0', 'q1', 'q2']
d_alph = ['a', 'b']
d_num = 6
d_tran = [  ['q0', 'q1', 'a'],
            ['q1', 'q1', 'a'], 
            ['q1', 'q1', 'b'], 
            ['q0', 'q2', 'b'], 
            ['q2', 'q2', 'a'], 
            ['q2', 'q2', 'b']]

d_final = ['q1']

# dfa = DFA(d_state, d_alph, d_num, d_tran, d_final)
# print(dfa.IsAcceptByDFA('baabaab'))
# dfa.Shape()