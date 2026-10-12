"""Exact four-qubit statevector simulation and a quantum fidelity kernel.

This is a quantum-kernel method executed on a classical CPU, not quantum
hardware. NumPy explicitly simulates RY, RZ and CNOT unitary gates. No quantum
speedup is claimed. A classical SVM learns from the quantum kernel matrix.
"""
import numpy as np

QUBITS = 4


def single_qubit_gate(state, gate, wire, qubits=QUBITS):
    tensor = np.moveaxis(state.reshape((2,) * qubits), wire, 0)
    updated = (gate @ tensor.reshape(2, -1)).reshape(tensor.shape)
    return np.moveaxis(updated, 0, wire).reshape(-1)


def cnot(state, control, target, qubits=QUBITS):
    # Wire zero is the most significant bit in the computational basis.
    indexes = np.arange(2 ** qubits)
    mask = (indexes >> (qubits - 1 - control)) & 1
    destination = indexes ^ (mask << (qubits - 1 - target))
    result = np.empty_like(state)
    result[destination] = state
    return result


def feature_state(angles):
    angles = np.asarray(angles, dtype=float)
    if angles.shape != (QUBITS,) or not np.isfinite(angles).all():
        raise ValueError('The circuit requires four finite angles.')
    state = np.zeros(2 ** QUBITS, dtype=complex)
    state[0] = 1.0
    for _ in range(2):
        for wire, angle in enumerate(angles):
            c, s = np.cos(angle / 2), np.sin(angle / 2)
            state = single_qubit_gate(state, np.array([[c, -s], [s, c]]), wire)
            rz = np.diag([np.exp(-0.5j * angle), np.exp(0.5j * angle)])
            state = single_qubit_gate(state, rz, wire)
        for control, target in ((0, 1), (1, 2), (2, 3)):
            state = cnot(state, control, target)
    return state


def states_for(angles):
    return np.stack([feature_state(row) for row in angles])


def fidelity_kernel(left_states, right_states):
    """K(x,z) = |<phi(x)|phi(z)>|^2, an exact noiseless fidelity."""
    return np.clip(np.abs(left_states.conj() @ right_states.T) ** 2, 0, 1)
