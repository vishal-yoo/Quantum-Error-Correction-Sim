import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def get_success_rate(is_protected, error_prob, manual_target=None):
    shots = 1000
    simulator = AerSimulator()

    if not is_protected:
        qc = QuantumCircuit(1, 1)
        if np.random.rand() < error_prob:
            qc.x(0)
        qc.measure(0, 0)
    else:
        qc = QuantumCircuit(5, 3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(0, 2)

        if manual_target is not None:
            qc.x(manual_target)
        elif np.random.rand() < error_prob:
            err_idx = np.random.randint(0, 3)
            qc.x(err_idx)

        qc.cx(0, 3)
        qc.cx(1, 3)
        qc.cx(1, 4)
        qc.cx(2, 4)

        qc.ccx(3, 4, 1)
        qc.measure([0, 1, 2], [0, 1, 2])

    t_qc = transpile(qc, simulator)
    counts = simulator.run(t_qc, shots=shots).result().get_counts()

    successes = counts.get('000', 0) + counts.get('111', 0) + counts.get('0', 0)
    return (successes / shots) * 100

print("--- Manual Stress Test Mode ---")
choice = int(input("Which qubit do you want to break to test the decoder? (0, 1, or 2): "))
test_run = get_success_rate(is_protected=True, error_prob=1.0, manual_target=choice)
print(f"Result: Qubit {choice} was broken, but the system recovered with {test_run}% accuracy.")
print("\n--- Generating Automated Comparison Graph ---")

probs = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
unprotected_results = [get_success_rate(False, p) for p in probs]
protected_results = [get_success_rate(True, p) for p in probs]

plt.plot(probs, unprotected_results, 'r--', label='Unprotected (1 Qubit)')
plt.plot(probs, protected_results, 'g-', label='Protected (Your Code)')
plt.xlabel('Error Probability')
plt.ylabel('Success Rate (%)')
plt.title('Comparison: How Much Better is Your Error Correction?')
plt.legend()
plt.grid(True)
plt.show()
