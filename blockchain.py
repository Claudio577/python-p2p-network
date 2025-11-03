# blockchain.py
import hashlib
import json
from time import time

class Blockchain:
    def __init__(self, difficulty='0000'):
        self.chain = []
        self.transactions = []
        self.difficulty = difficulty # Adicionado para melhoria futura
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            # O cálculo do hash permanece o mesmo
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            # Utiliza a dificuldade padrão '0000'
            if hash_operation[:4] == '0000':
                return new_proof
            new_proof += 1

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender, 'receiver': receiver, 'amount': amount})
        return self.get_previous_block()['index'] + 1

    def is_chain_valid(self, chain=None):
        """Verifica se uma cadeia (local ou externa) é válida."""
        if chain is None:
            chain = self.chain

        previous_block = chain[0]
        for i in range(1, len(chain)):
            block = chain[i]
            # 1. Checa se o previous_hash está correto
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            # 2. Checa se o Proof of Work está correto
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            
            # 3. (Melhoria futura): Checar a validade das transações no bloco

            previous_block = block
        return True

    def replace_chain(self, chain):
        """Substitui a cadeia local pela cadeia recebida se for mais longa e válida."""
        if len(chain) > len(self.chain) and self.is_chain_valid(chain):
            self.chain = chain
            print("✅ Cadeia substituída! A nova cadeia é maior e válida.")
            return True
        elif len(chain) <= len(self.chain):
            print("❌ Cadeia recebida é mais curta ou igual. Cadeia local mantida.")
        else:
            print("❌ Cadeia recebida é mais longa, mas inválida. Cadeia local mantida.")
        return False
