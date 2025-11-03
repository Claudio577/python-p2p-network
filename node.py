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
            # 1. Tentativa rápida de estender a cadeia
            last_block = self.blockchain.get_previous_block()
            
            if data["block"]["previous_hash"] == self.blockchain.hash(last_block):
                print("👍 Bloco válido e estende a cadeia.")
                self.blockchain.chain.append(data["block"])
            else:
                # 2. Se não estende, há um fork. Solicitar a cadeia completa para resolver o conflito.
                print(f"⚠️ Bloco recebido não estende a cadeia atual. Solicitando cadeia completa de {conn.id}...")
                self.request_chain_from_node(conn.id)
        
        elif data["type"] == "NEW_TX":
            print("💸 Nova transação recebida:", data["tx"])
            self.blockchain.transactions.append(data["tx"])

        elif data["type"] == "REQUEST_CHAIN":
            # Responde com a cadeia local completa
            print(f"🔗 Recebido pedido de cadeia de {conn.id}. Enviando a cadeia local.")
            self.send_chain_response(conn.id, self.blockchain.chain)

        elif data["type"] == "CHAIN_RESPONSE":
            # Recebe a cadeia de outro nó e tenta substituí-la
            received_chain = data["chain"]
            print(f"🔗 Recebida cadeia completa de {conn.id} (tamanho: {len(received_chain)}). Iniciando verificação...")
            self.blockchain.replace_chain(received_chain)
            # Nota: O método replace_chain já imprime o resultado da substituição.
    
    # NOVOS MÉTODOS P2P para resolução de conflito
    def request_chain_from_node(self, node_id):
        """Envia uma solicitação para obter a cadeia completa de um nó vizinho."""
        msg = {"type": "REQUEST_CHAIN"}
        self.send_to_node(node_id, json.dumps(msg))

    def send_chain_response(self, node_id, chain):
        """Envia a cadeia local como resposta a uma solicitação."""
        msg = {"type": "CHAIN_RESPONSE", "chain": chain}
        self.send_to_node(node_id, json.dumps(msg))
    # FIM DOS NOVOS MÉTODOS

    def broadcast_block(self, block):
        msg = {"type": "NEW_BLOCK", "block": block}
        self.send_to_nodes(json.dumps(msg))

    def broadcast_transaction(self, tx):
        msg = {"type": "NEW_TX", "tx": tx}
        self.send_to_nodes(json.dumps(msg))


if __name__ == "__main__":
    if len(sys.argv) < 2: # Alterado de 3 para 2, pois a conexão opcional
        print("Uso: python node.py <porta> <conectar_em_porta_opcional>")
        sys.exit(0)

    port = int(sys.argv[1])
    node = BlockchainNode("127.0.0.1", port)
    node.start()

    # conecta a outro nó (opcional)
    if len(sys.argv) == 3:
        connect_port = int(sys.argv[2])
        # A função connect_with_node retorna o ID do nó vizinho se a conexão for bem-sucedida
        neighbor_id = node.connect_with_node("127.0.0.1", connect_port)
        if neighbor_id:
             # Ao conectar, solicitamos a cadeia para sincronização inicial
            print(f"Conectado ao nó {neighbor_id}. Solicitando sincronização de cadeia...")
            node.request_chain_from_node(neighbor_id)
        else:
             print("Falha ao conectar ao nó vizinho.")


    # Simula ações
    # A criação do bloco inicial só deve ocorrer se a cadeia estiver vazia, mas
    # o __init__ da Blockchain já garante isso, então este trecho é removido 
    # ou adaptado para não criar um bloco redundante no nó 2, por exemplo.
    # Como a Blockchain sempre começa com 1 bloco (Gênesis), vamos garantir que 
    # a simulação de mineração só ocorra se não houver conexão a um nó existente.
    
    # Se o nó é o primeiro na rede (sem conexão inicial), ele mina o bloco 1 para 
    # iniciar a simulação. Se ele se conecta a um vizinho, ele sincronizará.
    if len(sys.argv) == 2 or (len(sys.argv) == 3 and not node.nodes_in_the_network):
        print("⛏️ Minerando Bloco Gênesis...")
        # A função create_block na Blockchain já faz isso no __init__, mas aqui 
        # estamos simulando a mineração do primeiro bloco real após a inicialização.
        # Vamos apenas pular a criação do bloco 1 (Gênesis) no código principal, 
        # pois já está no __init__ da Blockchain.
        pass
    
    print("\nNó pronto para interagir. Digite as ações abaixo.")


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
            node.stop() # Adicionado stop() para encerrar o loop da p2pnetwork
            break
