import numpy as np
import pennylane as qml

def generate_bits_and_bases(n):
    """Generate random bits and bases for Alice and Bob."""
    alice_bits = np.random.randint(2, size=n)
    alice_bases = np.random.randint(2, size=n)  # 0 = Z-basis, 1 = X-basis
    bob_bases = np.random.randint(2, size=n)
    return alice_bits, alice_bases, bob_bases

def simulate_bb84(alice_bits, alice_bases, bob_bases, with_eve=False, noise_prob=None, draw_circuit=True):
    """Simulate BB84 quantum transmission, optionally with Eve's interception and a depolarizing noise channel.
    
    Parameters:
      draw_circuit (bool): If True, draw the circuit for the first qubit of this simulation.
    """
    n = len(alice_bits)
    bob_bits = []
    
    if with_eve:
        eve_bases = np.random.randint(2, size=n)
    else:
        eve_bases = None
    
    for i in range(n):
        num_wires = 2 if with_eve else 1
        dev = qml.device("default.mixed", wires=num_wires, shots=1)
        
        @qml.qnode(dev)
        def bb84_circuit():
            if with_eve:
                # Alice prepares the qubit on wire 0
                if alice_bits[i] == 1:
                    qml.PauliX(wires=0)
                if alice_bases[i] == 1:
                    qml.Hadamard(wires=0)
                
                # Eve intercepts and measures in her basis.
                # Apply Hadamard on wire 0 only if Eve's basis is 1 and Alice's basis is 0, cuz H+H = I.
                if eve_bases[i] == 1 and alice_bases[i] == 0:
                    qml.Hadamard(wires=0)
                eve_measurement = qml.measure(wires=0)
                
                # Eve prepares a new qubit on wire 1 based on her measurement.
                qml.cond(eve_measurement == 1, qml.PauliX)(wires=1)
                if eve_bases[i] == 1:
                    qml.Hadamard(wires=1)  # Prepare in X-basis if measured in X
                
                # Noisy Channel Simulation
                if noise_prob is not None:
                    qml.PhaseFlip(noise_prob, wires=0)
                
                # Bob measures on wire 1 in his chosen basis
                if bob_bases[i] == 1:
                    qml.Hadamard(wires=1)
                return qml.sample(wires=1)
            else:
                # No Eve: Alice sends her qubits to Bob directly over wire 0.
                if alice_bits[i] == 1:
                    qml.PauliX(wires=0)
                if alice_bases[i] == 1:
                    qml.Hadamard(wires=0)
                
                # Noisy Channel Simulation
                if noise_prob is not None:
                    qml.PhaseFlip(noise_prob, wires=0)
                
                if bob_bases[i] == 1:
                    qml.Hadamard(wires=0)
                return qml.sample(wires=0)
        
        # Draw and print the circuit for the first qubit only if requested.
        if draw_circuit and i == 0:
            circuit_diagram = qml.draw(bb84_circuit)()
            if with_eve:
                print(f"\n\nQuantum Circuit (with_eve={with_eve}) for the first qubit "
                      f"(Alice's bit = {alice_bits[i]}, Alice's base = {alice_bases[i]}, Eve's base = {eve_bases[i]}, Bob's base = {bob_bases[i]}):\n")
            else:
                print(f"\n\nQuantum Circuit (with_eve={with_eve}) for the first qubit "
                      f"(Alice's bit = {alice_bits[i]}, Alice's base = {alice_bases[i]}, Bob's base = {bob_bases[i]}):\n")
            print(circuit_diagram)
        
        # Execute the circuit and append Bob's measurement outcome.
        bob_bits.append(int(bb84_circuit().item()))
    
    return bob_bits

def sift_keys(alice_bases, bob_bases, alice_bits, bob_bits):
    """Sift keys by matching measurement bases."""
    matched_indices = [i for i in range(len(alice_bases)) if alice_bases[i] == bob_bases[i]]
    return ([alice_bits[i] for i in matched_indices],
            [bob_bits[i] for i in matched_indices])