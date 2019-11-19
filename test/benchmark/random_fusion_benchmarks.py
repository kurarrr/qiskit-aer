from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler import assemble, transpile
from qiskit.providers.aer import QasmSimulator
from qiskit.quantum_info import random
from qiskit.quantum_info.synthesis import two_qubit_cnot_decompose
import numpy as np
import sys


def build_model_circuit_kak(width, depth, seed=None):
    """Create quantum volume model circuit on quantum register qreg of given
    depth (default depth is equal to width) and random seed.
    The model circuits consist of layers of Haar random
    elements of U(4) applied between corresponding pairs
    of qubits in a random bipartition.
    """
    qreg = QuantumRegister(width)
    depth = depth or width

    np.random.seed(seed)
    circuit = QuantumCircuit(qreg, name="Qvolume: %s by %s, seed: %s" % (width, depth, seed))

    for _ in range(depth):
        # Generate uniformly random permutation Pj of [0...n-1]
        perm = np.random.permutation(width)

        # For each pair p in Pj, generate Haar random U(4)
        # Decompose each U(4) into CNOT + SU(2)
        for k in range(width // 2):
            U = random.random_unitary(4, seed).data
            for gate in two_qubit_cnot_decompose(U):
                qs = [qreg[int(perm[2 * k + i.index])] for i in gate[1]]
                pars = gate[0].params
                name = gate[0].name
                if name == "cx":
                    circuit.cx(qs[0], qs[1])
                elif name == "u1":
                    circuit.u1(pars[0], qs[0])
                elif name == "u2":
                    circuit.u2(*pars[:2], qs[0])
                elif name == "u3":
                    circuit.u3(*pars[:3], qs[0])
                elif name == "id":
                    pass  # do nothing
                else:
                    raise Exception("Unexpected gate name: %s" % name)
    return circuit


class RandomFusionSuite:
    def __init__(self):
        self.timeout = 60 * 20
        self.qft_circuits = []
        self.backend = QasmSimulator()
        for num_qubits in (5, 10, 15, 20, 25):
            circ = build_model_circuit_kak(num_qubits, num_qubits, 1)
            qobj = assemble(circ)
            self.qft_circuits.append(qobj)

        self.param_names = ["Random Circuit", "Fusion Activated"]
        self.params = (self.qft_circuits, [True, False])

    def setup(self, qobj, fusion_enable):
        """ Setup env before benchmarks start """

    def time_random_transform(self, qobj, fusion_enable):
        result = self.backend.run(qobj, backend_options={'fusion_enable': fusion_enable}).result()
        if result.status != 'COMPLETED':
            raise QiskitError("Simulation failed. Status: " + result.status)