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
        self.master.state('zoomed') 

        # --- Cores e Estilo ---
        self.colors = {
            "bg_main": "#282c34",
            "bg_frame": "#3c4049",
            "bg_widget": "#21252b",
            "fg_normal": "#abb2bf",
            "fg_title": "#61afef",
            "fg_success": "#98c379",
            "fg_danger": "#e06c75",
            "accent": "#c678dd",
            "disabled": "#5c6370"
        }
        self.master.configure(bg=self.colors["bg_main"])

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
        self.total_andares = 3 # Começa com 3 andares

        # --- Styling ---
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=10)
        self.title_font = ("Segoe UI", 20, "bold")
        self.button_font = ("Segoe UI", 12)
        self.label_font = ("Segoe UI", 12)
        self.stats_font = ("Consolas", 11)

        self.main_frame = tk.Frame(master, bg=self.colors["bg_main"])
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        self.tela_inicial()

    def limpar_tela(self):
        """Destroys all widgets in the main frame to prepare for a new screen."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def tela_inicial(self):
        """Displays the main menu screen."""
        self.limpar_tela()

        tk.Label(self.main_frame, text="RPG de Masmorra", font=self.title_font, fg=self.colors["fg_title"], bg=self.colors["bg_main"]).pack(pady=(0, 20))
        
        vidas_texto = "❤️ " * self.vidas_heroi if self.vidas_heroi > 0 else "☠️ GAME OVER"
        tk.Label(self.main_frame, text=f"Vidas restantes: {vidas_texto}", font=self.stats_font, fg=self.colors["fg_normal"], bg=self.colors["bg_main"]).pack(pady=5)

        if self.heroi_selecionado:
            hero_info = f"Herói Ativo: {self.heroi_selecionado.nome} - {self.heroi_selecionado.classe} (Nível {self.heroi_selecionado.nivel})"
            tk.Label(self.main_frame, text=hero_info, font=self.label_font, fg=self.colors["fg_success"], bg=self.colors["bg_main"]).pack(pady=10)

        button_frame = tk.Frame(self.main_frame, bg=self.colors["bg_main"])
        button_frame.pack(pady=10)

        btn_style = {'font': self.button_font, 'bg': self.colors["bg_frame"], 'fg': self.colors["fg_normal"], 'activebackground': self.colors["accent"], 'activeforeground': 'white', 'width': 25, 'pady': 5, 'relief': 'flat', 'bd': 0}

        tk.Button(button_frame, text="Criar Novo Herói", command=self.tela_criar_heroi, **btn_style).pack(pady=5)
        tk.Button(button_frame, text="Selecionar Herói", command=self.tela_selecionar_heroi, **btn_style).pack(pady=5)

        if self.heroi_selecionado and self.vidas_heroi > 0:
            dungeon_btn_style = btn_style.copy()
            dungeon_btn_style['fg'] = self.colors["fg_success"]
            tk.Button(button_frame, text="Entrar na Masmorra", command=self.iniciar_masmorra, **dungeon_btn_style).pack(pady=5)
        else:
            disabled_btn_style = btn_style.copy()
            disabled_btn_style['state'] = 'disabled'
            disabled_btn_style['bg'] = self.colors["bg_widget"]
            disabled_btn_style['fg'] = self.colors["disabled"]
            tk.Button(button_frame, text="Entrar na Masmorra", **disabled_btn_style).pack(pady=5)

        exit_btn_style = btn_style.copy()
        exit_btn_style['fg'] = self.colors["fg_danger"]
        tk.Button(button_frame, text="Sair do Jogo", command=self.master.quit, **exit_btn_style).pack(pady=10)

    def tela_criar_heroi(self):
        """Handles the hero creation process in a new window."""
        popup = tk.Toplevel(self.master)
        popup.title("Criação de Herói")
        popup.geometry("450x400")
        popup.configure(bg=self.colors["bg_frame"])

        tk.Label(popup, text="Nome do Herói:", fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], font=self.label_font).pack(pady=(10,0))
        nome_entry = tk.Entry(popup, width=30, font=self.label_font, bg=self.colors["bg_widget"], fg=self.colors["fg_normal"], insertbackground='white', relief='flat')
        nome_entry.pack()

        tk.Label(popup, text="Escolha sua Classe:", fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], font=self.label_font).pack(pady=(10,0))
        classe_var = tk.StringVar(popup)
        classes = list(rpg_dinamico.CLASSES_BASE.keys())
        classe_var.set(classes[0])
        
        for classe in classes:
            tk.Radiobutton(popup, text=f"{classe} - {rpg_dinamico.CLASSES_BASE[classe]['desc']}", variable=classe_var, value=classe, 
                           wraplength=350, justify='left', anchor='w', fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], selectcolor=self.colors["bg_widget"], 
                           activebackground=self.colors["bg_frame"], activeforeground=self.colors["fg_title"], font=self.default_font, indicatoron=0, relief='flat', highlightthickness=0).pack(padx=20, fill='x', pady=2)

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

        tk.Button(popup, text="Confirmar", command=confirmar_criacao, font=self.button_font, bg=self.colors["accent"], fg='white', relief='flat').pack(pady=20)

    def tela_distribuir_pontos(self, heroi, pontos, is_creation=False, on_close_callback=None):
        """Opens a window to distribute attribute points."""
        popup = tk.Toplevel(self.master)
        popup.title("Distribuir Pontos de Atributo")
        popup.geometry("500x300")
        popup.configure(bg=self.colors["bg_frame"])

        pontos_restantes = tk.IntVar(value=pontos)
        
        stats_vars = {
            "forca_base": tk.IntVar(value=0),
            "defesa_base": tk.IntVar(value=0),
            "agilidade_base": tk.IntVar(value=0)
        }

        def update_pontos_label(*args):
            gastos = sum(var.get() for var in stats_vars.values())
            restantes = pontos - gastos
            pontos_restantes.set(restantes)
            pontos_label.config(text=f"Pontos restantes: {restantes}")
            if restantes < 0:
                pontos_label.config(fg=self.colors["fg_danger"])
            else:
                pontos_label.config(fg=self.colors["fg_normal"])

        for var in stats_vars.values():
            var.trace_add("write", update_pontos_label)

        tk.Label(popup, text=f"Você tem {pontos} pontos para distribuir.", fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], font=self.label_font).pack(pady=10)
        pontos_label = tk.Label(popup, text=f"Pontos restantes: {pontos}", fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], font=self.label_font)
        pontos_label.pack(pady=5)

        for stat, var in stats_vars.items():
            frame = tk.Frame(popup, bg=self.colors["bg_frame"])
            frame.pack(fill='x', padx=20, pady=5)
            tk.Label(frame, text=stat.replace('_base', '').capitalize(), fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], width=10, anchor='w').pack(side='left')
            tk.Scale(frame, from_=0, to=pontos, variable=var, orient='horizontal', length=200, bg=self.colors["disabled"], fg=self.colors["fg_title"], troughcolor=self.colors["bg_widget"], highlightthickness=0, relief='flat').pack(side='left', expand=True, fill='x')

        def confirmar_pontos():
            gastos = sum(var.get() for var in stats_vars.values())
            if gastos > pontos:
                messagebox.showerror("Erro", f"Você só pode distribuir {pontos} pontos, mas tentou usar {gastos}!", parent=popup)
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
            
            popup.destroy()

            if on_close_callback:
                on_close_callback()
            else:
                self.tela_inicial()

        tk.Button(popup, text="Confirmar", command=confirmar_pontos, font=self.button_font, bg=self.colors["accent"], fg='white', relief='flat').pack(pady=20)
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
        popup.geometry("700x450")
        popup.configure(bg=self.colors["bg_frame"])

        tk.Label(popup, text="Escolha seu herói:", fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], font=self.label_font).pack(pady=10)
        
        main_frame = tk.Frame(popup, bg=self.colors["bg_frame"])
        main_frame.pack(expand=True, fill='both', padx=10, pady=5)

        listbox_frame = tk.Frame(main_frame, bg=self.colors["bg_frame"])
        listbox_frame.pack(side='left', expand=True, fill='both', padx=(0, 5))
        
        listbox = tk.Listbox(listbox_frame, font=self.label_font, bg=self.colors["bg_widget"], fg=self.colors["fg_normal"], selectbackground=self.colors["accent"], exportselection=False, relief='flat', highlightthickness=0)
        listbox.pack(side='left', expand=True, fill='both')

        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical', command=listbox.yview, relief='flat')
        scrollbar.pack(side='right', fill='y')
        listbox.config(yscrollcommand=scrollbar.set)

        status_frame = tk.Frame(main_frame, bg=self.colors["bg_widget"])
        status_frame.pack(side='right', expand=True, fill='both', padx=(5, 0))
        
        status_text = tk.Text(status_frame, bg=self.colors["bg_widget"], fg=self.colors["fg_normal"], font=self.stats_font, wrap='word', bd=0, highlightthickness=0)
        status_text.pack(expand=True, fill='both', padx=10, pady=10)
        status_text.insert(tk.END, "Selecione um herói para ver os detalhes.")
        status_text.config(state='disabled')

        nomes_herois = list(rpg_dinamico.HEROIS_CRIADOS.keys())
        for nome in nomes_herois:
            heroi = rpg_dinamico.HEROIS_CRIADOS[nome]
            listbox.insert(tk.END, f"{heroi.nome} - {heroi.classe} (Nível {heroi.nivel})")

        btn_confirmar = tk.Button(popup, text="Selecionar", font=self.button_font, bg=self.colors["accent"], fg='white', relief='flat', state='disabled')
        
        def on_hero_select(event):
            if not listbox.curselection(): return
            
            nome_heroi = nomes_herois[listbox.curselection()[0]]
            heroi = rpg_dinamico.HEROIS_CRIADOS[nome_heroi]
            
            status_text.config(state='normal')
            status_text.delete('1.0', tk.END)
            status_text.insert(tk.END, heroi.get_status_texto_com_itens())
            status_text.config(state='disabled')
            btn_confirmar.config(state='normal')

        listbox.bind('<<ListboxSelect>>', on_hero_select)

        def confirmar_selecao():
            if not listbox.curselection():
                messagebox.showerror("Erro", "Por favor, selecione um herói.", parent=popup)
                return
            
            nome_heroi_selecionado = nomes_herois[listbox.curselection()[0]]
            self.heroi_selecionado = rpg_dinamico.HEROIS_CRIADOS[nome_heroi_selecionado]
            popup.destroy()
            self.tela_inicial()

        btn_confirmar.config(command=confirmar_selecao)
        btn_confirmar.pack(pady=10)

    def iniciar_masmorra(self):
        """Prepares the hero and starts the first floor of the dungeon."""
        jogador = self.heroi_selecionado
        jogador.vida_atual = jogador.vida_maxima
        jogador.caos_atual = jogador.caos_maximo
        jogador.buffs_ativos = {}
        jogador.efeitos_status = {}

        self.andar_atual = 1
        
        messagebox.showinfo("Masmorra", f"Você entra na masmorra. Ela tem {self.total_andares} andares antes do chefe.")
        
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
        self.batalha_win.geometry("1280x720")
        self.batalha_win.configure(bg=self.colors["bg_main"])
        self.batalha_win.protocol("WM_DELETE_WINDOW", self.acao_fugir)

        # --- Layout Responsivo ---
        stats_frame = tk.Frame(self.batalha_win, bg=self.colors["bg_main"])
        stats_frame.pack(side='top', fill='x', padx=10, pady=10)
        
        self.botoes_acao_frame = tk.Frame(self.batalha_win, bg=self.colors["bg_main"])
        self.botoes_acao_frame.pack(side='bottom', fill='x', pady=20) # Posição ajustada
        
        log_frame = tk.Frame(self.batalha_win, bg=self.colors["bg_widget"])
        log_frame.pack(side='top', expand=True, fill='both', padx=10, pady=10)

        # --- Painéis de Status ---
        heroi_frame = tk.Frame(stats_frame, bg=self.colors["bg_frame"], bd=2, relief='sunken')
        heroi_frame.pack(side='left', expand=True, fill='x', padx=(0, 5))
        inimigo_frame = tk.Frame(stats_frame, bg=self.colors["bg_frame"], bd=2, relief='sunken')
        inimigo_frame.pack(side='right', expand=True, fill='x', padx=(5, 0))

        tk.Label(heroi_frame, text=f"Herói: {self.heroi_selecionado.nome} ({self.heroi_selecionado.classe})", font=self.button_font, fg=self.colors["fg_title"], bg=self.colors["bg_frame"]).pack()
        self.heroi_stats_label = tk.Label(heroi_frame, text="", font=self.stats_font, fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], justify='left')
        self.heroi_stats_label.pack(fill='x', padx=5, pady=5)

        tk.Label(inimigo_frame, text=f"Inimigo: {self.inimigo_atual.nome}", font=self.button_font, fg=self.colors["fg_danger"], bg=self.colors["bg_frame"]).pack()
        self.inimigo_stats_label = tk.Label(inimigo_frame, text="", font=self.stats_font, fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], justify='left')
        self.inimigo_stats_label.pack(fill='x', padx=5, pady=5)

        # --- Log de Batalha ---
        self.log_text_widget = tk.Text(log_frame, height=10, bg=self.colors["bg_widget"], fg=self.colors["fg_normal"], font=self.stats_font, wrap='word', bd=0)
        self.log_text_widget.pack(side='left', expand=True, fill='both', padx=5, pady=5)
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text_widget.yview, relief='flat', bg=self.colors["bg_widget"])
        scrollbar.pack(side='right', fill='y')
        self.log_text_widget.config(yscrollcommand=scrollbar.set)

        # --- Botões de Ação ---
        self.botoes_acao_frame.columnconfigure((0, 1, 2, 3, 4), weight=1) # Centraliza os botões
        btn_style = {'font': self.button_font, 'bg': self.colors["bg_frame"], 'fg': self.colors["fg_normal"], 'width': 12, 'pady': 5, 'relief':'flat'}
        
        tk.Button(self.botoes_acao_frame, text="Ataque Básico", command=self.acao_ataque, **btn_style).grid(row=0, column=0, padx=5)
        tk.Button(self.botoes_acao_frame, text="Habilidades", command=self.acao_habilidade_menu, **btn_style).grid(row=0, column=1, padx=5)
        tk.Button(self.botoes_acao_frame, text="Poção", command=self.acao_pocao, **btn_style).grid(row=0, column=2, padx=5)
        tk.Button(self.botoes_acao_frame, text="Fugir", command=self.acao_fugir, **btn_style).grid(row=0, column=3, padx=5)
        tk.Button(self.botoes_acao_frame, text="Status", command=self.tela_mostrar_status, **btn_style).grid(row=0, column=4, padx=5)

        self.turno_do_jogador_inicio()
        
        self.batalha_win.transient(self.master)
        self.batalha_win.grab_set()

    def tela_mostrar_status(self):
        """Displays a popup with the hero's detailed status. Does not take a turn."""
        popup = tk.Toplevel(self.batalha_win)
        popup.title(f"Status de {self.heroi_selecionado.nome}")
        popup.geometry("400x600")
        popup.configure(bg=self.colors["bg_frame"])
        
        status_texto = self.heroi_selecionado.get_status_texto_com_itens()

        text_frame = tk.Frame(popup, bg=self.colors["bg_widget"])
        text_frame.pack(expand=True, fill='both', padx=15, pady=15)

        status_widget = tk.Text(text_frame, bg=self.colors["bg_widget"], fg=self.colors["fg_normal"], font=self.stats_font, wrap='word', bd=0, highlightthickness=0)
        status_widget.insert(tk.END, status_texto)
        status_widget.config(state='disabled')
        status_widget.pack(side='left', expand=True, fill='both')

        scrollbar = tk.Scrollbar(text_frame, command=status_widget.yview, relief='flat')
        scrollbar.pack(side='right', fill='y')
        status_widget.config(yscrollcommand=scrollbar.set)

        tk.Button(popup, text="Fechar", command=popup.destroy, font=self.button_font, bg=self.colors["accent"], fg='white', relief='flat').pack(pady=10)

        popup.transient(self.batalha_win)
        popup.grab_set()

    def atualizar_status_batalha(self):
        """Updates the hero and enemy stat labels in the battle window."""
        jogador = self.heroi_selecionado
        inimigo = self.inimigo_atual
        
        heroi_status_lines = [
            f"❤️ {jogador.vida_atual:<5.1f} / {jogador.vida_maxima:.1f}",
            f"🔮 {jogador.caos_atual:<5.1f} / {jogador.caos_maximo:.1f}",
            f"💪 {jogador.forca:<5.1f}  🛡️ {jogador.defesa:<5.1f}  👟 {jogador.agilidade:<5.1f}"
        ]
        if jogador.buffs_ativos:
            heroi_status_lines.append(" ".join([f"⬆️{k[0].upper()}" for k in jogador.buffs_ativos.keys()]))
        if jogador.efeitos_status:
            heroi_status_lines.append(" ".join([f"⬇️{k[0].upper()}" for k in jogador.efeitos_status.keys()]))
        
        self.heroi_stats_label.config(text="\n".join(heroi_status_lines))
        
        inimigo_status_lines = [
            f"❤️ {inimigo.vida_atual:<5.1f} / {inimigo.vida_maxima:.1f}",
            f"💪 {inimigo.forca:<5.1f}  🛡️ {inimigo.defesa:<5.1f}  👟 {inimigo.agilidade:<5.1f}"
        ]
        if inimigo.efeitos_status:
            inimigo_status_lines.append(" ".join([f"⬇️{k[0].upper()}" for k in inimigo.efeitos_status.keys()]))

        self.inimigo_stats_label.config(text="\n".join(inimigo_status_lines))

    def log_batalha(self, msg):
        """Adds a message to the battle log."""
        if self.log_text_widget and self.log_text_widget.winfo_exists():
            self.log_text_widget.config(state='normal')
            self.log_text_widget.insert(tk.END, msg + "\n")
            self.log_text_widget.see(tk.END)
            self.log_text_widget.config(state='disabled')

    def atualizar_botoes_acao(self, state='normal'):
        """Updates the state of action buttons based on game state."""
        if not self.botoes_acao_frame or not self.botoes_acao_frame.winfo_exists():
            return
        
        try:
            for child in self.botoes_acao_frame.winfo_children():
                child.config(state=state)

            if state == 'normal':
                jogador = self.heroi_selecionado
                btn_habilidade = self.botoes_acao_frame.grid_slaves(row=0, column=1)[0]
                btn_pocao = self.botoes_acao_frame.grid_slaves(row=0, column=2)[0]

                if not rpg_dinamico.CLASSES_BASE[jogador.classe]['habilidades']:
                    btn_habilidade.config(state='disabled')
                if not jogador.inventario_pocoes:
                    btn_pocao.config(state='disabled')
        except (IndexError, tk.TclError):
            pass # Window or widgets might be closing

    def turno_do_jogador_inicio(self):
        """Processes start-of-turn effects for the player."""
        self.log_batalha("-" * 20)
        self.heroi_selecionado.processar_efeitos_e_buffs(self.log_batalha)
        self.atualizar_status_batalha()
        if self.verificar_fim_batalha(): return

        if 'congelado' in self.heroi_selecionado.efeitos_status:
            self.log_batalha(f"🥶 {self.heroi_selecionado.nome} está congelado e perde o turno!")
            self.master.after(1500, self.turno_inimigo)
        else:
            self.log_batalha("Sua vez de agir!")
            self.atualizar_botoes_acao('normal')


    def turno_jogador_fim(self, acao_jogador):
        """A generic handler for a player's turn with error handling."""
        try:
            self.atualizar_botoes_acao('disabled')
            acao_jogador() # Execute the chosen action
            self.atualizar_status_batalha()
            if self.verificar_fim_batalha():
                return
            self.master.after(1500, self.turno_inimigo)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro no turno do jogador:\n{e}")
            if self.batalha_win and self.batalha_win.winfo_exists():
                self.batalha_win.destroy()
            self.tela_inicial()

    def acao_ataque(self):
        self.turno_jogador_fim(lambda: self.heroi_selecionado.atacar(self.inimigo_atual, self.log_batalha))

    def acao_habilidade_menu(self):
        jogador = self.heroi_selecionado
        habilidades = rpg_dinamico.CLASSES_BASE[jogador.classe]['habilidades']

        popup = tk.Toplevel(self.batalha_win)
        popup.title("Escolher Habilidade")
        popup.geometry("500x300")
        popup.configure(bg=self.colors["bg_frame"])
        
        tk.Label(popup, text="Escolha uma habilidade:", fg=self.colors["fg_normal"], bg=self.colors["bg_frame"], font=self.label_font).pack(pady=10)

        def usar(habilidade):
            if jogador.caos_atual < habilidade['custo']:
                messagebox.showwarning("Sem Caos", "Você não tem Caos suficiente para usar esta habilidade.", parent=popup)
                return

            popup.destroy()
            self.turno_jogador_fim(lambda: jogador.usar_habilidade(self.inimigo_atual, habilidade, self.log_batalha))

        for hab in habilidades:
            btn_text = f"{hab['nome']} (Custo: {hab['custo']})\n{hab['desc']}"
            btn = tk.Button(popup, text=btn_text, command=lambda h=hab: usar(h),
                            wraplength=380, justify='left', bg=self.colors["bg_frame"], fg=self.colors["fg_normal"], font=self.default_font, relief='flat')
            if jogador.caos_atual < hab['custo']:
                btn.config(state='disabled', bg=self.colors["bg_widget"], fg=self.colors["disabled"])
            btn.pack(fill='x', padx=10, pady=5)
        
        popup.transient(self.batalha_win)
        popup.grab_set()

    def acao_pocao(self):
        if not self.heroi_selecionado.inventario_pocoes:
            self.log_batalha("Você não tem nenhuma poção!")
            return

        popup = tk.Toplevel(self.batalha_win)
        popup.title("Usar Poção")
        popup.geometry("400x300")
        popup.configure(bg=self.colors["bg_frame"])
        
        tk.Label(popup, text="Escolha uma poção para usar:", fg=self.colors["fg_normal"], bg=self.colors["bg_frame"]).pack(pady=10)

        def usar(pocao_index):
            popup.destroy()
            self.turno_jogador_fim(lambda: self.heroi_selecionado.usar_pocao(pocao_index, self.log_batalha))

        for i, pocao in enumerate(self.heroi_selecionado.inventario_pocoes):
            tk.Button(popup, text=str(pocao), command=lambda idx=i: usar(idx),
                      wraplength=380, justify='left', bg=self.colors["bg_frame"], fg=self.colors["fg_normal"], relief='flat').pack(fill='x', padx=10, pady=5)
        
        popup.transient(self.batalha_win)
        popup.grab_set()

    def acao_fugir(self):
        self.atualizar_botoes_acao('disabled')
        chance = 50 + (self.heroi_selecionado.agilidade - self.inimigo_atual.agilidade)
        if rpg_dinamico.random.randint(1, 100) <= chance:
            self.log_batalha("Você fugiu com sucesso!")
            self.master.after(1500, lambda: messagebox.showinfo("Fuga", "Você conseguiu escapar da batalha."))
            self.master.after(1500, self.fuga_masmorra)
        else:
            self.log_batalha("Fuga falhou!")
            self.master.after(1500, self.turno_inimigo)

    def turno_inimigo(self):
        """Handles the enemy's turn with error handling."""
        try:
            if self.inimigo_atual.esta_vivo():
                self.log_batalha("-" * 20)
                self.inimigo_atual.processar_efeitos_e_buffs(self.log_batalha)
                self.atualizar_status_batalha()
                if self.verificar_fim_batalha(): return

                if 'congelado' in self.inimigo_atual.efeitos_status:
                    self.log_batalha(f"🥶 {self.inimigo_atual.nome} está congelado e não pode atacar!")
                else:
                    self.inimigo_atual.atacar(self.heroi_selecionado, self.log_batalha)
                
                self.atualizar_status_batalha()
                if self.verificar_fim_batalha(): return
                
                self.master.after(1000, self.turno_do_jogador_inicio)
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
            self.master.after(1500, self.vitoria_batalha)
            return True
        elif not jogador.esta_vivo():
            self.log_batalha("❌ Você foi derrotado!")
            self.master.after(1500, self.derrota_masmorra)
            return True
        return False

    def vitoria_batalha(self):
        """Handles the rewards and progression after winning a battle."""
        if self.batalha_win and self.batalha_win.winfo_exists():
            self.batalha_win.destroy()
        
        jogador = self.heroi_selecionado
        inimigo = self.inimigo_atual
        
        jogador.buffs_ativos = {}
        jogador.efeitos_status = {}
        
        xp_ganho = inimigo.nivel * 5 + rpg_dinamico.random.randint(1, 5)
        nivel_antes = jogador.nivel
        jogador.ganhar_xp(xp_ganho)
        messagebox.showinfo("Vitória!", f"Você ganhou {xp_ganho} de XP!")
        
        if jogador.nivel > nivel_antes:
            messagebox.showinfo("Level Up!", f"🎉 {jogador.nome} alcançou o Nível {jogador.nivel}! 🎉")
            self.tela_distribuir_pontos(jogador, rpg_dinamico.PONTOS_POR_NIVEL, is_creation=False, on_close_callback=self.mostrar_recompensa_visual)
        else:
            self.mostrar_recompensa_visual()

    def fuga_masmorra(self):
        """Handles the consequences of fleeing a battle."""
        if self.batalha_win and self.batalha_win.winfo_exists():
            self.batalha_win.destroy()

        jogador = self.heroi_selecionado
        xp_perdido = (jogador.xp_atual * rpg_dinamico.PENALIDADE_XP_MORTE) / 2 # Perde metade da penalidade normal
        jogador.xp_atual -= xp_perdido
        
        messagebox.showinfo("Fuga da Masmorra", f"Você fugiu da masmorra!\nPerdeu {xp_perdido:.0f} de XP, mas manteve sua vida.")
        self.tela_inicial()


    def derrota_masmorra(self):
        """Handles the consequences of losing a battle."""
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
        messagebox.showinfo("Vitória!", "🏆 Você conquistou a masmorra! 🏆\nPrepare-se para um novo desafio ainda maior!")
        self.total_andares += 1
        self.iniciar_masmorra()

    def mostrar_recompensa_visual(self):
        """Displays the reward selection window."""
        popup = tk.Toplevel(self.master)
        popup.title("Recompensa da Batalha")
        popup.geometry("1200x600")
        popup.configure(bg=self.colors["bg_frame"])
        
        jogador = self.heroi_selecionado

        main_frame = tk.Frame(popup, bg=self.colors["bg_frame"])
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        status_panel = tk.Frame(main_frame, bg=self.colors["bg_widget"])
        status_panel.pack(side='left', expand=True, fill='both', padx=(0, 5))
        
        status_text = tk.Text(status_panel, bg=self.colors["bg_widget"], fg=self.colors["fg_normal"], font=self.stats_font, wrap='word', bd=0, highlightthickness=0)
        status_text.pack(expand=True, fill='both', padx=10, pady=10)
        status_text.insert(tk.END, jogador.get_status_texto_com_itens())
        status_text.config(state='disabled')

        rewards_panel = tk.Frame(main_frame, bg=self.colors["bg_frame"])
        rewards_panel.pack(side='left', fill='y', padx=(5, 0), ipadx=10)

        tk.Label(rewards_panel, text="Escolha sua recompensa:", font=self.label_font, fg=self.colors["fg_normal"], bg=self.colors["bg_frame"]).pack(pady=10)
        recompensas = [rpg_dinamico.gerar_recompensa_aleatoria(jogador.nivel) for _ in range(3)]

        def proximo_passo():
            popup.destroy()
            if self.andar_atual > self.total_andares:
                self.vitoria_masmorra()
            else:
                self.andar_atual += 1
                self.proximo_andar()

        def selecionar_item(item, button):
            for child in rewards_panel.winfo_children():
                if isinstance(child, tk.Button):
                    child.config(state='disabled')

            if isinstance(item, rpg_dinamico.Equipamento):
                if messagebox.askyesno("Equipar Item?", f"Deseja equipar o novo item?\n\nNOVO: {item}\nATUAL: {jogador.equipamentos.get(item.slot) or 'Nada'}", parent=popup):
                    jogador.equipar_item(item)
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
            btn = tk.Button(rewards_panel, text=str(item), wraplength=380, justify='left', bg=self.colors["bg_frame"], fg=self.colors["fg_normal"], relief='flat')
            btn.config(command=lambda i=item, b=btn: selecionar_item(i, b))
            btn.pack(fill='x', padx=10, pady=5)

        tk.Button(rewards_panel, text="Não quero nenhum item.", command=proximo_passo, bg=self.colors["bg_frame"], fg=self.colors["fg_danger"], relief='flat').pack(pady=10)

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
        rpg_dinamico.Item.nome_formatado = lambda self: f"{self.nome} [{self.raridade.capitalize()}] {'✨' if self.raridade == 'raro' else ''}".strip()
        
        def patched_equip_str(self):
            bonus = [f"{b:+.1f} {s}" for s,b in [("FOR",self.bonus_forca), ("DEF",self.bonus_defesa), ("AGI",self.bonus_agilidade), ("VIDA",self.bonus_vida), ("CAOS", self.bonus_caos)] if b]
            return f"{self.nome_formatado()} ({', '.join(bonus)})"
        rpg_dinamico.Equipamento.__str__ = patched_equip_str

        def patched_get_status_texto_com_itens(self):
            lines = []
            lines.append(f"--- {self.nome} (Nível {self.nivel}) ---")
            lines.append(f"❤️ Vida: {self.vida_atual:.1f} / {self.vida_maxima:.1f}")
            lines.append(f"🔮 Caos: {self.caos_atual:.1f} / {self.caos_maximo:.1f}")
            if self.nivel < 5: lines.append(f"📊 XP: {self.xp_atual:.0f} / {self.xp_proximo_nivel}")
            else: lines.append("📊 XP: MÁXIMO")
            lines.append("\n--- Atributos Totais ---")
            lines.append(f"💪 Força: {self.forca:.1f}")
            lines.append(f"🛡️ Defesa: {self.defesa:.1f}")
            lines.append(f"👟 Agilidade: {self.agilidade:.1f}")
            lines.append("\n--- Equipamentos ---")
            for slot, item in self.equipamentos.items():
                item_str = str(item) if item else 'Vazio'
                lines.append(f"   - {slot.capitalize()}: {item_str}")
            lines.append("\n--- Inventário de Poções ---")
            if self.inventario_pocoes: [lines.append(f"   - {pocao}") for pocao in self.inventario_pocoes]
            else: lines.append("   Vazio")
            if self.buffs_ativos: lines.append("\n--- Buffs Ativos ---"); lines.append("   " + ", ".join([f"{data['valor']:.1f} {tipo.upper()} ({data['turnos_restantes']}t)" for tipo, data in self.buffs_ativos.items()]))
            if self.efeitos_status: lines.append("\n--- Efeitos de Status ---"); lines.append("   " + ", ".join([f"{tipo.upper()} ({data['turnos_restantes']}t)" for tipo, data in self.efeitos_status.items()]))
            return "\n".join(lines)
        rpg_dinamico.Heroi.get_status_texto_com_itens = patched_get_status_texto_com_itens

        def patched_processar_efeitos(self, logger=print):
            for tipo, data in list(self.buffs_ativos.items()):
                data['turnos_restantes'] -= 1
                if data['turnos_restantes'] <= 0: logger(f"O efeito do buff de {tipo.upper()} em {self.nome} acabou."); del self.buffs_ativos[tipo]
            for tipo, data in list(self.efeitos_status.items()):
                if tipo == 'veneno':
                    dano_veneno = data['dano']
                    logger(f"🐍 {self.nome} sofre {dano_veneno:.1f} de dano de veneno.")
                    self.receber_dano(dano_veneno)
                data['turnos_restantes'] -= 1
                if data['turnos_restantes'] <= 0: logger(f"O efeito de {tipo.upper()} em {self.nome} acabou."); del self.efeitos_status[tipo]
        rpg_dinamico.Personagem.processar_efeitos_e_buffs = patched_processar_efeitos

        def patched_atacar(self, alvo, logger=print):
            logger(f"💥 {self.nome} usa um Ataque Básico contra {alvo.nome}!")
            chance_acerto = 90 - (alvo.agilidade - self.agilidade); chance_acerto = max(20, min(100, chance_acerto))
            if rpg_dinamico.random.randint(1, 100) > chance_acerto: logger(f"   💨 ERROU!"); return
            reducao_de_dano = alvo.defesa * 0.3; dano = max(1.0, self.forca - reducao_de_dano)
            logger(f"   🎯 Acertou! Dano Físico: {dano:.1f}!"); alvo.receber_dano(dano)
        rpg_dinamico.Personagem.atacar = patched_atacar

        def patched_usar_habilidade(self, alvo, habilidade, logger=print):
            self.caos_atual -= habilidade['custo']; multiplicador = habilidade['multiplicador'] + self.proficiencia; dano_magico = self.forca * multiplicador
            logger(f"✨ {self.nome} usa {habilidade['nome']}!")
            if dano_magico > 0: logger(f"   Dano Mágico: {dano_magico:.1f}!"); alvo.receber_dano(dano_magico)
            efeito = habilidade.get('efeito')
            if efeito and rpg_dinamico.random.random() < efeito['chance']:
                if efeito['tipo'] in ['veneno', 'congelado']:
                    logger(f"   🎯 O alvo foi afetado por {efeito['tipo'].upper()}!")
                    alvo.efeitos_status[efeito['tipo']] = {'turnos_restantes': efeito['duracao'] + 1, 'dano': efeito.get('dano', 0)}
                elif efeito['tipo'] == 'buff_forca':
                    logger(f"   💪 Você se sente mais forte!")
                    self.buffs_ativos['forca'] = {'valor': efeito['valor'], 'turnos_restantes': efeito['duracao'] + 1}
            return True
        rpg_dinamico.Heroi.usar_habilidade = patched_usar_habilidade

        def patched_usar_pocao(self, pocao_index, logger=print):
            pocao = self.inventario_pocoes.pop(pocao_index)
            logger(f"Você usou {pocao.nome_formatado()}!")
            if pocao.tipo == 'cura':
                vida_curada = min(self.vida_maxima - self.vida_atual, pocao.valor)
                self.vida_atual += vida_curada
                logger(f"   Recuperou {vida_curada:.1f} de vida.")
            elif pocao.tipo == 'restaura_caos':
                caos_recuperado = min(self.caos_maximo - self.caos_atual, pocao.valor)
                self.caos_atual += caos_recuperado
                logger(f"   Recuperou {caos_recuperado:.1f} de caos.")
            else:
                tipo_buff = pocao.tipo.split('_')[1]
                self.buffs_ativos[tipo_buff] = {'valor': pocao.valor, 'turnos_restantes': pocao.duracao + 1}
                logger(f"   Seu {tipo_buff.upper()} aumentou em {pocao.valor:.1f} por {pocao.duracao} turnos!")
        rpg_dinamico.Heroi.usar_pocao = patched_usar_pocao
        
        def patched_ganhar_xp(self, quantidade):
            if self.nivel >= 5: return
            self.xp_atual += quantidade
            while self.xp_atual >= self.xp_proximo_nivel and self.nivel < 5:
                xp_excedente = self.xp_atual - self.xp_proximo_nivel
                self.nivel += 1
                self.xp_atual = xp_excedente
                self.xp_proximo_nivel = rpg_dinamico.XP_PARA_NIVEL.get(self.nivel, float('inf'))
                self.proficiencia += 0.05
                self.vida_base += 20
                self.caos_base += 10
        rpg_dinamico.Heroi.ganhar_xp = patched_ganhar_xp

        def patched_equipar_item(self, novo_equip):
            item_atual = self.equipamentos.get(novo_equip.slot)
            bonus_vida_antigo = item_atual.bonus_vida if item_atual else 0.0
            bonus_caos_antigo = item_atual.bonus_caos if item_atual else 0.0
            self.equipamentos[novo_equip.slot] = novo_equip
            delta_vida = novo_equip.bonus_vida - bonus_vida_antigo
            delta_caos = novo_equip.bonus_caos - bonus_caos_antigo
            self.vida_atual += delta_vida
            self.caos_atual += delta_caos
            self.vida_atual = min(self.vida_maxima, self.vida_atual)
            self.caos_atual = min(self.caos_maximo, self.caos_atual)
        rpg_dinamico.Heroi.equipar_item = patched_equipar_item


    patch_rpg_dinamico()
    root = tk.Tk()
    app = RPGApp(root)
    root.mainloop()