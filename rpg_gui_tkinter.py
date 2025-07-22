# rpg_gui_tkinter.py
import tkinter as tk
from tkinter import messagebox, simpledialog, font
import rpg_dinamico  # Your game logic file
import traceback

class RPGApp:
    """
    The main application class for the Tkinter RPG.
    Manages all windows, game state, and hero data.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("RPG de Masmorra Dinâmica")
        self.master.geometry("500x450")
        self.master.configure(bg="#2d2d2d")

        # --- Game State ---
        self.heroi_selecionado = None
        self.vidas_heroi = 3
        
        # --- Battle State ---
        self.batalha_win = None
        self.log_text_widget = None
        self.heroi_stats_label = None
        self.inimigo_stats_label = None
        self.inimigo_atual = None
        self.botoes_acao_frame = None

        # --- Dungeon State ---
        self.andar_atual = 0
        self.total_andares = 0

        # --- Styling ---
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Helvetica", size=11)
        self.title_font = ("Helvetica", 20, "bold")
        self.button_font = ("Helvetica", 12)
        self.label_font = ("Helvetica", 12)
        self.stats_font = ("Consolas", 12) # Monospaced font for better alignment

        self.main_frame = tk.Frame(master, bg="#2d2d2d")
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        self.tela_inicial()

    def limpar_tela(self):
        """Destroys all widgets in the main frame to prepare for a new screen."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def tela_inicial(self):
        """Displays the main menu screen."""
        self.limpar_tela()

        tk.Label(self.main_frame, text="RPG de Masmorra", font=self.title_font, fg="white", bg="#2d2d2d").pack(pady=(0, 20))
        
        vidas_texto = "❤️ " * self.vidas_heroi if self.vidas_heroi > 0 else "☠️ GAME OVER"
        tk.Label(self.main_frame, text=f"Vidas restantes: {vidas_texto}", font=self.stats_font, fg="white", bg="#2d2d2d").pack(pady=5)

        if self.heroi_selecionado:
            hero_info = f"Herói Ativo: {self.heroi_selecionado.nome} - {self.heroi_selecionado.classe} (Nível {self.heroi_selecionado.nivel})"
            tk.Label(self.main_frame, text=hero_info, font=self.label_font, fg="#aaffaa", bg="#2d2d2d").pack(pady=10)

        # --- Button Frame ---
        button_frame = tk.Frame(self.main_frame, bg="#2d2d2d")
        button_frame.pack(pady=10)

        btn_style = {'font': self.button_font, 'bg': '#4a4a4a', 'fg': 'white', 'activebackground': '#6a6a6a', 'activeforeground': 'white', 'width': 25, 'pady': 5, 'relief': 'raised', 'bd': 2}

        tk.Button(button_frame, text="Criar Novo Herói", command=self.tela_criar_heroi, **btn_style).pack(pady=5)
        tk.Button(button_frame, text="Selecionar Herói", command=self.tela_selecionar_heroi, **btn_style).pack(pady=5)

        if self.heroi_selecionado and self.vidas_heroi > 0:
            dungeon_btn_style = btn_style.copy()
            dungeon_btn_style['fg'] = "#aaffaa"
            tk.Button(button_frame, text="Entrar na Masmorra", command=self.iniciar_masmorra, **dungeon_btn_style).pack(pady=5)
        else:
            disabled_btn_style = btn_style.copy()
            disabled_btn_style['state'] = 'disabled'
            disabled_btn_style['bg'] = '#3a3a3a'
            tk.Button(button_frame, text="Entrar na Masmorra", **disabled_btn_style).pack(pady=5)

        exit_btn_style = btn_style.copy()
        exit_btn_style['fg'] = "#ffaaaa"
        tk.Button(button_frame, text="Sair do Jogo", command=self.master.quit, **exit_btn_style).pack(pady=10)

    def tela_criar_heroi(self):
        """Handles the hero creation process in a new window."""
        popup = tk.Toplevel(self.master)
        popup.title("Criação de Herói")
        popup.geometry("400x300")
        popup.configure(bg="#3d3d3d")

        tk.Label(popup, text="Nome do Herói:", fg="white", bg="#3d3d3d", font=self.label_font).pack(pady=(10,0))
        nome_entry = tk.Entry(popup, width=30, font=self.label_font)
        nome_entry.pack()

        tk.Label(popup, text="Escolha sua Classe:", fg="white", bg="#3d3d3d", font=self.label_font).pack(pady=(10,0))
        classe_var = tk.StringVar(popup)
        classes = list(rpg_dinamico.CLASSES_BASE.keys())
        classe_var.set(classes[0])
        
        for classe in classes:
            tk.Radiobutton(popup, text=f"{classe} - {rpg_dinamico.CLASSES_BASE[classe]['desc']}", variable=classe_var, value=classe, 
                           wraplength=350, justify='left', anchor='w', fg="white", bg="#3d3d3d", selectcolor="#5d5d5d", 
                           activebackground="#3d3d3d", activeforeground="white", font=self.default_font).pack(padx=20, fill='x')

        def confirmar_criacao():
            nome = nome_entry.get().strip()
            if not nome:
                messagebox.showerror("Erro", "O nome do herói não pode ser vazio.", parent=popup)
                return
            if nome in rpg_dinamico.HEROIS_CRIADOS:
                messagebox.showerror("Erro", "Já existe um herói com esse nome.", parent=popup)
                return

            classe = classe_var.get()
            stats_iniciais = rpg_dinamico.CLASSES_BASE[classe]["stats"]
            novo_heroi = rpg_dinamico.Heroi(nome, classe, **stats_iniciais)
            
            popup.destroy()
            self.tela_distribuir_pontos(novo_heroi, rpg_dinamico.PONTOS_DISTRIBUICAO_INICIAL, is_creation=True)

        tk.Button(popup, text="Confirmar", command=confirmar_criacao, font=self.button_font, bg='#4a4a4a', fg='white').pack(pady=20)

    def tela_distribuir_pontos(self, heroi, pontos, is_creation=False):
        """Opens a window to distribute attribute points."""
        popup = tk.Toplevel(self.master)
        popup.title("Distribuir Pontos de Atributo")
        popup.configure(bg="#3d3d3d")

        pontos_restantes = tk.IntVar(value=pontos)
        
        stats_vars = {
            "forca_base": tk.IntVar(value=0),
            "defesa_base": tk.IntVar(value=0),
            "agilidade_base": tk.IntVar(value=0)
        }

        def update_pontos_label(*args):
            gastos = sum(var.get() for var in stats_vars.values())
            pontos_restantes.set(pontos - gastos)
            pontos_label.config(text=f"Pontos restantes: {pontos_restantes.get()}")

        for var in stats_vars.values():
            var.trace_add("write", update_pontos_label)

        tk.Label(popup, text=f"Você tem {pontos} pontos para distribuir.", fg="white", bg="#3d3d3d", font=self.label_font).pack(pady=10)
        pontos_label = tk.Label(popup, text=f"Pontos restantes: {pontos}", fg="white", bg="#3d3d3d", font=self.label_font)
        pontos_label.pack(pady=5)

        for stat, var in stats_vars.items():
            frame = tk.Frame(popup, bg="#3d3d3d")
            frame.pack(fill='x', padx=20, pady=5)
            tk.Label(frame, text=stat.replace('_base', '').capitalize(), fg="white", bg="#3d3d3d", width=10, anchor='w').pack(side='left')
            tk.Scale(frame, from_=0, to=pontos, variable=var, orient='horizontal', length=200, bg="#5d5d5d", fg="white", troughcolor="#2d2d2d").pack(side='left', expand=True, fill='x')

        def confirmar_pontos():
            if pontos_restantes.get() < 0:
                messagebox.showerror("Erro", "Você gastou pontos demais!", parent=popup)
                return
            
            heroi.forca_base += stats_vars["forca_base"].get()
            heroi.defesa_base += stats_vars["defesa_base"].get()
            heroi.agilidade_base += stats_vars["agilidade_base"].get()

            heroi.vida_atual = heroi.vida_maxima
            heroi.caos_atual = heroi.caos_maximo

            if is_creation:
                rpg_dinamico.HEROIS_CRIADOS[heroi.nome] = heroi
                self.heroi_selecionado = heroi
                messagebox.showinfo("Sucesso", f"Herói {heroi.nome} criado com sucesso!")
            else:
                messagebox.showinfo("Level Up!", f"{heroi.nome} alcançou o nível {heroi.nivel}!")

            popup.destroy()
            self.tela_inicial()

        tk.Button(popup, text="Confirmar", command=confirmar_pontos, font=self.button_font, bg='#4a4a4a', fg='white').pack(pady=20)
        popup.transient(self.master)
        popup.grab_set()
        self.master.wait_window(popup)

    def tela_selecionar_heroi(self):
        """Opens a window to select an existing hero."""
        if not rpg_dinamico.HEROIS_CRIADOS:
            messagebox.showinfo("Aviso", "Nenhum herói foi criado ainda. Crie um primeiro!")
            self.tela_criar_heroi()
            return

        popup = tk.Toplevel(self.master)
        popup.title("Selecionar Herói")
        popup.geometry("400x350")
        popup.configure(bg="#3d3d3d")

        tk.Label(popup, text="Escolha seu herói:", fg="white", bg="#3d3d3d", font=self.label_font).pack(pady=10)
        
        listbox_frame = tk.Frame(popup, bg="#3d3d3d")
        listbox_frame.pack(expand=True, fill='both', padx=20, pady=5)
        
        listbox = tk.Listbox(listbox_frame, font=self.label_font, bg="#2d2d2d", fg="white", selectbackground="#0078d7")
        listbox.pack(side='left', expand=True, fill='both')

        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical', command=listbox.yview)
        scrollbar.pack(side='right', fill='y')
        listbox.config(yscrollcommand=scrollbar.set)

        nomes_herois = list(rpg_dinamico.HEROIS_CRIADOS.keys())
        for nome in nomes_herois:
            heroi = rpg_dinamico.HEROIS_CRIADOS[nome]
            listbox.insert(tk.END, f"{heroi.nome} - {heroi.classe} (Nível {heroi.nivel})")

        def confirmar_selecao():
            selecionado = listbox.curselection()
            if not selecionado:
                messagebox.showerror("Erro", "Por favor, selecione um herói.", parent=popup)
                return
            
            nome_heroi_selecionado = nomes_herois[selecionado[0]]
            self.heroi_selecionado = rpg_dinamico.HEROIS_CRIADOS[nome_heroi_selecionado]
            popup.destroy()
            self.tela_inicial()

        tk.Button(popup, text="Selecionar", command=confirmar_selecao, font=self.button_font, bg='#4a4a4a', fg='white').pack(pady=10)

    def iniciar_masmorra(self):
        """Prepares the hero and starts the first floor of the dungeon."""
        jogador = self.heroi_selecionado
        jogador.vida_atual = jogador.vida_maxima
        jogador.caos_atual = jogador.caos_maximo
        jogador.buffs_ativos = {}

        self.andar_atual = 1
        self.total_andares = 2 + jogador.nivel
        
        messagebox.showinfo("Masmorra", f"Você entra na masmorra. Ela tem {self.total_andares} andares.")
        
        self.proximo_andar()

    def proximo_andar(self):
        """Proceeds to the next floor or the final boss."""
        jogador = self.heroi_selecionado
        if self.andar_atual > self.total_andares:
            self.inimigo_atual = rpg_dinamico.gerar_chefe(jogador.nivel)
            messagebox.showinfo("Chefe!", f"Você chegou ao andar final e encontra o chefe: {self.inimigo_atual.nome}!")
        else:
            self.inimigo_atual = rpg_dinamico.gerar_inimigo(jogador.nivel)
            messagebox.showinfo("Novo Andar", f"Andar {self.andar_atual}/{self.total_andares}\nUm {self.inimigo_atual.nome} apareceu!")
        
        self.iniciar_batalha_visual()

    def iniciar_batalha_visual(self):
        """Creates the battle window UI."""
        if self.batalha_win and self.batalha_win.winfo_exists():
            self.batalha_win.destroy()

        self.batalha_win = tk.Toplevel(self.master)
        self.batalha_win.title(f"Batalha contra {self.inimigo_atual.nome}")
        self.batalha_win.geometry("800x600")
        self.batalha_win.configure(bg="#2d2d2d")
        self.batalha_win.protocol("WM_DELETE_WINDOW", self.acao_fugir)

        jogador = self.heroi_selecionado
        inimigo = self.inimigo_atual

        heroi_frame = tk.Frame(self.batalha_win, bg="#3d3d3d", bd=2, relief='sunken')
        heroi_frame.pack(pady=10, padx=10, fill='x')
        tk.Label(heroi_frame, text=f"Herói: {jogador.nome} ({jogador.classe})", font=self.button_font, fg="white", bg="#3d3d3d").pack()
        self.heroi_stats_label = tk.Label(heroi_frame, text="", font=self.stats_font, fg="white", bg="#3d3d3d")
        self.heroi_stats_label.pack()

        inimigo_frame = tk.Frame(self.batalha_win, bg="#3d3d3d", bd=2, relief='sunken')
        inimigo_frame.pack(pady=10, padx=10, fill='x')
        tk.Label(inimigo_frame, text=f"Inimigo: {inimigo.nome}", font=self.button_font, fg="white", bg="#3d3d3d").pack()
        self.inimigo_stats_label = tk.Label(inimigo_frame, text="", font=self.stats_font, fg="white", bg="#3d3d3d")
        self.inimigo_stats_label.pack()

        log_frame = tk.Frame(self.batalha_win)
        log_frame.pack(pady=10, padx=10, expand=True, fill='both')
        self.log_text_widget = tk.Text(log_frame, height=10, width=80, bg="#1e1e1e", fg="white", font=self.stats_font, wrap='word')
        self.log_text_widget.pack(side='left', expand=True, fill='both')
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text_widget.config(yscrollcommand=scrollbar.set)

        self.botoes_acao_frame = tk.Frame(self.batalha_win, bg="#2d2d2d")
        self.botoes_acao_frame.pack(pady=10)
        
        btn_style = {'font': self.button_font, 'bg': '#4a4a4a', 'fg': 'white', 'width': 12, 'pady': 5}
        
        tk.Button(self.botoes_acao_frame, text="Atacar", command=self.acao_ataque, **btn_style).grid(row=0, column=0, padx=5)
        tk.Button(self.botoes_acao_frame, text="Habilidade", command=self.acao_habilidade, **btn_style).grid(row=0, column=1, padx=5)
        tk.Button(self.botoes_acao_frame, text="Poção", command=self.acao_pocao, **btn_style).grid(row=0, column=2, padx=5)
        tk.Button(self.botoes_acao_frame, text="Fugir", command=self.acao_fugir, **btn_style).grid(row=0, column=3, padx=5)
        tk.Button(self.botoes_acao_frame, text="Status", command=self.tela_mostrar_status, **btn_style).grid(row=0, column=4, padx=5)

        self.atualizar_status_batalha()
        self.log_batalha(f"A batalha contra {inimigo.nome} começa!")
        self.atualizar_botoes_acao()
        
        self.batalha_win.transient(self.master)
        self.batalha_win.grab_set()

    def tela_mostrar_status(self):
        """Displays a popup with the hero's detailed status. Does not take a turn."""
        popup = tk.Toplevel(self.batalha_win)
        popup.title(f"Status de {self.heroi_selecionado.nome}")
        popup.configure(bg="#3d3d3d")
        
        status_texto = self.heroi_selecionado.get_status_texto()

        text_frame = tk.Frame(popup, bg="#3d3d3d")
        text_frame.pack(expand=True, fill='both', padx=15, pady=15)

        status_widget = tk.Text(text_frame, bg="#1e1e1e", fg="white", font=self.stats_font, wrap='word', bd=0, highlightthickness=0)
        status_widget.insert(tk.END, status_texto)
        status_widget.config(state='disabled')
        status_widget.pack(side='left', expand=True, fill='both')

        scrollbar = tk.Scrollbar(text_frame, command=status_widget.yview)
        scrollbar.pack(side='right', fill='y')
        status_widget.config(yscrollcommand=scrollbar.set)

        tk.Button(popup, text="Fechar", command=popup.destroy, font=self.button_font, bg='#4a4a4a', fg='white').pack(pady=10)

        popup.transient(self.batalha_win)
        popup.grab_set()

    def atualizar_status_batalha(self):
        """Updates the hero and enemy stat labels in the battle window."""
        jogador = self.heroi_selecionado
        inimigo = self.inimigo_atual
        
        self.heroi_stats_label.config(text=f"❤️ {jogador.vida_atual:<5.1f} / {jogador.vida_maxima:.1f}   🔮 {jogador.caos_atual:<5.1f} / {jogador.caos_maximo:.1f}")
        self.inimigo_stats_label.config(text=f"❤️ {inimigo.vida_atual:<5.1f} / {inimigo.vida_maxima:.1f}")

    def log_batalha(self, msg):
        """Adds a message to the battle log."""
        if self.log_text_widget and self.log_text_widget.winfo_exists():
            self.log_text_widget.insert(tk.END, msg + "\n")
            self.log_text_widget.see(tk.END)

    def atualizar_botoes_acao(self):
        """Updates the state of action buttons based on game state."""
        if not self.botoes_acao_frame or not self.botoes_acao_frame.winfo_exists():
            return
        
        try:
            jogador = self.heroi_selecionado
            habilidade = rpg_dinamico.CLASSES_BASE[jogador.classe]['habilidade']
            
            btn_habilidade = self.botoes_acao_frame.grid_slaves(row=0, column=1)[0]
            btn_pocao = self.botoes_acao_frame.grid_slaves(row=0, column=2)[0]

            for child in self.botoes_acao_frame.winfo_children():
                child.config(state='normal')

            if jogador.caos_atual < habilidade['custo']:
                btn_habilidade.config(state='disabled')

            if not jogador.inventario_pocoes:
                btn_pocao.config(state='disabled')
        except (IndexError, tk.TclError):
            pass # Window or widgets might be closing

    def desabilitar_todos_botoes_acao(self):
        """Disables all action buttons, usually during an action."""
        if not self.botoes_acao_frame or not self.botoes_acao_frame.winfo_exists():
            return
        for child in self.botoes_acao_frame.winfo_children():
            child.config(state='disabled')

    def turno_jogador(self, acao_jogador):
        """A generic handler for a player's turn with error handling."""
        try:
            self.desabilitar_todos_botoes_acao()
            acao_jogador()
            self.atualizar_status_batalha()
            if self.verificar_fim_batalha():
                return
            self.master.after(1000, self.turno_inimigo)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro no turno do jogador:\n{e}")
            if self.batalha_win and self.batalha_win.winfo_exists():
                self.batalha_win.destroy()
            self.tela_inicial()

    def acao_ataque(self):
        self.turno_jogador(lambda: self.heroi_selecionado.atacar(self.inimigo_atual, self.log_batalha))

    def acao_habilidade(self):
        self.turno_jogador(lambda: self.heroi_selecionado.usar_habilidade(self.inimigo_atual, self.log_batalha))

    def acao_pocao(self):
        if not self.heroi_selecionado.inventario_pocoes:
            self.log_batalha("Você não tem nenhuma poção!")
            return

        popup = tk.Toplevel(self.batalha_win)
        popup.title("Usar Poção")
        popup.configure(bg="#3d3d3d")
        
        tk.Label(popup, text="Escolha uma poção para usar:", fg="white", bg="#3d3d3d").pack(pady=10)

        def usar(pocao, index):
            popup.destroy()
            self.turno_jogador(lambda: self.heroi_selecionado.usar_pocao(index, self.log_batalha))

        for i, pocao in enumerate(self.heroi_selecionado.inventario_pocoes):
            tk.Button(popup, text=str(pocao), command=lambda p=pocao, idx=i: usar(p, idx),
                      wraplength=380, justify='left', bg="#4a4a4a", fg="white").pack(fill='x', padx=10, pady=5)
        
        popup.transient(self.batalha_win)
        popup.grab_set()

    def acao_fugir(self):
        self.desabilitar_todos_botoes_acao()
        chance = 50 + (self.heroi_selecionado.agilidade - self.inimigo_atual.agilidade)
        if rpg_dinamico.random.randint(1, 100) <= chance:
            self.log_batalha("Você fugiu com sucesso!")
            self.master.after(1000, lambda: messagebox.showinfo("Fuga", "Você conseguiu escapar da batalha, mas não da masmorra."))
            self.master.after(1000, self.derrota_masmorra)
        else:
            self.log_batalha("Fuga falhou!")
            self.master.after(1000, self.turno_inimigo)

    def turno_inimigo(self):
        """Handles the enemy's turn with error handling."""
        try:
            if self.inimigo_atual.esta_vivo():
                self.log_batalha("-" * 20)
                self.inimigo_atual.atacar(self.heroi_selecionado, self.log_batalha)
                self.atualizar_status_batalha()
                if not self.verificar_fim_batalha():
                    self.atualizar_botoes_acao()
                    self.log_batalha("Sua vez de agir!")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro no turno do inimigo:\n{e}")
            if self.batalha_win and self.batalha_win.winfo_exists():
                self.batalha_win.destroy()
            self.tela_inicial()

    def verificar_fim_batalha(self):
        """Checks if the battle has ended and handles the outcome."""
        jogador = self.heroi_selecionado
        inimigo = self.inimigo_atual

        if not inimigo.esta_vivo():
            self.log_batalha(f"🎉 Você venceu a batalha contra {inimigo.nome}!")
            self.master.after(1000, self.vitoria_batalha)
            return True
        elif not jogador.esta_vivo():
            self.log_batalha("❌ Você foi derrotado!")
            self.master.after(1000, self.derrota_masmorra)
            return True
        return False

    def vitoria_batalha(self):
        """Handles the rewards and progression after winning a battle."""
        if self.batalha_win and self.batalha_win.winfo_exists():
            self.batalha_win.destroy()
        
        jogador = self.heroi_selecionado
        inimigo = self.inimigo_atual
        
        xp_ganho = inimigo.nivel * 5 + rpg_dinamico.random.randint(1, 5)
        nivel_antes = jogador.nivel
        jogador.ganhar_xp(xp_ganho, self.log_batalha)
        messagebox.showinfo("Vitória!", f"Você ganhou {xp_ganho} de XP!")
        
        if jogador.nivel > nivel_antes:
            self.tela_distribuir_pontos(jogador, rpg_dinamico.PONTOS_POR_NIVEL)
        
        self.mostrar_recompensa_visual()

    def derrota_masmorra(self):
        """Handles the consequences of losing a battle or fleeing."""
        if self.batalha_win and self.batalha_win.winfo_exists():
            self.batalha_win.destroy()

        self.vidas_heroi -= 1
        jogador = self.heroi_selecionado
        xp_perdido = jogador.xp_atual * rpg_dinamico.PENALIDADE_XP_MORTE
        jogador.xp_atual -= xp_perdido
        
        messagebox.showinfo("Derrota", f"Você foi derrotado na masmorra!\nPerdeu uma vida e {xp_perdido:.0f} de XP!")

        if self.vidas_heroi <= 0:
            messagebox.showwarning("Game Over", "GAME OVER. Suas vidas acabaram. Obrigado por jogar!")
            self.master.quit()
        else:
            self.tela_inicial()

    def vitoria_masmorra(self):
        """Handles winning the entire dungeon."""
        messagebox.showinfo("Vitória!", "🏆 Você conquistou a masmorra! 🏆\nO herói descansará e voltará mais forte.")
        self.tela_inicial()

    def mostrar_recompensa_visual(self):
        """Displays the reward selection window."""
        popup = tk.Toplevel(self.master)
        popup.title("Recompensa da Batalha")
        popup.configure(bg="#3d3d3d")
        
        jogador = self.heroi_selecionado
        tk.Label(popup, text="Escolha sua recompensa:", font=self.label_font, fg="white", bg="#3d3d3d").pack(pady=10)
        recompensas = [rpg_dinamico.gerar_recompensa_aleatoria(jogador.nivel) for _ in range(3)]

        def proximo_passo():
            popup.destroy()
            if self.andar_atual > self.total_andares:
                self.vitoria_masmorra()
            else:
                self.andar_atual += 1
                self.proximo_andar()

        def selecionar_item(item, button):
            button.config(state='disabled') # Disable button after selection
            if isinstance(item, rpg_dinamico.Equipamento):
                if messagebox.askyesno("Equipar Item?", f"Deseja equipar o novo item?\n\nNOVO: {item}\nATUAL: {jogador.equipamentos.get(item.slot) or 'Nada'}", parent=popup):
                    jogador.equipar_item(item, self.log_batalha)
                    messagebox.showinfo("Equipado", f"{item.nome_formatado()} foi equipado.", parent=popup)
                else:
                    messagebox.showinfo("Item Ignorado", "Você decidiu não equipar o item.", parent=popup)

            elif isinstance(item, rpg_dinamico.Pocao):
                if len(jogador.inventario_pocoes) < rpg_dinamico.MAX_POCOES_INVENTARIO:
                    jogador.inventario_pocoes.append(item)
                    messagebox.showinfo("Poção", f"{item.nome_formatado()} adicionada ao inventário.", parent=popup)
                else:
                    messagebox.showwarning("Inventário cheio", "Seu inventário de poções está cheio!", parent=popup)
            
            proximo_passo()

        for item in recompensas:
            btn = tk.Button(popup, text=str(item), wraplength=380, justify='left', bg="#4a4a4a", fg="white")
            btn.config(command=lambda i=item, b=btn: selecionar_item(i, b))
            btn.pack(fill='x', padx=10, pady=5)

        tk.Button(popup, text="Não quero nenhum item.", command=proximo_passo, bg="#4a4a4a", fg="white").pack(pady=10)

        popup.protocol("WM_DELETE_WINDOW", proximo_passo)
        popup.transient(self.master)
        popup.grab_set()
        self.master.wait_window(popup)

if __name__ == "__main__":
    def patch_rpg_dinamico():
        """
        Modifies the rpg_dinamico classes in memory to accept a logging function,
        avoiding the need to change the original file. This makes the logic
        compatible with the GUI without altering the console version.
        """
        def patched_nome_formatado(self):
            icone = "✨" if self.raridade == "raro" else "🔹" if self.raridade == "incomum" else ""
            return f"{self.nome} [{self.raridade.capitalize()}] {icone}".strip()
        rpg_dinamico.Item.nome_formatado = patched_nome_formatado

        def patched_get_status_texto(self):
            status_lines = []
            status_lines.append(f"--- STATUS: {self.nome} - O {self.classe.capitalize()} (Nível {self.nivel}) ---")
            status_lines.append(f"❤️ Vida: {self.vida_atual:.1f} / {self.vida_maxima:.1f}")
            status_lines.append(f"🔮 Caos: {self.caos_atual:.1f} / {self.caos_maximo:.1f}")
            
            if self.nivel < 5:
                status_lines.append(f"📊 XP: {self.xp_atual:.0f} / {self.xp_proximo_nivel}")
            else:
                status_lines.append("📊 XP: MÁXIMO")

            status_lines.append("\n--- Atributos Totais (com Equipamentos) ---")
            status_lines.append(f"💪 Força: {self.forca:.1f} | 🛡️ Defesa: {self.defesa:.1f} | 👟 Agilidade: {self.agilidade:.1f}")

            status_lines.append("\n--- Equipamentos ---")
            for slot, item in self.equipamentos.items():
                item_str = item.nome_formatado() if item else 'Vazio'
                status_lines.append(f"   - {slot.capitalize()}: {item_str}")

            status_lines.append("\n--- Inventário de Poções ---")
            if self.inventario_pocoes:
                for pocao in self.inventario_pocoes:
                    status_lines.append(f"   - {pocao}")
            else:
                status_lines.append("   Vazio")
            
            if self.buffs_ativos:
                status_lines.append("\n--- Buffs Ativos ---")
                buff_str = ", ".join([f"{data['valor']:.1f} {tipo.upper()} ({data['turnos_restantes']}t)" for tipo, data in self.buffs_ativos.items()])
                status_lines.append(f"   {buff_str}")

            return "\n".join(status_lines)
        rpg_dinamico.Heroi.get_status_texto = patched_get_status_texto

        def patched_atacar_personagem(self, alvo, logger=print):
            logger(f"\n💥 {self.nome} usa um Ataque Básico contra {alvo.nome}!")
            chance_acerto = 90 - (alvo.agilidade - self.agilidade)
            chance_acerto = max(20, min(100, chance_acerto))
            if rpg_dinamico.random.randint(1, 100) > chance_acerto:
                logger(f"   💨 ERROU!")
                return
            reducao_de_dano = alvo.defesa * 0.3
            dano = max(1.0, self.forca - reducao_de_dano)
            logger(f"   🎯 Acertou! Dano Físico causado: {dano:.1f}!")
            alvo.receber_dano(dano)
        rpg_dinamico.Personagem.atacar = patched_atacar_personagem

        def patched_usar_habilidade(self, alvo, logger=print):
            habilidade = rpg_dinamico.CLASSES_BASE[self.classe]['habilidade']
            custo = habilidade['custo']
            if self.caos_atual < custo:
                logger("Caos insuficiente para usar esta habilidade!")
                return False
            self.caos_atual -= custo
            multiplicador = habilidade['multiplicador'] + self.proficiencia
            dano_magico = self.forca * multiplicador
            logger(f"\n✨ {self.nome} usa {habilidade['nome']}!")
            logger(f"   Dano Mágico causado: {dano_magico:.1f}! (Ignora defesa)")
            alvo.receber_dano(dano_magico)
            return True
        rpg_dinamico.Heroi.usar_habilidade = patched_usar_habilidade

        def patched_usar_pocao(self, pocao_index, logger=print):
            pocao = self.inventario_pocoes.pop(pocao_index)
            logger(f"\nVocê usou {pocao.nome_formatado()}!")
            if pocao.tipo == 'cura':
                vida_curada = min(self.vida_maxima - self.vida_atual, pocao.valor)
                self.vida_atual += vida_curada
                logger(f"   Você recuperou {vida_curada:.1f} de vida.")
            else:
                tipo_buff = pocao.tipo.split('_')[1]
                self.buffs_ativos[tipo_buff] = {'valor': pocao.valor, 'turnos_restantes': pocao.duracao + 1}
                logger(f"   Seu atributo {tipo_buff.upper()} aumentou em {pocao.valor:.1f} por {pocao.duracao} turnos!")
        rpg_dinamico.Heroi.usar_pocao = patched_usar_pocao
        
        def patched_ganhar_xp(self, quantidade, logger=print):
            if self.nivel >= 5: return
            self.xp_atual += quantidade
            logger(f"✨ Você ganhou {quantidade} de XP! ({self.xp_atual:.0f}/{self.xp_proximo_nivel})")
            while self.xp_atual >= self.xp_proximo_nivel and self.nivel < 5:
                xp_excedente = self.xp_atual - self.xp_proximo_nivel
                self.nivel += 1
                self.xp_atual = xp_excedente
                self.xp_proximo_nivel = rpg_dinamico.XP_PARA_NIVEL.get(self.nivel, float('inf'))
                self.proficiencia += 0.05
                self.vida_base += 2
                self.caos_base += 2
                logger(f"🎉🎉🎉 LEVEL UP! Você alcançou o Nível {self.nivel}! 🎉🎉🎉")
        rpg_dinamico.Heroi.ganhar_xp = patched_ganhar_xp

        def patched_equipar_item(self, novo_equip, logger=print):
            item_atual = self.equipamentos[novo_equip.slot]
            bonus_vida_antigo = item_atual.bonus_vida if item_atual else 0.0
            bonus_caos_antigo = item_atual.bonus_caos if item_atual else 0.0
            if item_atual:
                logger(f"   Substituindo {item_atual.nome_formatado()}...")
            self.equipamentos[novo_equip.slot] = novo_equip
            delta_vida = novo_equip.bonus_vida - bonus_vida_antigo
            delta_caos = novo_equip.bonus_caos - bonus_caos_antigo
            self.vida_atual += delta_vida
            self.caos_atual += delta_caos
            self.vida_atual = min(self.vida_maxima, self.vida_atual)
            self.caos_atual = min(self.caos_maximo, self.caos_atual)
            logger(f"   {self.nome} equipou {novo_equip.nome_formatado()}.")
        rpg_dinamico.Heroi.equipar_item = patched_equipar_item

    patch_rpg_dinamico()
    root = tk.Tk()
    app = RPGApp(root)
    root.mainloop()