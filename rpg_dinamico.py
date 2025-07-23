# -*- coding: utf-8 -*-
import os
import random
import time

# --- CONSTANTES DE CONFIGURAÇÃO DO JOGO --- Felipe
XP_PARA_NIVEL = {1: 10, 2: 25, 3: 50, 4: 80, 5: float('inf')}
PONTOS_DISTRIBUICAO_INICIAL = 15
PONTOS_POR_NIVEL = 5
PENALIDADE_XP_MORTE = 0.70
CHANCE_QUEBRA_AO_FUGIR = 0.25
MAX_POCOES_INVENTARIO = 5

RARIDADES = {
    "comum": {"chance": 0.75, "multiplicador": 1.0, "cor": "\033[97m"},
    "incomum": {"chance": 0.20, "multiplicador": 1.5, "cor": "\033[92m"},
    "raro": {"chance": 0.05, "multiplicador": 2.5, "cor": "\033[94m"}
}
COR_RESET = "\033[0m"

# --- BANCO DE DADOS DE HABILIDADES E CLASSES ---
CLASSES_BASE = {
    "Feral": {
        "desc": "Usa o Caos para fortalecer seus ataques físicos.",
        "stats": {"vida_base": 50, "forca_base": 15, "defesa_base": 10, "agilidade_base": 10, "caos_base": 40},
        "habilidades": [
            {"nome": "Impacto do Caos", "custo": 8, "multiplicador": 1.35, "efeito": None, "desc": "Um golpe poderoso que ignora a defesa."},
            {"nome": "Fúria Selvagem", "custo": 6, "multiplicador": 0, "efeito": {"tipo": "buff_forca", "valor": 5, "duracao": 3, "chance": 1.0}, "desc": "Aumenta sua própria Força por 3 turnos."}
        ]
    },
    "Sombra": {
        "desc": "Usa o Caos para golpes rápidos e eficientes.",
        "stats": {"vida_base": 60, "forca_base": 10, "defesa_base": 5, "agilidade_base": 15, "caos_base": 40},
        "habilidades": [
            {"nome": "Lâmina do Caos", "custo": 4, "multiplicador": 1.20, "efeito": None, "desc": "Um ataque mágico rápido e de baixo custo."},
            {"nome": "Névoa Venenosa", "custo": 10, "multiplicador": 0.5, "efeito": {"tipo": "veneno", "dano": 5, "duracao": 3, "chance": 1.0}, "desc": "Causa dano inicial e dano de veneno por 3 turnos."}
        ]
    },
    "Moldador de Essência": {
        "desc": "Transforma sua força vital em poder mágico devastador.",
        "stats": {"vida_base": 45, "forca_base": 20, "defesa_base": 10, "agilidade_base": 10, "caos_base": 60},
        "habilidades": [
            {"nome": "Orbe do Caos", "custo": 12, "multiplicador": 1.50, "efeito": None, "desc": "Uma esfera de energia mágica de alto dano."},
            {"nome": "Raio Congelante", "custo": 15, "multiplicador": 0.8, "efeito": {"tipo": "congelado", "duracao": 2, "chance": 0.75}, "desc": "Causa dano e tem 75% de chance de congelar o alvo por 1 turno."}
        ]
    }
}

NOMES_EQUIPAMENTOS = { "arma": {"prefixos": ["Espada", "Machado"], "sufixos": ["Brutal", "Veloz"]}, "capacete": {"prefixos": ["Elmo", "Capacete"], "sufixos": ["da Guarda", "Sombrio"]}, "armadura": {"prefixos": ["Peitoral", "Cota de Malha"], "sufixos": ["de Placas", "Leve"]}, "calca": {"prefixos": ["Grevas", "Calças"], "sufixos": ["de Batalha", "do Viajante"]}, "bota": {"prefixos": ["Botas", "Coturno"], "sufixos": ["de Corrida", "Pesadas"]} }
INIMIGO_TEMPLATES = { "Goblin Ladrão": {"vida": 20, "forca": 5, "defesa": 2, "agilidade": 8, "caos": 10}, "Orc Guerreiro": {"vida": 40, "forca": 10, "defesa": 5, "agilidade": 3, "caos": 5}, "Lobo das Neves": {"vida": 30, "forca": 8, "defesa": 3, "agilidade": 12, "caos": 15}, "Golem de Pedra": {"vida": 60, "forca": 12, "defesa": 10, "agilidade": 1, "caos": 0}, "Mago Esqueleto": {"vida": 25, "forca": 15, "defesa": 2, "agilidade": 6, "caos": 30} }
CHEFE_TEMPLATES = { "Lich Tirano": {"vida": 150, "forca": 20, "defesa": 15, "agilidade": 10, "caos": 100}, "Behemoth Colossal": {"vida": 250, "forca": 30, "defesa": 25, "agilidade": 5, "caos": 20}, "Quimera Mutante": {"vida": 180, "forca": 25, "defesa": 10, "agilidade": 20, "caos": 50} }
# MODIFICAÇÃO: Adicionada a Poção de Caos
POCA_TEMPLATES = { "cura": {"nome": "Poção de Cura", "valor": 50}, "restaura_caos": {"nome": "Poção de Caos", "valor": 40}, "buff_forca": {"nome": "Elixir de Força", "valor": 5, "duracao": 3}, "buff_defesa": {"nome": "Poção Casca de Ferro", "valor": 5, "duracao": 3}, "buff_agilidade": {"nome": "Extrato de Agilidade", "valor": 5, "duracao": 3} }

# --- CLASSES BASE (A ESTRUTURA DO JOGO) ---

class Item:
    def __init__(self, nome, raridade): self.nome = nome; self.raridade = raridade
    def nome_formatado(self): cor = RARIDADES[self.raridade]['cor']; icone = "✨" if self.raridade == "raro" else ""; return f"{cor}{self.nome} [{self.raridade.capitalize()}] {icone}{COR_RESET}"

class Equipamento(Item):
    def __init__(self, nome, slot, raridade, bonus_vida=0.0, bonus_forca=0.0, bonus_defesa=0.0, bonus_agilidade=0.0, bonus_caos=0.0):
        super().__init__(nome, raridade); self.slot = slot; self.bonus_vida = float(bonus_vida); self.bonus_forca = float(bonus_forca); self.bonus_defesa = float(bonus_defesa); self.bonus_agilidade = float(bonus_agilidade); self.bonus_caos = float(bonus_caos)
    def __str__(self):
        bonus = [f"{b:+.1f} {s}" for s,b in [("FOR",self.bonus_forca), ("DEF",self.bonus_defesa), ("AGI",self.bonus_agilidade), ("VIDA",self.bonus_vida), ("CAOS", self.bonus_caos)] if b]
        return f"{self.nome_formatado()} ({', '.join(bonus)})"

class Pocao(Item):
    def __init__(self, nome, raridade, tipo, valor, duracao=0):
        super().__init__(nome, raridade); self.tipo = tipo; self.valor = float(valor); self.duracao = duracao
    def __str__(self):
        if self.tipo == 'cura': return f"{self.nome_formatado()} (Cura {self.valor:.1f} de Vida)"
        elif self.tipo == 'restaura_caos': return f"{self.nome_formatado()} (Restaura {self.valor:.1f} de Caos)"
        else: tipo_str = self.tipo.split('_')[1].upper(); return f"{self.nome_formatado()} (+{self.valor:.1f} {tipo_str} por {self.duracao} turnos)"

class Personagem:
    def __init__(self, nome, vida_base, forca_base, defesa_base, agilidade_base, caos_base, nivel=1):
        self.nome = nome; self.vida_base = float(vida_base); self.forca_base = float(forca_base); self.defesa_base = float(defesa_base); self.agilidade_base = float(agilidade_base); self.caos_base = float(caos_base); self.nivel = nivel
        self.vida_atual = self.vida_base; self.caos_atual = self.caos_base
        self.equipamentos = {"arma": None, "capacete": None, "armadura": None, "calca": None, "bota": None}
        self.buffs_ativos = {}
        self.efeitos_status = {}

    @property
    def forca(self): return self.forca_base + sum(eq.bonus_forca for eq in self.equipamentos.values() if eq) + self.buffs_ativos.get('forca', {'valor': 0})['valor']
    @property
    def defesa(self): return self.defesa_base + sum(eq.bonus_defesa for eq in self.equipamentos.values() if eq) + self.buffs_ativos.get('defesa', {'valor': 0})['valor']
    @property
    def agilidade(self): return self.agilidade_base + sum(eq.bonus_agilidade for eq in self.equipamentos.values() if eq) + self.buffs_ativos.get('agilidade', {'valor': 0})['valor']
    @property
    def vida_maxima(self): return self.vida_base + sum(eq.bonus_vida for eq in self.equipamentos.values() if eq)
    @property
    def caos_maximo(self): return self.caos_base + sum(eq.bonus_caos for eq in self.equipamentos.values() if eq)

    def atacar(self, alvo):
        if 'congelado' in self.efeitos_status:
            print(f"🥶 {self.nome} está congelado e não pode se mover!"); time.sleep(1); return

        print(f"\n💥 {self.nome} usa um Ataque Básico contra {alvo.nome}!")
        time.sleep(1); chance_acerto = 90 - (alvo.agilidade - self.agilidade); chance_acerto = max(20, min(100, chance_acerto))
        if random.randint(1, 100) > chance_acerto: print(f"   💨 ERROU!"); time.sleep(1); return
        reducao_de_dano = alvo.defesa * 0.3; dano = max(1.0, self.forca - reducao_de_dano)
        print(f"   🎯 Acertou! Dano Físico causado: {dano:.1f}!"); alvo.receber_dano(dano); time.sleep(1)

    def receber_dano(self, dano): self.vida_atual -= dano; self.vida_atual = max(0.0, self.vida_atual)
    def esta_vivo(self): return self.vida_atual > 0

    def processar_efeitos_e_buffs(self):
        for tipo, data in list(self.buffs_ativos.items()):
            data['turnos_restantes'] -= 1
            if data['turnos_restantes'] <= 0: print(f"O efeito do buff de {tipo.upper()} acabou."); del self.buffs_ativos[tipo]; time.sleep(1)
        
        for tipo, data in list(self.efeitos_status.items()):
            if tipo == 'veneno':
                dano_veneno = data['dano']
                print(f"🐍 {self.nome} sofre {dano_veneno:.1f} de dano de veneno.")
                self.receber_dano(dano_veneno); time.sleep(1)
            
            data['turnos_restantes'] -= 1
            if data['turnos_restantes'] <= 0:
                print(f"O efeito de {tipo.upper()} em {self.nome} acabou."); del self.efeitos_status[tipo]; time.sleep(1)


    def mostrar_status(self):
        classe_info = f"- O {self.classe.capitalize()} " if hasattr(self, 'classe') else ""
        print(f"--- STATUS: {self.nome} {classe_info}(Nível {self.nivel}) ---")
        print(f"❤️  Vida: {self.vida_atual:.1f} / {self.vida_maxima:.1f}  |  🔮 Caos: {self.caos_atual:.1f} / {self.caos_maximo:.1f}")
        print(f"💪 Força: {self.forca:.1f} | 🛡️ Defesa: {self.defesa:.1f} | 👟 Agilidade: {self.agilidade:.1f}")
        
        status_str_list = []
        if self.buffs_ativos:
            buff_str = ", ".join([f"{data['valor']:.1f} {tipo.upper()} ({data['turnos_restantes']}t)" for tipo, data in self.buffs_ativos.items()])
            status_str_list.append(f"BUFFS: {buff_str}")
        if self.efeitos_status:
            efeito_str = ", ".join([f"{tipo.upper()} ({data['turnos_restantes']}t)" for tipo, data in self.efeitos_status.items()])
            status_str_list.append(f"EFEITOS: {efeito_str}")
        
        if status_str_list:
            print(f"   ATIVOS: " + " | ".join(status_str_list))


class Chefao(Personagem):
    def __init__(self, nome, vida_base, forca_base, defesa_base, agilidade_base, caos_base, nivel=1):
        super().__init__(nome, vida_base, forca_base, defesa_base, agilidade_base, caos_base, nivel)
        self.nome = f"🔥 {nome} 🔥"

class Heroi(Personagem):
    def __init__(self, nome, classe, vida_base, forca_base, defesa_base, agilidade_base, caos_base):
        super().__init__(nome, vida_base, forca_base, defesa_base, agilidade_base, caos_base, nivel=1)
        self.classe = classe; self.xp_atual = 0; self.xp_proximo_nivel = XP_PARA_NIVEL[self.nivel]; self.inventario_pocoes = []; self.proficiencia = 0.0

    def ganhar_xp(self, quantidade):
        if self.nivel >= 5: return
        self.xp_atual += quantidade
        print(f"\n✨ Você ganhou {quantidade} de XP! ({self.xp_atual:.0f}/{self.xp_proximo_nivel})"); time.sleep(1)
        while self.xp_atual >= self.xp_proximo_nivel and self.nivel < 5: self.subir_de_nivel()

    def subir_de_nivel(self):
        xp_excedente = self.xp_atual - self.xp_proximo_nivel; self.nivel += 1; self.xp_atual = xp_excedente
        self.xp_proximo_nivel = XP_PARA_NIVEL.get(self.nivel, float('inf'))
        self.proficiencia += 0.05
        # MODIFICAÇÃO: Aumento de vida e caos por nível
        self.vida_base += 20
        self.caos_base += 10
        limpar_tela()
        print("\n🎉🎉🎉 LEVEL UP! 🎉🎉🎉"); print(f"Você alcançou o Nível {self.nivel}!"); time.sleep(2)
        print(f"Sua proficiência com habilidades aumentou! Vida e Caos base também aumentaram.")
        distribuir_pontos_nivel(self, PONTOS_POR_NIVEL)
        self.vida_atual = self.vida_maxima; self.caos_atual = self.caos_maximo
        print("Seus atributos foram fortalecidos e sua Vida/Caos foram restaurados!"); time.sleep(3)

    def usar_habilidade(self, alvo, habilidade):
        custo = habilidade['custo']
        if self.caos_atual < custo: print("Caos insuficiente para usar esta habilidade!"); time.sleep(2); return False
        
        self.caos_atual -= custo
        multiplicador = habilidade['multiplicador'] + self.proficiencia
        dano_magico = self.forca * multiplicador

        print(f"\n✨ {self.nome} usa {habilidade['nome']}!")
        time.sleep(1)
        
        if dano_magico > 0:
            print(f"   Dano Mágico causado: {dano_magico:.1f}! (Ignora defesa)"); alvo.receber_dano(dano_magico)
        
        efeito = habilidade.get('efeito')
        if efeito and random.random() < efeito['chance']:
            if efeito['tipo'] in ['veneno', 'congelado']:
                print(f"   � O alvo foi afetado por {efeito['tipo'].upper()}!")
                alvo.efeitos_status[efeito['tipo']] = {'turnos_restantes': efeito['duracao'] + 1, 'dano': efeito.get('dano', 0)}
            elif efeito['tipo'] == 'buff_forca':
                print(f"   💪 Você se sente mais forte!")
                self.buffs_ativos['forca'] = {'valor': efeito['valor'], 'turnos_restantes': efeito['duracao'] + 1}
        
        time.sleep(1); return True

    def usar_pocao(self, pocao_index):
        pocao = self.inventario_pocoes.pop(pocao_index); print(f"\nVocê usou {pocao.nome_formatado()}!")
        if pocao.tipo == 'cura':
            vida_curada = min(self.vida_maxima - self.vida_atual, pocao.valor); self.vida_atual += vida_curada
            print(f"   Você recuperou {vida_curada:.1f} de vida.")
        # MODIFICAÇÃO: Lógica para a poção de caos
        elif pocao.tipo == 'restaura_caos':
            caos_recuperado = min(self.caos_maximo - self.caos_atual, pocao.valor); self.caos_atual += caos_recuperado
            print(f"   Você recuperou {caos_recuperado:.1f} de caos.")
        else:
            tipo_buff = pocao.tipo.split('_')[1]; self.buffs_ativos[tipo_buff] = {'valor': pocao.valor, 'turnos_restantes': pocao.duracao + 1}
            print(f"   Seu atributo {tipo_buff.upper()} aumentou em {pocao.valor:.1f} por {pocao.duracao} turnos!")
        time.sleep(2)

    def avaliar_e_equipar_item(self, novo_equip):
        limpar_tela(); print("✨ AVALIANDO ITEM ✨"); print(f"Item novo: {novo_equip}"); item_atual = self.equipamentos[novo_equip.slot]
        print(f"Equipado atualmente: {item_atual if item_atual else 'Nada'}")
        escolha = input("\nDeseja equipar o novo item? (S/N) ").upper()
        if escolha == 'S':
            bonus_vida_antigo = item_atual.bonus_vida if item_atual else 0.0
            bonus_caos_antigo = item_atual.bonus_caos if item_atual else 0.0
            if item_atual: print(f"   Substituindo {item_atual.nome_formatado()}...")
            self.equipamentos[novo_equip.slot] = novo_equip
            delta_vida = novo_equip.bonus_vida - bonus_vida_antigo; delta_caos = novo_equip.bonus_caos - bonus_caos_antigo
            self.vida_atual += delta_vida; self.caos_atual += delta_caos
            self.vida_atual = min(self.vida_maxima, self.vida_atual); self.caos_atual = min(self.caos_maximo, self.caos_atual)
            print(f"   {self.nome} equipou {novo_equip.nome_formatado()}."); return True
        else: print("Você decidiu não equipar este item."); return False

    def mostrar_status_completo(self):
        super().mostrar_status()
        if self.nivel < 5: print(f"📊 XP: {self.xp_atual:.0f} / {self.xp_proximo_nivel}")
        else: print("📊 XP: MÁXIMO")
        print("--- Atributos Base ---"); print(f"   - Vida: {self.vida_base:.1f}, Força: {self.forca_base:.1f}, Defesa: {self.defesa_base:.1f}, Agilidade: {self.agilidade_base:.1f}, Caos: {self.caos_base:.1f}")
        print("--- Equipamentos ---"); [print(f"   - {slot.capitalize()}: {item.nome_formatado() if item else 'Vazio'}") for slot, item in self.equipamentos.items()]
        print("--- Inventário de Poções ---");
        if self.inventario_pocoes: [print(f"   - {pocao}") for pocao in self.inventario_pocoes]
        else: print("   Vazio")
        print("--------------------")

# --- BANCO DE DADOS E FUNÇÕES GLOBAIS ---
HEROIS_CRIADOS = {}
def limpar_tela(): os.system('cls' if os.name == 'nt' else 'clear')
def obter_raridade():
    roll = random.random(); cumulative_chance = 0
    for raridade in ["comum", "incomum", "raro"]:
        data = RARIDADES[raridade]
        cumulative_chance += data['chance'];
        if roll < cumulative_chance: return raridade
    return "comum"

def gerar_inimigo(nivel_heroi):
    nome_template = random.choice(list(INIMIGO_TEMPLATES.keys())); stats_base = INIMIGO_TEMPLATES[nome_template]
    pontos_extras = (nivel_heroi - 1) * 8
    vida_final = stats_base["vida"] + pontos_extras * 2; forca_final = stats_base["forca"] + pontos_extras * 0.5; defesa_final = stats_base["defesa"] + pontos_extras * 0.3; agilidade_final = stats_base["agilidade"] + pontos_extras * 0.2; caos_final = stats_base["caos"]
    return Personagem(f"{nome_template} (N{nivel_heroi})", vida_final, forca_final, defesa_final, agilidade_final, caos_final, nivel=nivel_heroi)

def gerar_chefe(nivel_heroi):
    nome_template = random.choice(list(CHEFE_TEMPLATES.keys())); stats_base = CHEFE_TEMPLATES[nome_template]
    pontos_extras = (nivel_heroi - 1) * 12
    vida_final = stats_base["vida"] + pontos_extras * 4; forca_final = stats_base["forca"] + pontos_extras * 0.6; defesa_final = stats_base["defesa"] + pontos_extras * 0.4; agilidade_final = stats_base["agilidade"] + pontos_extras * 0.2; caos_final = stats_base["caos"]
    return Chefao(f"{nome_template} (N{nivel_heroi})", vida_final, forca_final, defesa_final, agilidade_final, caos_final, nivel=nivel_heroi)

def gerar_recompensa_aleatoria(nivel_batalha=1):
    if random.random() > 0.4:
        raridade = obter_raridade(); multiplicador = RARIDADES[raridade]['multiplicador']; slot = random.choice(list(NOMES_EQUIPAMENTOS.keys())); bonus_base = nivel_batalha * 2
        prefixo = random.choice(NOMES_EQUIPAMENTOS[slot]["prefixos"]); sufixo = random.choice(NOMES_EQUIPAMENTOS[slot]["sufixos"]); nome_item = f"{prefixo} {sufixo}"
        bonus_caos = (random.uniform(bonus_base, bonus_base + 2) * multiplicador) if random.random() < 0.2 else 0
        if slot == "arma": return Equipamento(nome_item, slot, raridade, bonus_forca=random.uniform(bonus_base, bonus_base + 3) * multiplicador, bonus_caos=bonus_caos)
        if slot == "capacete": return Equipamento(nome_item, slot, raridade, bonus_defesa=random.uniform(bonus_base, bonus_base + 2) * multiplicador, bonus_agilidade=-random.uniform(1, 2), bonus_caos=bonus_caos)
        if slot == "armadura": return Equipamento(nome_item, slot, raridade, bonus_defesa=random.uniform(bonus_base, bonus_base + 5) * multiplicador, bonus_vida=bonus_base*2*multiplicador)
        if slot == "calca": return Equipamento(nome_item, slot, raridade, bonus_agilidade=random.uniform(bonus_base, bonus_base + 2) * multiplicador, bonus_vida=bonus_base*multiplicador)
        if slot == "bota": return Equipamento(nome_item, slot, raridade, bonus_agilidade=random.uniform(bonus_base, bonus_base + 2) * multiplicador, bonus_defesa=-random.uniform(1, 2))
    else:
        raridade = obter_raridade(); multiplicador = RARIDADES[raridade]['multiplicador']; tipo_pocao = random.choice(list(POCA_TEMPLATES.keys())); template = POCA_TEMPLATES[tipo_pocao]
        valor_final = template.get('valor', 0) * multiplicador
        return Pocao(template['nome'], raridade, tipo_pocao, valor_final, template.get('duracao', 0))

# --- TELAS E MENUS DO JOGO ---
def distribuir_pontos_nivel(jogador, pontos):
    while pontos > 0:
        limpar_tela(); print(f"--- DISTRIBUA SEUS PONTOS DE ATRIBUTO ---"); jogador.mostrar_status_completo()
        print(f"\nVocê tem {pontos} pontos restantes para distribuir.")
        print("Qual atributo você quer aumentar?\n1. Força\n2. Defesa\n3. Agilidade\n4. Terminei")
        attr_escolha = input("> ")
        if attr_escolha == '4': break
        try:
            pontos_gastar = int(input(f"Quantos pontos (de {pontos})? "));
            if pontos_gastar <= 0 or pontos_gastar > pontos: print("Valor inválido."); time.sleep(1); continue
            if attr_escolha == '1': jogador.forca_base += pontos_gastar
            elif attr_escolha == '2': jogador.defesa_base += pontos_gastar
            elif attr_escolha == '3': jogador.agilidade_base += pontos_gastar
            else: print("Escolha inválida."); time.sleep(1); continue
            pontos -= pontos_gastar
            jogador.vida_atual = jogador.vida_maxima; jogador.caos_atual = jogador.caos_maximo
        except ValueError: print("Entrada inválida."); time.sleep(1)

def criar_novo_heroi():
    limpar_tela(); print("--- CRIAÇÃO DE HERÓI ---"); nome = input("Qual o nome do seu Herói? ")
    print("\nEscolha a sua classe:"); [print(f"{i + 1}. {c.capitalize()} - {d['desc']}") for i, (c, d) in enumerate(CLASSES_BASE.items())]
    escolha_classe_nome = "";
    while escolha_classe_nome not in CLASSES_BASE:
        try: index = int(input("> ")) - 1; escolha_classe_nome = list(CLASSES_BASE.keys())[index] if 0 <= index < len(CLASSES_BASE) else ""
        except(ValueError, IndexError): print("Escolha inválida.")
    stats_iniciais = CLASSES_BASE[escolha_classe_nome]["stats"]; heroi = Heroi(nome, escolha_classe_nome, **stats_iniciais)
    distribuir_pontos_nivel(heroi, PONTOS_DISTRIBUICAO_INICIAL)
    HEROIS_CRIADOS[nome] = heroi; limpar_tela(); print(f"--- Herói {nome} - O {escolha_classe_nome.capitalize()} foi criado! ---"); heroi.mostrar_status_completo(); input("\nPressione ENTER para continuar..."); return heroi

def selecionar_heroi():
    limpar_tela()
    if not HEROIS_CRIADOS: print("Nenhum herói criado."); time.sleep(2); return criar_novo_heroi()
    print("--- SELECIONE SEU HERÓI ---"); nomes_herois = list(HEROIS_CRIADOS.keys())
    for i, nome in enumerate(nomes_herois): heroi_obj = HEROIS_CRIADOS[nome]; print(f"{i + 1}. {heroi_obj.nome} - {heroi_obj.classe.capitalize()} (Nível {heroi_obj.nivel})")
    while True:
        try:
            escolha = int(input("> ")) - 1
            if 0 <= escolha < len(nomes_herois): nome_escolhido = nomes_herois[escolha]; print(f"Você selecionou {nome_escolhido}!"); time.sleep(1); return HEROIS_CRIADOS[nome_escolhido]
            else: print("Escolha inválida.")
        except (ValueError, IndexError): print("Por favor, digite um número.")

def usar_pocao_em_batalha(jogador):
    limpar_tela();
    if not jogador.inventario_pocoes: print("Seu inventário de poções está vazio."); time.sleep(2); return False
    print("--- INVENTÁRIO DE POÇÕES ---"); [print(f"{i + 1}. {p}") for i,p in enumerate(jogador.inventario_pocoes)]; print(f"{len(jogador.inventario_pocoes) + 1}. Voltar")
    while True:
        try:
            escolha = int(input("> "))
            if 1 <= escolha <= len(jogador.inventario_pocoes): jogador.usar_pocao(escolha - 1); return True
            elif escolha == len(jogador.inventario_pocoes) + 1: return False
            else: print("Escolha inválida.")
        except ValueError: print("Por favor, digite um número.")

def menu_de_habilidades(jogador, inimigo):
    habilidades = CLASSES_BASE[jogador.classe]['habilidades']
    while True:
        limpar_tela()
        print("--- ESCOLHA UMA HABILIDADE ---")
        for i, hab in enumerate(habilidades):
            print(f"{i + 1}. {hab['nome']} (Custo: {hab['custo']} Caos) - {hab['desc']}")
        print(f"{len(habilidades) + 1}. Voltar")

        try:
            escolha = int(input("> "))
            if 1 <= escolha <= len(habilidades):
                habilidade_escolhida = habilidades[escolha - 1]
                if jogador.usar_habilidade(inimigo, habilidade_escolhida):
                    return True 
                else:
                    return False 
            elif escolha == len(habilidades) + 1:
                return False
            else:
                print("Escolha inválida."); time.sleep(1)
        except ValueError:
            print("Entrada inválida."); time.sleep(1)

def menu_de_ataque(jogador, inimigo):
    while True:
        limpar_tela(); print("Escolha seu tipo de ataque:"); print("1. Ataque Básico (Dano Físico, usa Força vs Defesa)")
        print(f"2. Habilidades de Classe (Usa Caos)"); print("3. Voltar")
        escolha = input("> ")
        if escolha == '1': 
            jogador.atacar(inimigo)
            return True
        elif escolha == '2':
            if menu_de_habilidades(jogador, inimigo): 
                return True 
            else: 
                continue 
        elif escolha == '3': 
            return False
        else: 
            print("Opção inválida.")

def tela_de_recompensa(jogador):
    limpar_tela(); print("🏆 RECOMPENSAS DA BATALHA 🏆"); print("Você encontrou alguns tesouros! Escolha sabiamente:")
    recompensas = [gerar_recompensa_aleatoria(jogador.nivel) for _ in range(3)]
    while True:
        limpar_tela(); print("Escolha uma recompensa:")
        for i, item in enumerate(recompensas):
            if item: print(f"{i + 1}. {item}")
        print(f"{len(recompensas) + 1}. Não quero nenhum item.")
        try:
            escolha = int(input("> "))
            if 1 <= escolha <= len(recompensas):
                item_escolhido = recompensas[escolha - 1]
                if not item_escolhido: print("Você já pegou este item."); time.sleep(1); continue
                if isinstance(item_escolhido, Equipamento):
                    if jogador.avaliar_e_equipar_item(item_escolhido): break
                elif isinstance(item_escolhido, Pocao):
                    if len(jogador.inventario_pocoes) < MAX_POCOES_INVENTARIO:
                        jogador.inventario_pocoes.append(item_escolhido); print(f"Você guardou {item_escolhido.nome_formatado()} no inventário."); time.sleep(2); break
                    else: print("Seu inventário de poções está cheio!"); time.sleep(2)
            elif escolha == len(recompensas) + 1: print("Você decide não levar nenhum tesouro."); time.sleep(2); break
            else: print("Escolha inválida.")
        except ValueError: print("Por favor, digite um número.")

def iniciar_batalha(jogador, inimigo):
    limpar_tela(); print(f"⚔️  Um {inimigo.nome} apareceu! ⚔️"); time.sleep(2)
    while jogador.esta_vivo() and inimigo.esta_vivo():
        limpar_tela(); print(f"--- BATALHA: {jogador.nome} vs {inimigo.nome} ---"); jogador.mostrar_status(); print("\nVS\n"); inimigo.mostrar_status()
        
        jogador.processar_efeitos_e_buffs()
        if not jogador.esta_vivo(): break

        turno_usado = False
        while not turno_usado:
            print("\nSua vez de agir!"); acao = input("1. Atacar\n2. Usar Poção\n3. Tentar Fugir\n4. Ver Status Detalhado\n> ")
            if acao == "1":
                if menu_de_ataque(jogador, inimigo): turno_usado = True
            elif acao == "2": 
                if usar_pocao_em_batalha(jogador): turno_usado = True
            elif acao == "3":
                chance_fuga = 50 + (jogador.agilidade - inimigo.agilidade); chance_fuga = max(10, min(90, chance_fuga))
                print(f"\nTentando fugir... (Chance: {chance_fuga:.1f}%)"); time.sleep(1)
                if random.randint(1, 100) <= chance_fuga: print("...Você conseguiu escapar!"); time.sleep(2); return "fugiu"
                else: 
                    print("...A fuga falhou!"); turno_usado = True
                    if random.random() < CHANCE_QUEBRA_AO_FUGIR:
                            itens_equipados = [s for s, e in jogador.equipamentos.items() if e]
                            if itens_equipados: slot_quebrado = random.choice(itens_equipados); print(f"🔥 Oh não! Seu item '{jogador.equipamentos[slot_quebrado].nome_formatado()}' foi destruído!"); jogador.equipamentos[slot_quebrado] = None; time.sleep(2)
            elif acao == "4": jogador.mostrar_status_completo(); input("\nPressione ENTER para continuar..."); limpar_tela(); jogador.mostrar_status(); print("\nVS\n"); inimigo.mostrar_status()
            else: print("Ação inválida.")
        
        if not inimigo.esta_vivo(): break

        inimigo.processar_efeitos_e_buffs()
        if not inimigo.esta_vivo(): break

        inimigo.atacar(jogador)
        if not jogador.esta_vivo(): break
    
    if jogador.esta_vivo(): 
        jogador.buffs_ativos = {}; jogador.efeitos_status = {}
        print(f"\nVocê venceu a batalha contra {inimigo.nome}!"); time.sleep(1); xp_ganho = inimigo.nivel * 5 + random.randint(1, 5); jogador.ganhar_xp(xp_ganho); tela_de_recompensa(jogador); return "vitoria"
    else: return "derrota"

def iniciar_masmorra(jogador, andares_base=3):
    total_andares = andares_base
    for andar_atual in range(1, total_andares + 1):
        limpar_tela(); print(f"--- MASMORRA - ANDAR {andar_atual}/{total_andares} ---"); inimigo = gerar_inimigo(jogador.nivel); input("Pressione ENTER para prosseguir..."); resultado_batalha = iniciar_batalha(jogador, inimigo)
        if resultado_batalha in ["derrota", "fugiu"]: return resultado_batalha
    
    limpar_tela(); print(f"--- ANDAR FINAL - O Covil do Chefe ---"); chefe = gerar_chefe(jogador.nivel); input("Pressione ENTER para enfrentar o desafio final..."); resultado_chefe = iniciar_batalha(jogador, chefe)
    return "venceu_masmorra" if resultado_chefe == "vitoria" else "perdeu_masmorra"

def main():
    heroi_selecionado = None; vidas_heroi = 3; andares_masmorra = 3
    while True:
        limpar_tela(); print("====== RPG DE MASMORRA ======"); print(f"Vidas restantes: {'❤️' * vidas_heroi if vidas_heroi > 0 else '☠️'}")
        if heroi_selecionado: print(f"Herói Ativo: {heroi_selecionado.nome} - {heroi_selecionado.classe.capitalize()} (Nível {heroi_selecionado.nivel})")
        print("\n1. Criar Novo Herói\n2. Selecionar Herói Existente");
        if heroi_selecionado and vidas_heroi > 0: print("3. Entrar na Masmorra")
        print("4. Sair do Jogo")
        
        escolha = input("> ")
        if escolha == '1': heroi_selecionado = criar_novo_heroi()
        elif escolha == '2': heroi_selecionado = selecionar_heroi()
        elif escolha == '3' and heroi_selecionado and vidas_heroi > 0:
            while vidas_heroi > 0:
                heroi_selecionado.vida_atual = heroi_selecionado.vida_maxima; heroi_selecionado.caos_atual = heroi_selecionado.caos_maximo; heroi_selecionado.buffs_ativos = {}; heroi_selecionado.efeitos_status = {}
                resultado_final = iniciar_masmorra(heroi_selecionado, andares_masmorra)
                
                if resultado_final in ["derrota", "perdeu_masmorra"]:
                    vidas_heroi -= 1; xp_perdido = heroi_selecionado.xp_atual * PENALIDADE_XP_MORTE; heroi_selecionado.xp_atual -= xp_perdido
                    print(f"Você foi derrotado... Perdeu uma vida e {xp_perdido:.0f} de XP.")
                    if vidas_heroi <= 0: print("GAME OVER."); time.sleep(4); break
                    else: print(f"Você tem {vidas_heroi} vidas restantes."); time.sleep(4); break
                
                elif resultado_final == "fugiu":
                    xp_perdido = (heroi_selecionado.xp_atual * PENALIDADE_XP_MORTE) / 2
                    heroi_selecionado.xp_atual -= xp_perdido
                    print(f"Você fugiu da masmorra, perdendo {xp_perdido:.0f} de XP."); time.sleep(4); break

                elif resultado_final == "venceu_masmorra": 
                    print("\n🏆🏆🏆 VOCÊ CONQUISTOU A MASMORRA! 🏆🏆🏆"); time.sleep(2)
                    andares_masmorra += 1
                    print(f"A próxima masmorra terá {andares_masmorra} andares. Prepare-se!"); time.sleep(4)

        elif escolha == '4': print("Obrigado por jogar!"); break
        else: print("Opção inválida!"); time.sleep(1)

if __name__ == "__main__":
    main()