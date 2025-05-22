from compiler import get_compiler
from backend import get_spinq_cloud
comp = get_compiler("qasm")
# 编译QASM文本
qasm_str = """
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0], q[1];
"""

exe = comp.compile(qasm_str, 1)
backend = get_spinq_cloud('a492760446', '/Users/yucheng/.ssh/id_rsa')

circuit, qubit_mapping = backend.transpile("gemini_vp", exe)

print("qubite_mapping", qubit_mapping)
# 打印 qubit_mapping 的所有属性和对应的值
for attr in dir(qubit_mapping):
  # 排除以双下划线开头的特殊方法和属性
  if not attr.startswith("__"):
    try:
      value = getattr(qubit_mapping, attr)
      print(f"{attr}: {value}")
    except Exception as e:
      print(f"{attr}: <Unable to retrieve value> ({e})")
