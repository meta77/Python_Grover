from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt

# --- パラメータ設定 ---
n = 3  # 量子ビット数（N=8）　 探索空間は8個の状態：000〜111
target_state = '101'  # 正解、つまり、探索対象のビット列

# --- ① 初期化（全ビットにHadamard） ---
qc = QuantumCircuit(n, n)
qc.h(range(n))

# 状態ベクトルを可視化（初期化後）
sv = Statevector.from_instruction(qc)
print("初期状態ベクトル（全状態が等確率の重ね合わせ）:")
display(sv.draw(output='text'))

# --- ② オラクル（target_stateに位相反転） ---
oracle = QuantumCircuit(n)
for i, bit in enumerate(reversed(target_state)):
    if bit == '0':
        oracle.x(i)
oracle.h(n-1)
oracle.mcx(list(range(n-1)), n-1)  # 多制御NOT
oracle.h(n-1)
for i, bit in enumerate(reversed(target_state)):
    if bit == '0':
        oracle.x(i)
oracle.name = "Oracle"
qc.append(oracle.to_gate(), range(n))

# --- ③ ディフューザー（反転増幅） ---
diffuser = QuantumCircuit(n)
diffuser.h(range(n))
diffuser.x(range(n))
diffuser.h(n-1)
diffuser.mcx(list(range(n-1)), n-1)
diffuser.h(n-1)
diffuser.x(range(n))
diffuser.h(range(n))
diffuser.name = "Diffuser"
qc.append(diffuser.to_gate(), range(n))

# --- ④ 測定 ---
qc.measure(range(n), range(n))

# --- ⑤ 実行 ---
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
counts = job.result().get_counts()

# --- ⑥ 結果表示 ---
print(f"\n探索対象: {target_state}")
plot_histogram(counts)
plt.title("グローバーのアルゴリズム実行結果")
plt.show()

# --- 解説 ---
print("✅ グローバーのアルゴリズムにより、探索対象である状態（ここでは '101'）の出現頻度が最も高くなります。")
print("✅ 状態空間が非構造であっても、量子干渉によって効率的に探索が可能です。")
