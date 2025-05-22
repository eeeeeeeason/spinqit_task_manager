#request,调用本地localhost:5000/submit
import json
import os
import requests
import logging
from mcp.server.fastmcp import FastMCP
from spinqit_task_manager import cloud_mcp_submit
from spinqit_task_manager.compiler import get_compiler
from spinqit_task_manager.backend import get_spinq_cloud
from spinqit_task_manager.backend.client.spinq_cloud_client import SpinQCloudClient
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
from spinqit_task_manager.model.spinqCloud.task import Task
from flask import Flask, request, jsonify
from spinqit_task_manager.model.spinqCloud.circuit import graph_to_circuit, convert_cz

import base64

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.debug("Starting Submit qasm task click initialization")


# 初始化MCP服务器
try:
    logger.debug("Submit qasm task")
    mcp = FastMCP("qasm_submit")
    logger.debug("FastMCP initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize FastMCP: {e}")
    raise

# 定义乘法工具
def qasm_submit(qasm_str, user_name, private_key_path) -> json:
    """submit qasm task to spinq cloud"""
    logger.debug(f"submit qasm task to spinq cloud with qasm_str={qasm_str}")
    private_key = None
    # 读取私钥文件
    if os.path.exists(private_key_path):
        with open(private_key_path, "r") as f:
            private_key = f.read()
    else:
        logger.error(f"Private key file {private_key_path} does not exist")
        raise FileNotFoundError(f"Private key file {private_key_path} does not exist")
    comp = get_compiler("qasm")
    # 编译QASM文本
    exe = comp.compile(qasm_str, 0)
    qnum = exe.qnum # 对于模拟器来说需要设置比特数与qasm匹配
    backend = get_spinq_cloud(user_name, private_key_path)
    message = user_name.encode(encoding="utf-8")
    rsakey = RSA.importKey(private_key)
    signer = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(message)
    sign = signer.sign(digest)
    signature = base64.b64encode(sign)
    signature = str(signature, encoding = "utf-8")
    api_client = SpinQCloudClient(user_name, signature)
    p = backend.get_platform("simulator")
    # 根据比特数构造mapping {0: 0, 1: 1}
    init_mapping = {}
    for i in range(qnum):
        init_mapping[i] = i
    circuit = graph_to_circuit(exe, init_mapping, p, None, None)

    # circuit, qubit_mapping = backend.transpile("gemini_vp", exe)

    newTask = Task("test-05152305", "simulator", circuit, init_mapping, calc_matrix=False, shots=1000, process_now=True, description="", api_client=api_client)
    res = api_client.create_task(newTask.to_request())
    res_entity = json.loads(res.content)
    print(res_entity)
    return res_entity

def get_task_result_by_id(user_name, private_key_path, task_id) -> json:
  # 提交实验成功后会拿到task_id，我们用task_id和登录用户去查看实验结果
  private_key = None
  # 读取私钥文件
  if os.path.exists(private_key_path):
      with open(private_key_path, "r") as f:
          private_key = f.read()
  else:
      logger.error(f"Private key file {private_key_path} does not exist")
      raise FileNotFoundError(f"Private key file {private_key_path} does not exist")
  # backend = get_spinq_cloud(user_name, private_key_path)
  message = user_name.encode(encoding="utf-8")
  rsakey = RSA.importKey(private_key)
  signer = Signature_pkcs1_v1_5.new(rsakey)
  digest = SHA256.new()
  digest.update(message)
  sign = signer.sign(digest)
  signature = base64.b64encode(sign)
  signature = str(signature, encoding = "utf-8")
  api_client = SpinQCloudClient(user_name, signature)
  api_client.login()
  task_res = api_client.task_result_by_id(task_id)
  res_entity = json.loads(task_res.content)
  print(res_entity)
  return res_entity


# 运行服务器
if __name__ == "__main__":
  qasm_str = "OPENQASM 2.0;\\\\ninclude \\\\\"qelib1.inc\\\\\";\\\\n\\\\nqreg q[2];\\\\nh q[0];\\\\ncx q[0], q[1];\"
  qasm_submit(qasm_str, "a492760446","/Users/yucheng/.ssh/id_rsa")

  # get_task_result_by_id("a492760446","/Users/yucheng/.ssh/id_rsa","23243")