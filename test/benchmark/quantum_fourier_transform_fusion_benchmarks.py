import math, itertools
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler import assemble, transpile
from qiskit.providers.aer import QasmSimulator

def qft_circuit(num_qubit, use_cu1):
    qreg = QuantumRegister(num_qubit,"q")
    creg = ClassicalRegister(num_qubit, "c")
    circuit = QuantumCircuit(qreg, creg)

    for i in range(num_qubit):
        circuit.h(qreg[i])

    for i in range(num_qubit):
        for j in range(i):
            l = math.pi/float(2**(i-j))
            if use_cu1:
                circuit.cu1(l, qreg[i], qreg[j])
            else:
                circuit.u1(l/2, qreg[i])
                circuit.cx(qreg[i], qreg[j])
                circuit.u1(-l/2, qreg[j])
                circuit.cx(qreg[i], qreg[j])
                circuit.u1(l/2, qreg[j])
        circuit.h(qreg[i])

    circuit.barrier()
    for i in range(num_qubit):
        circuit.measure(q[i], c[i])
    self.qft_circuits.append(qobj)

    return circuit

class QuantumFourierTransformFusionSuite:
    def __init__(self):
        self.timeout = 60 * 20
        self.qft_circuits = []
        self.backend = QasmSimulator()
        num_qubits = [5, 10, 15, 20, 25, 26]

        for num_qubit in num_qubits:
            for use_cu1 in [True, False]:
                circuit = qft_circuit(num_qubit, use_cu1)
                self.circuit[(num_qubit, use_cu1)] = assemble(circuit, self.backend, shots=1)
        self.param_names = ["Quantum Fourier Transform", "Fusion Activated", "Use cu1 gate"]
        self.params = (num_qubits, [True, False], [True, False])

    def setup(self, num_qubit, fusion_enable, use_cu1):
        """ Setup env before benchmarks start """

    def time_quantum_fourier_transform(self, num_qubit, fusion_enable, use_cu1):
        """ Benchmark QFT """
        result = self.backend.run(self.circuit[(num_qubit, use_cu1)], backend_options={'fusion_enable': fusion_enable}).result()
        if result.status != 'COMPLETED':
            raise QiskitError("Simulation failed. Status: " + result.status)