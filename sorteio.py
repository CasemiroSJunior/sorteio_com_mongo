import random
from datetime import datetime
import pymongo
from faker import Faker
fake = Faker(['pt_BR'])
import os
random.seed(datetime.now().timestamp())

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['loteria']
dbSorteio = db['sorteio']
dbJogos = db['jogos']
num = set()

max=75
min=1

def sortear_numeros():
    numeros = set()
    while len(numeros) < 6:
        numero = random.randint(min, max)
        if numero not in numeros:
            numeros.add(numero)
    return sorted(numeros)

def criar_jogador():
    jogador = {
        'nome': fake.name(),
        'cpf': fake.cpf(),
    }
    return jogador

def criar_concurso():
    sorteio = random.randint(1, 10000)
    data = fake.date_between(start_date='-2y', end_date='today')
    numeros_sorteados = sortear_numeros()
    
    concurso = {
        'sorteio': sorteio,
        'data': data.strftime('%Y-%m-%d'),
        'numeros_sorteados': numeros_sorteados,
        'tipo': 'Mega-Sena',
        'premiacao': {
            'sena': random.randint(100000, 1000000),
            'quina': random.randint(10000, 50000),
            'quadra': random.randint(1000, 5000)
        }
    }
    return concurso


def faltando(numeros_sorteados):

    jogos = dbJogos.find({"numeros": {"$in": list(numeros_sorteados)}})

    print(f"{len(numeros_sorteados) - 6} números que faltam")
    print(f"{len(jogos.to_list())} apostadores próximos do prêmio")

def criar_jogo():
    concurso = criar_concurso()
    dbSorteio.insert_one(concurso)

    for _ in range(10):

        jogador = fake.name()
        numeros_jogados = sortear_numeros()
        query = dbJogos.find_one({"numeros": numeros_jogados})
        if query is not None:
            dbJogos.update_one({"numeros": numeros_jogados}, {"$push":{"apostadores":jogador}})    
        
        else:
            jogo = {
                'apostadores': [jogador],
                'sorteio': concurso['sorteio'],
                'data': concurso['data'],
                'numeros': numeros_jogados,
                'identificador': random.randint(10000, 99999),
                'tipo': concurso['tipo']
            }
            dbJogos.insert_one(jogo)
    

        while(len(num) < 6):
            
            sorteado = random.randint(1, 75)

            if sorteado in num:
                continue
            else:
                num.add(sorteado)
                faltando(num)

                input("Sorteando o próximo número...")
                
                os.system('cls')

            if len(num) > 6:
                break
            print(sorteado)
            

criar_jogo()
dbJogos.delete_many({})

""" jogo:{
    'apostadores': [jogador],
    'sorteio': 2823,
    'data': 2025-6-3,
    'numeros': [1, 2, 3, 4, 5, 6],
    'identificador': 10887,
    'tipo': 'Mega-Sena',
} """
