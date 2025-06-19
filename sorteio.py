import random
from datetime import datetime
import pymongo
from faker import Faker
fake = Faker(['pt_BR'])
import os
random.seed(datetime.now().timestamp())
from tqdm import tqdm

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
    #numeros_sorteados = sortear_numeros()
    
    concurso = {
        'sorteio': sorteio,
        'data': data.strftime('%Y-%m-%d'),
        'numeros_sorteados': [],
        'tipo': 'Mega-Sena',
        'ganhadores_sena': [],
        'ganhadores_quina': [],
        'ganhadores_quadra': [],
        'premiacao': {
            'sena': 130000000,
            'quina': 6064938,
            'quadra': 8664084
        }
    }
    return concurso


def faltando(numeros_sorteados):

   

    jogos = dbJogos.find({"numeros": {"$all": list(numeros_sorteados)}}).to_list()
    #jogadores = dbJogos.find({"numeros": {"$all": list(numeros_sorteados)}})
    print(f"{6 - len(numeros_sorteados) } números que faltam")
    print(f"{len(jogos)} apostadores próximos do prêmio")

def checar_quina(num,concurso,senadores):
    quina = num[0:4]
    quinados = dbJogos.find({"numeros": {"$all": list(quina)}}).to_list()
    for ganhador in quinados:
        if ganhador['nome'] in senadores:
            continue
            
        concurso['ganhadores_quina'].append(ganhador['nome'])

def checar_quadra(num,concurso,senadores,quinadores):
    quadra = num[0:3]
    quadradores = dbJogos.find({"numeros": {"$all": list(quadra)}}).to_list()
    for ganhador in quadradores:
        if (ganhador['nome'] in quinadores) or (ganhador['nome'] in senadores):
            continue

        concurso['ganhadores_quadra'].append(ganhador['nome'])

def criar_jogo():
    #Aqui o programa que cria o concurso atual
    concurso = criar_concurso()
    

   
    for i in tqdm (range(4000000)):
        
        #aqui ele cria o jogador
        jogador = fake.name()
        numeros_jogados = sortear_numeros()
        #query = dbJogos.find_one({"numeros": numeros_jogados})
        ##Aqui procura se ja tem um jogo com os mesmos números jogados
        ##if query is not None:
            ## se ja existe, ele adiciona o jogador na lista de apostadores
        ##    dbJogos.update_one({"numeros": numeros_jogados}, {"$push":{"apostadores":jogador}})
        ##Se não existe, ele cria um novo jogo
        #else:


        jogador = {
            "nome" : jogador,
            'sorteio': concurso['sorteio'],
            'data': concurso['data'],
            'numeros': numeros_jogados,
            #'identificador': random.randint(10000, 99999),
            'tipo': concurso['tipo'],
        }
        dbJogos.insert_one(jogador)
        #if( _ % 1000 == 0):
        #   print(f"Criando jogos... {_}/30000", end='\r')
    
        
    
    while(len(num) < 6):
        
        sorteado = random.randint(1,75)

        if sorteado in num:
            continue
        else:
            num.add(sorteado)
            faltando(num)

            print(f"Números sorteados: {sorted(num)}")
            input("Sorteando o próximo número...")
            os.system('cls')

        if len(num) > 6:
            break
    
    
    ganhadores = dbJogos.find({"numeros": list(num)})
    for ganhador in ganhadores:
        concurso['ganhadores_sena'].append(ganhador['nome'])
    concurso['numeros_sorteados'] = list(num)

    checar_quina( list(num),concurso,concurso['ganhadores_sena'])
    checar_quadra( list(num),concurso,concurso['ganhadores_sena'], concurso['ganhadores_quina'])

    dbSorteio.insert_one(concurso)
    if( len(concurso['ganhadores_sena']) != 0):
        print(f"{len(concurso['ganhadores_sena'])} Ganhadores da Sena: {concurso['ganhadores_sena']}, recebendo R${concurso['premiacao'].get('sena')/len(concurso['ganhadores_sena'])} cada um")
    if( len(concurso['ganhadores_quina']) != 0):
        print(f"{len(concurso['ganhadores_quina'])} Ganhadores da Quina: {concurso['ganhadores_quina']}, recebendo R${concurso['premiacao'].get('quina')/len(concurso['ganhadores_quina'])} cada um")
    if( len(concurso['ganhadores_quadra']) != 0):
        print(f"{len(concurso['ganhadores_quadra'])} Ganhadores da Quadra: {concurso['ganhadores_quadra']}, recebendo R${concurso['premiacao'].get('quadra')/len(concurso['ganhadores_quadra'])} cada um")
            

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


## numeros_sorteados = [1, 2, 3, 4, 5, 6]
## Encontrar no banco de dados os jogos que possuem os numeros sorteados
## Adiciona um campo de soma para cada numero sorteado que possui
## Verifica se a quantidade de numeros sorteados é igual a 5 (quina) ou 4 (quadra)
## Se for Maior que 4 e menor que 6, quina
## se for maior que 3 e menor que 5, quadra
## Adiciona o jogador na lista de ganhadores do concurso em seu respectivo campo