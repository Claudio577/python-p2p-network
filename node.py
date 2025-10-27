# node.py
from p2pnetwork.node import Node
from blockchain import Blockchain
import json
import sys

class BlockchainNode(Node):
    def __init__(self, host, port, id=None):
        super().__init__(host, port, id)
        self.blockchain = Blockchain()
        print(f"🚀 Nó iniciado em {host}:{port}")

    def on_message(self, conn, message):
        data = json.loads(message)
        if data["type"] == "NEW_BLOCK":
            print("📦 Recebido novo bloco da rede!")
            self.blockchain.chain.append(data["block"])
        elif data["type"] == "NEW_TX":
            print("💸 Nova transação recebida:", data["tx"])
            self.blockchain.transactions.append(data["tx"])

    def broadcast_block(self, block):
        msg = {"type": "NEW_BLOCK", "block": block}
        self.send_to_nodes(json.dumps(msg))

    def broadcast_transaction(self, tx):
        msg = {"type": "NEW_TX", "tx": tx}
        self.send_to_nodes(json.dumps(msg))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python node.py <porta> <conectar_em_porta_opcional>")
        sys.exit(0)

    port = int(sys.argv[1])
    node = BlockchainNode("127.0.0.1", port)
    node.start()

    # conecta a outro nó (opcional)
    if len(sys.argv) == 3:
        connect_port = int(sys.argv[2])
        node.connect_with_node("127.0.0.1", connect_port)

    # Simula ações
    print("⛏️ Minerando bloco inicial...")
    block = node.blockchain.create_block(proof=100, previous_hash='0')
    node.broadcast_block(block)
    print("Bloco inicial criado e enviado para a rede!")

    while True:
        action = input("\n1=transação, 2=minerar, 3=ver chain, 0=sair → ")
        if action == "1":
            s = input("Remetente: ")
            r = input("Destinatário: ")
            v = float(input("Valor: "))
            node.blockchain.add_transaction(s, r, v)
            node.broadcast_transaction({'sender': s, 'receiver': r, 'amount': v})
        elif action == "2":
            prev_block = node.blockchain.get_previous_block()
            proof = node.blockchain.proof_of_work(prev_block['proof'])
            prev_hash = node.blockchain.hash(prev_block)
            block = node.blockchain.create_block(proof, prev_hash)
            node.broadcast_block(block)
            print("✅ Bloco minerado e transmitido!")
        elif action == "3":
            print(json.dumps(node.blockchain.chain, indent=4))
        elif action == "0":
            print("Encerrando nó...")
            break
