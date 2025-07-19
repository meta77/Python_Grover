from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt

# --- パラメータ設定 ---
n = 3  # 今回は量子ビット数3。このとき、探索空間は8個の状態：000〜111
target_state = '101'  # 正解、つまり、探索対象のビット列



# --- ① 初期化（全ビットにHadamard） ---
qc = QuantumCircuit(n, n) # 3量子ビットの量子回路を定義し、それぞれの量子ビットの測定結果を保存するために、3つの古典ビットも用意している。
qc.h(range(n)) # 量子回路 qc において、0番から n-1 番までのすべての量子ビットにHadamardゲートを適用する。
'''
 for i in range(n):
    qc.h(i)
と同じ意味。
'''

# 状態ベクトルを可視化（初期化後）
sv = Statevector.from_instruction(qc) # 量子回路 qc を理想的に実行したときに得られる量子状態（複素数のベクトル）を計算して、それを sv に保存する
print("初期状態ベクトル（全状態が等確率の重ね合わせ）:")
display(sv.draw(output='text'))





# --- ② オラクル（target_stateのみ位相反転） ---
# グローバーのアルゴリズムでは、探索対象である状態（たとえば '101'）だけに−1をかける（＝位相を反転）して、
# その後の処理でその状態の確率振幅を「増幅」する。

oracle = QuantumCircuit(n) # 新しい量子回路oracleを定義 「正解にだけ反応する関数」 を構築する回路。

# 正解ビット列 '101' を 一時的に |111⟩ に変換する。
# 実用とは違い、あらかじめ正解を知っているという前提で回路を作る。
for i, bit in enumerate(reversed(target_state)):
    if bit == '0':
        oracle.x(i)


# 指定した状態（正解）にだけ -1 の位相を与える
oracle.h(n-1)
oracle.mcx(list(range(n-1)), n-1)  # 多制御NOT
oracle.h(n-1)

# 再度 Xゲート で元に戻す
for i, bit in enumerate(reversed(target_state)):
    if bit == '0':
        oracle.x(i)





# 回路に名前をつけて、メインの回路 qc に「ゲート化して挿入」
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
