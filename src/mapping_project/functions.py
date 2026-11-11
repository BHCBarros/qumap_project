import numpy as np
import qiskit as qk
import qiskit.circuit as qkc
import qiskit.primitives as qkp
import qiskit.quantum_info as qki
import scipy as sci


def front_layer(DAG,gate_list):
    # This function outputs the front layer of the DAG, which are the gates with no predecessor. In the DAG matrix this is clear because they'll be columns with nothing but zeroes in it, which can be checked by adding up its respective values. It will return the front layer as well as an updated DAG and gate list without the selected gates.
    indices=[]
    new_gate_list=[]
    F=[]
    for i in range(DAG.shape[0]):
        if DAG[:,i].sum() == 0:
            F.append(gate_list[i])
        else:
            indices.append(i)
            new_gate_list.append(gate_list[i])
    return (tuple(F),DAG[indices,indices],new_gate_list)

def DAG_generate(qc):
    # This function generates a Directed Acyclic Graph for the quantum circuit qc. It'll be a matrix with all 2 qubit gates in the circuit with whether or not they connect. ij=i->j (i connects and predecesses j). It is a matrix containing only zeroes and ones. All elements in the main diagonal are zero.
    # It returns the graph and a list containing the gate operations that represent each row of the graph.
    gate_list=mqu_gatelist(qc)
    DAG=np.zeros((len(gate_list),len(gate_list)),dtype=int)
    for i in range(len(gate_list)):
        gates=find_predecessors(gate_list,gate_list[-i-1])
        for gate in gates:
            DAG[gate[0],-i-1]=1
    return (DAG,gate_list)

def find_predecessors(gate_list,index):
    gate=gate_list[index][1]
    n=len(gate_list)-index
    gates_per_qubit={key:False for key in gate.qubits}
    for qubit in gate.qubits:
        if False not in gates_per_qubit.values():
            break
        for i in range(1,index+1):
            if qubit in gate_list[-n-i][1].qubits:
                gates_per_qubit[qubit]=gate_list[-n-i][1]
                break
    return tuple(set([value for value in gates_per_qubit.values() if value != False]))

def mqu_gatelist(qc):
    # This function generates a list of all multiqubit gates a quantum circuit has, dropping all single qubit gates
    return tuple([(i,qc.data[i]) for i in range(len(qc.data)) if qc.data[i] > 1])

'''
# The idea I had for finding the DAG before I came up with the code above. Included as history only. To be removed after release of stable version.
def gate_per_qubit(qc):
    # This function receives a quantum circuit and returns a dictionary containing as keys every qubit in the circuit and as values a list of all multiqubit gates applied to that qubit in the order they appear. It will combine all single qbit gates into the next multiqubit gate it finds.
    inst_orderdict={key: [] for key in qc.qubits}
    for instruction in qc.data:
        qubits=instruction.qubits
        for qubit in qubits:
            inst_orderdict[qubit].append(instruction)
    gate_orderdict={key: [] for key in qc.qubits}
    final_gate_orderdict={key: [] for key in qc.qubits}
    for qubit in inst_orderdict.keys:
        inst_not_1=None
        previous_inst_not_1=0
        for i,instruction in enumerate(inst_orderdict[qubit]):
            if len(instruction.qubits) != 1:
                inst_not_1=i
                if inst_orderdict[qubit][previous_inst_not_1+1:inst_not_1] != []:
                    new_inst=merge_instructions(qc.qregs,*inst_orderdict[qubit][previous_inst_not_1+1:inst_not_1])
                    gate_orderdict[qubit].extend([new_inst,instruction])
                else:
                    gate_orderdict[qubit].append(instruction)
                previous_inst_not_1=inst_not_1
    for qubit in gate_orderdict.keys:
        for i,instruction in enumerate(gate_orderdict[qubit]):
            if len(instruction.qubits) != 1:
                one_qubit_insts=_list_comprehend(gate_orderdict,instruction)
                new_inst2=merge_instructions(qc.qregs,*one_qubit_insts.append(instruction))
                final_gate_orderdict[qubit].append(new_inst2)
    return final_gate_orderdict

def merge_instructions(reg,*insts):
    # This function merges the instructions in insts into one instruction. All instructions must come from the same quantum circuit.
    qc=qkc.QuantumCircuit(reg)
    for inst in insts:
        qc.append(inst.operation,inst.qubits)
    return qc.to_instruction()

def get_inst_index(inst_list,inst):
    for i in range(len(inst_list)):
        if id(inst_list[i]) == id(inst):
            break
    return i

def _list_comprehend(gates_dict,instruction):
    # performs the following list comprehension:
    # [gate_orderdict[bit][get_instruction(gate_orderdict[bit],instruction)-1] for bit in gate_orderdict.keys if ((len(gate_orderdict[bit][get_instruction(gate_orderdict[bit],instruction)-1].qubits) == 1) and (gate_orderdict[bit],instruction)-1 >= 0))]
    # Since this was very large to write down, I decided it deserved its own function.
    ret=[]
    for key in gates_dict.keys:
        i=get_inst_index(gates_dict[key],instruction)-1
        if i >= 0 and len(gates_dict[key][i]) == 1: # Keep conditions in this order!!!!
                ret.append(gates_dict[key][i])
    return ret
'''