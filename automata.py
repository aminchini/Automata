import os
import copy
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


    def FindRegex (self):
        the_nfa = {}
        temp_nfa = copy.deepcopy(self.nfa)
        temp_nfa['s'] = [[self.states[0], '&']]
        temp_nfa['f'] = [['', '']]
        for finals in self.final_states:
            temp_nfa[finals].append(['f', '&'])
        for key in temp_nfa.keys():
            transition = {}
            transition['out'] = temp_nfa[key]
            _in = []
            for item in temp_nfa.keys():
                for eleman in temp_nfa[item]:
                    if eleman[0] == key:
                        _in.append([item, eleman[1]])
            transition['in'] = _in
            the_nfa[key] = transition

        def exmaker(state, entry, out):
            loops = []
            for en in the_nfa[state]['in']:
                for o in the_nfa[state]['out']:
                    if en == o:
                        loops.append(en[1])
            if entry[0] == out[0]:
                loops.append(out[1]+entry[1])
            
            loop = ''
            if len(loops) == 1:
                loop = '(' + loops[0] + ')*'
            elif len(loops) > 1 :
                loop = '(' + '+'.join(list(set(loops))) + ')*'
            
            res = ''
            if entry[1] == '&' and out[1] != '&':
                res = loop + out[1]
            elif out[1] == '&' and entry[1] != '&':
                res = entry[1] + loop
            elif entry[1] == '&' and out[1] == '&':
                if loop != '':
                    res = loop
                else:
                    res = '&'
            else:
                res = entry[1] + loop + out[1]
            return res
        
        the_state = []
        for s in self.states:
            if s not in self.final_states:
                the_state.append(s)
        the_state += self.final_states
        
        for state in the_state:
            state_info = the_nfa[state]
            deleted = False
            for entry in state_info['in']:
                if entry in state_info['out']:
                    continue
                for o in the_nfa[entry[0]]['out']:
                    if o[0] == state:
                        index = the_nfa[entry[0]]['out'].remove(o)
                for out in state_info['out']:
                    if out in state_info['in']:
                        continue
                    if out == ['', '']:
                        continue
                    exp = exmaker(state, entry, out)
                    the_nfa[entry[0]]['out'].append([out[0], exp])
                    for en in the_nfa[out[0]]['in']:
                        if en[0] == state:
                            index = the_nfa[out[0]]['in'].index(en)
                            the_nfa[out[0]]['in'][index] = [entry[0], exp]
                            deleted = True
                    if deleted:
                        the_nfa[out[0]]['in'].append([entry[0], exp])

        return ' + '.join(list(set([i[1] for i in the_nfa['s']['out']])))


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
        dfa_states.append('trap')

        return [dfa_states, dfa_alphabet, len(dfa_transitions), dfa_transitions, dfa_final_states]


    def Shape(self, name):
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

        g.render(filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), name))

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
        non_final = []
        for state in self.states:
            if state not in self.final_states:
                non_final.append(state)

        reachables = {self.states[0]}
        temp_reach = [self.states[0]]
        while temp_reach:
            reachable = temp_reach.pop(0)
            for item in self.dfa[reachable]:
                if item[0] not in reachables:
                    reachables.add(item[0])
                    temp_reach.append(item[0])

        current_groups = {  'g1': list(reachables.intersection(set(non_final))),
                            'g2': list(reachables.intersection(set(self.final_states))) }
        trans = {}
        for states in current_groups['g1'] + current_groups['g2']:
            trans[states] = []
            for des in self.dfa[states]:
                index = self.alphabet.index(des[1])
                trans[states].insert(index, des[0])

        
        while True:
            next_groups = {}
            for nodes in trans.keys():
                name  = ''
                for node in trans[nodes]:
                    for g in current_groups.keys():
                        if node in current_groups[g]:
                            name += g
                if name not in next_groups.keys():
                    next_groups[name] = [nodes]
                else:
                    next_groups[name].append(nodes)
            curr_val = list(current_groups.values())
            nex_val = list(next_groups.values())
            if curr_val == nex_val:
                break
            current_groups = next_groups
        
        res_nodes = {}
        res_states = []
        state_group = {}
        res_final = set()
        g = 1
        for val in current_groups.values():
            res_nodes['g'+str(g)] = val
            if self.states[0] in val:
                res_states.insert(0, 'g'+str(g))
            else:
                res_states.append('g'+str(g))
            for value in val:
                state_group[value] = 'g'+str(g)
                if value in self.final_states:
                    res_final.add('g'+str(g))
            g += 1

        res_trans = []
        for key in res_nodes.keys():
            for nod in trans.keys():
                if nod == res_nodes[key][0]:
                    c = 0
                    for a in self.alphabet:
                        res_trans.append([key, state_group[trans[nod][c]], a])
                        c += 1

        return [res_states, self.alphabet, len(res_trans), res_trans, list(res_final)]


    def Shape(self, name):
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

        g.render(filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), name))

        
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

print(nfa.FindRegex())

nfa.Shape('the_NFA')

result_dfa = nfa.CreateEqeulvantDFA()
dfa_of_nfa = DFA(result_dfa[0], result_dfa[1], result_dfa[2], result_dfa[3], result_dfa[4])
dfa_of_nfa.Shape('DFA_of_NFA')

print(dfa_of_nfa.IsAcceptByDFA(''))
print(dfa_of_nfa.IsAcceptByDFA('abb'))
print(dfa_of_nfa.IsAcceptByDFA('abaa'))
print(dfa_of_nfa.IsAcceptByDFA('abab'))

simple = dfa_of_nfa.MakeSimpleDFA()
sim_of_dfa = DFA(simple[0], simple[1], simple[2], simple[3], simple[4])
sim_of_dfa.Shape('Simple_DFA')

"""Create another DFA separately"""

d_state = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5']
d_alph = ['a', 'b']
d_num = 12
d_tran = [  ['q0', 'q1', 'a'],
            ['q1', 'q0', 'a'], 
            ['q1', 'q3', 'b'], 
            ['q0', 'q3', 'b'], 
            ['q2', 'q1', 'a'], 
            ['q2', 'q4', 'b'],
            ['q4', 'q3', 'a'], 
            ['q4', 'q3', 'b'], 
            ['q3', 'q5', 'a'], 
            ['q3', 'q5', 'b'], 
            ['q5', 'q5', 'a'],
            ['q5', 'q5', 'b']]

d_final = ['q3', 'q5']

# dfa = DFA(d_state, d_alph, d_num, d_tran, d_final)

# print(dfa.IsAcceptByDFA('aabaab'))

# sm = dfa.MakeSimpleDFA()
# sm_of_dfa = DFA(sm[0], sm[1], sm[2], sm[3], sm[4])
# sm_of_dfa.Shape()

# dfa.Shape()

"""Another NFA"""

n_state = ['q0', 'q1', 'q2', 'q3']
n_alph = ['a', 'b']
n_num = 6
n_tran = [  ['q0', 'q1', 'a'],
            ['q1', 'q2',],
            ['q2', 'q0',],
            ['q2', 'q3', 'b'],
            ['q3', 'q2', 'a'],
            ['q3', 'q3', 'a']   ]
n_final = ['q3']

# n_nfa = NFA(n_state, n_alph, n_num, n_tran, n_final)
# n_nfa.FindRegex()
# n_dfa = n_nfa.CreateEqeulvantDFA()
# n_dfa_of_nfa = DFA(n_dfa[0], n_dfa[1], n_dfa[2], n_dfa[3], n_dfa[4])
# n_dfa_of_nfa.Shape()