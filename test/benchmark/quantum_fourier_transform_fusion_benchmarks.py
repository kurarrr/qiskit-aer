import math
import sys
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler import assemble, transpile
from qiskit.providers.aer import QasmSimulator

def qft(qreg, circuit):
    n = len(qreg)
    for i in range(n):
        circuit.h(qreg[i])

    for i in range(n):
        for j in range(i):
            l = math.pi/float(2**(i-j))
            circuit.u1(l/2, qreg[i])
            circuit.cx(qreg[i], qreg[j])
            circuit.u1(-l/2, qreg[j])
            circuit.cx(qreg[i], qreg[j])
            circuit.u1(l/2, qreg[j])
        circuit.h(qreg[i])

    return circuit

class QuantumFourierTransformFusionSuite:
    def __init__(self):
        self.timeout = 60 * 20
        self.qft_circuits = []
        self.backend = QasmSimulator()
        for num_qubits in (5, 10, 15, 20):
            q = QuantumRegister(num_qubits,"q")
            c = ClassicalRegister(num_qubits, "c")
            circ = qft(q, QuantumCircuit(q, c, name="qft"))
            circ.barrier()
            for i in range(num_qubits):
                circ.measure(q[i], c[i])
            qobj = assemble(circ)
            self.qft_circuits.append(qobj)

        self.param_names = ["Quantum Fourier Transform", "Fusion Activated"]
        self.params = (self.qft_circuits, [True, False])

    def setup(self, qobj, fusion_enable):
        """ Setup env before benchmarks start """

    def time_quantum_fourier_transform(self, qobj, fusion_enable):
        """ Benchmark QFT """
        result = self.backend.run(qobj, backend_options={'fusion_enable': fusion_enable}).result()
        if result.status != 'COMPLETED':
            raise QiskitError("Simulation failed. Status: " + result.status)