# 需求： 接收qasm文本，使用flask框架，创建线路并提交到spinq cloud
from spinqit_simplified.compiler import get_compiler
from spinqit_simplified.backend import get_spinq_cloud
from spinqit_simplified.backend.client.spinq_cloud_client import SpinQCloudClient
from math import pi
from datetime import datetime
from copy import deepcopy
from autoray import numpy as ar
from scipy import sparse
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
from spinqit_simplified.model.spinqCloud.task import Task


comp = get_compiler("qasm")
from flask import Flask, request, jsonify
import json

# 创建Flask应用
app = Flask(__name__)
@app.route('/submit', methods=['POST'])
def submit():
    # 获取请求数据
    data = request.get_json()
    print(data,"data")
    qasm_str = data.get('qasm_str',"")
    user_name = data.get('user_name',"")
    private_key = data.get('private_key',"")
    
    # 存储对应user_name的private_key到test/user_name_id_rsa中
    with open("test/"+user_name+"_id_rsa", "w") as f:
        f.write(private_key)

    # 存储到test中，记录时间戳
    time = datetime.now().strftime("%Y%m%d%H%M%S")
    with open("test/callee"+time+".qasm", "w") as f:
        f.write(qasm_str)

    optimization_level = data.get('optimization_level', 0)
    comp = get_compiler("qasm")
    # 编译QASM文本
    exe = comp.compile("test/callee"+time+".qasm", optimization_level)
    
    # 配置模拟器
    
    # 执行并获取结果

    username = user_name
    # 读取test/id_rsa内容
    keyfile = "test/"+user_name+"_id_rsa"
    backend = get_spinq_cloud(username, keyfile)


    with open(keyfile) as f:
      key = f.read()
    message = username.encode(encoding="utf-8")
    rsakey = RSA.importKey(key)
    signer = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(message)
    sign = signer.sign(digest)
    signature = base64.b64encode(sign)
    signature = str(signature, encoding = "utf-8")

    # 没看懂mapping规则先借用双子座的transpile
    circuit, qubit_mapping = backend.transpile("gemini_vp", exe)
    api_client = SpinQCloudClient(username, signature)
    newTask = Task("test", "simulator", circuit, qubit_mapping.phy_to_log, calc_matrix=False, shots=1000, process_now=True, description="", api_client=api_client)
    res = api_client.create_task(newTask.to_request())
    res_entity = json.loads(res.content)
    return jsonify(res_entity)

