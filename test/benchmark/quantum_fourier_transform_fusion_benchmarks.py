import time
import math
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler import assemble, transpile
from qiskit.providers.aer import QasmSimulator
def qft(qreg, circuit):
    n = len(qreg)
    for i in range(n):
        circuit.h(qreg[i])
    for i in range(n):
        for j in range(i):
            circuit.cu1(math.pi/float(2**(i-j)), qreg[i], qreg[j])
        circuit.h(qreg[i])
    return circuit
qubit = 20
backend = QasmSimulator()
print ('app,qubit,time')
backend_options = {}
backend_options['fusion_enable'] = True
q = QuantumRegister(qubit,"q")
c = ClassicalRegister(qubit, "c")
circ = qft(q, QuantumCircuit(q, c, name="qft"))
circ.barrier()
for i in range(qubit):
    circ.measure(q[i], c[i])
qobj = assemble(circ)
start_simulation = time.time()
backend.run(qobj, backend_options=backend_options).result()
end_simulation = time.time()
print ('qft,{qubit},{simulation}'.format(
    qubit=qubit, 
    simulation=(end_simulation - start_simulation)))