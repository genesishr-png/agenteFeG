import os
import sys
import json
import time
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

import config

class AgenteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Agente RAG - Organizador de Arquivos Jurídicos")
        self.root.geometry("820x760")
        self.root.configure(bg="#0f172a")  # Slate 900
        
        self.settings_file = Path(__file__).resolve().parent / ".gui_settings.json"
        self.watcher_process = None
        self.watcher_thread = None
        self.is_monitoring = False
        
        # Variáveis Tkinter
        self.input_dir_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.dry_run_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Status: Pronto")
        self.gemini_key_var = tk.StringVar()
        self.anthropic_key_var = tk.StringVar()
        self.show_keys_var = tk.BooleanVar(value=False)
        
        # Carrega preferências salvas
        self.load_settings()
        
        # Constrói a UI
        self.setup_ui()

    def load_env_keys(self):
        env_path = Path(__file__).resolve().parent / ".env"
        gemini_key = ""
        anthropic_key = ""
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            gemini_key = line.split("=", 1)[1].strip()
                        elif line.startswith("ANTHROPIC_API_KEY="):
                            anthropic_key = line.split("=", 1)[1].strip()
            except Exception:
                pass
        # Remove placeholder text for user convenience
        if gemini_key == "sua_chave_do_gemini_aqui":
            gemini_key = ""
        if anthropic_key == "sua_chave_do_claude_aqui":
            anthropic_key = ""
        return gemini_key, anthropic_key

    def save_env_keys(self, gemini_key, anthropic_key):
        env_path = Path(__file__).resolve().parent / ".env"
        # If both are empty/placeholders, we can write fallback placeholders
        g_val = gemini_key.strip() if gemini_key.strip() else "sua_chave_do_gemini_aqui"
        a_val = anthropic_key.strip() if anthropic_key.strip() else "sua_chave_do_claude_aqui"
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("# Chaves de API para os modelos de IA\n")
                f.write(f"GEMINI_API_KEY={g_val}\n")
                f.write(f"ANTHROPIC_API_KEY={a_val}\n")
        except Exception:
            pass

    def load_settings(self):
        """Carrega as pastas selecionadas anteriormente e chaves de API."""
        gemini_key, anthropic_key = self.load_env_keys()
        self.gemini_key_var.set(gemini_key)
        self.anthropic_key_var.set(anthropic_key)
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.input_dir_var.set(data.get("input_dir", str(config.DEFAULT_INPUT_DIR)))
                    self.output_dir_var.set(data.get("output_dir", str(config.DEFAULT_OUTPUT_DIR)))
                    self.dry_run_var.set(data.get("dry_run", True))
                    return
            except Exception:
                pass
        
        # Defaults se não houver arquivo de config
        self.input_dir_var.set(str(config.DEFAULT_INPUT_DIR))
        self.output_dir_var.set(str(config.DEFAULT_OUTPUT_DIR))

    def save_settings(self):
        """Salva as pastas selecionadas e chaves de API."""
        # Salva chaves no .env
        self.save_env_keys(self.gemini_key_var.get(), self.anthropic_key_var.get())
        
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump({
                    "input_dir": self.input_dir_var.get(),
                    "output_dir": self.output_dir_var.get(),
                    "dry_run": self.dry_run_var.get()
                }, f, indent=2)
        except Exception:
            pass

    def setup_ui(self):
        # Estilo geral (Cores Modernas)
        bg_dark = "#0f172a"
        bg_card = "#1e293b"
        accent_color = "#6366f1"  # Indigo
        accent_green = "#10b981"  # Emerald
        text_light = "#f8fafc"
        text_muted = "#94a3b8"
        
        # Configura fontes padrão
        font_title = ("Segoe UI", 16, "bold")
        font_header = ("Segoe UI", 11, "bold")
        font_body = ("Segoe UI", 10)
        font_console = ("Consolas", 9)
        
        # Cabeçalho Principal (Header)
        header_frame = tk.Frame(self.root, bg=bg_card, height=70, bd=0, highlightthickness=0)
        header_frame.pack(fill="x", side="top")
        
        header_title = tk.Label(
            header_frame, 
            text="AGENTE INTELIGENTE RAG - ORGANIZAÇÃO DE PROCESSOS", 
            fg=text_light, 
            bg=bg_card,
            font=font_title
        )
        header_title.pack(side="left", padx=20, pady=18)
        
        # Container de Conteúdo
        content_frame = tk.Frame(self.root, bg=bg_dark)
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # 1. Card de Configuração de Pastas
        paths_card = tk.LabelFrame(
            content_frame, 
            text=" Configurações de Diretórios ", 
            fg=accent_color, 
            bg=bg_dark,
            font=font_header,
            bd=1,
            relief="solid",
            highlightthickness=0
        )
        paths_card.pack(fill="x", pady=5, ipady=8, ipadx=5)
        
        # Input Dir Row
        lbl_in = tk.Label(paths_card, text="Pasta de Entrada:", fg=text_muted, bg=bg_dark, font=font_body, anchor="w")
        lbl_in.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        ent_in = tk.Entry(paths_card, textvariable=self.input_dir_var, bg=bg_card, fg=text_light, insertbackground=text_light, font=font_body, bd=0, width=65)
        ent_in.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        btn_browse_in = tk.Button(
            paths_card, 
            text="Procurar...", 
            command=self.browse_input, 
            bg=accent_color, 
            fg=text_light, 
            activebackground="#4f46e5",
            activeforeground=text_light,
            bd=0, 
            font=font_body,
            padx=12,
            pady=3,
            cursor="hand2"
        )
        btn_browse_in.grid(row=0, column=2, padx=10, pady=5)
        
        # Output Dir Row
        lbl_out = tk.Label(paths_card, text="Pasta de Destino:", fg=text_muted, bg=bg_dark, font=font_body, anchor="w")
        lbl_out.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ent_out = tk.Entry(paths_card, textvariable=self.output_dir_var, bg=bg_card, fg=text_light, insertbackground=text_light, font=font_body, bd=0, width=65)
        ent_out.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        btn_browse_out = tk.Button(
            paths_card, 
            text="Procurar...", 
            command=self.browse_output, 
            bg=accent_color, 
            fg=text_light, 
            activebackground="#4f46e5",
            activeforeground=text_light,
            bd=0, 
            font=font_body,
            padx=12,
            pady=3,
            cursor="hand2"
        )
        btn_browse_out.grid(row=1, column=2, padx=10, pady=5)
        
        # Opção Dry Run
        chk_dry = tk.Checkbutton(
            paths_card,
            text="Executar apenas Simulação (Dry Run - não move arquivos físicos)",
            variable=self.dry_run_var,
            onvalue=True,
            offvalue=False,
            bg=bg_dark,
            fg=text_light,
            selectcolor=bg_card,
            activebackground=bg_dark,
            activeforeground=text_light,
            font=font_body,
            bd=0
        )
        chk_dry.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # 1.5. Card de Configuração de APIs
        apis_card = tk.LabelFrame(
            content_frame, 
            text=" Configurações das APIs (IA) ", 
            fg=accent_color, 
            bg=bg_dark,
            font=font_header,
            bd=1,
            relief="solid",
            highlightthickness=0
        )
        apis_card.pack(fill="x", pady=5, ipady=8, ipadx=5)
        
        # Gemini Key Row
        lbl_gemini = tk.Label(apis_card, text="Gemini API Key:", fg=text_muted, bg=bg_dark, font=font_body, anchor="w")
        lbl_gemini.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.ent_gemini = tk.Entry(
            apis_card, 
            textvariable=self.gemini_key_var, 
            bg=bg_card, 
            fg=text_light, 
            insertbackground=text_light, 
            font=font_body, 
            bd=0, 
            width=65,
            show="*"
        )
        self.ent_gemini.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Anthropic Key Row
        lbl_claude = tk.Label(apis_card, text="Claude API Key:", fg=text_muted, bg=bg_dark, font=font_body, anchor="w")
        lbl_claude.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.ent_claude = tk.Entry(
            apis_card, 
            textvariable=self.anthropic_key_var, 
            bg=bg_card, 
            fg=text_light, 
            insertbackground=text_light, 
            font=font_body, 
            bd=0, 
            width=65,
            show="*"
        )
        self.ent_claude.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Checkbox Mostrar Chaves
        chk_show_keys = tk.Checkbutton(
            apis_card,
            text="Mostrar chaves de API",
            variable=self.show_keys_var,
            command=self.toggle_show_keys,
            bg=bg_dark,
            fg=text_light,
            selectcolor=bg_card,
            activebackground=bg_dark,
            activeforeground=text_light,
            font=font_body,
            bd=0
        )
        chk_show_keys.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # 2. Card de Ações
        actions_frame = tk.Frame(content_frame, bg=bg_dark)
        actions_frame.pack(fill="x", pady=10)
        
        self.btn_run = tk.Button(
            actions_frame,
            text="⚡ Iniciar Organização (Lote)",
            command=self.trigger_run_once,
            bg=accent_color,
            fg=text_light,
            activebackground="#4f46e5",
            activeforeground=text_light,
            font=font_header,
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.btn_run.pack(side="left", padx=5)
        
        self.btn_watch = tk.Button(
            actions_frame,
            text="👀 Ativar Monitoramento Contínuo",
            command=self.toggle_monitoring,
            bg=accent_green,
            fg=text_light,
            activebackground="#059669",
            activeforeground=text_light,
            font=font_header,
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.btn_watch.pack(side="left", padx=15)
        
        btn_clear_log = tk.Button(
            actions_frame,
            text="Limpar Log",
            command=self.clear_console,
            bg=bg_card,
            fg=text_muted,
            activebackground="#334155",
            activeforeground=text_light,
            font=font_body,
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_clear_log.pack(side="right", padx=5)
        
        # Status Label
        self.lbl_status = tk.Label(
            content_frame,
            textvariable=self.status_var,
            fg="#60a5fa",
            bg=bg_dark,
            font=("Segoe UI", 10, "italic"),
            anchor="w"
        )
        self.lbl_status.pack(fill="x", pady=2)
        
        # 3. Console de Visualização de Logs
        console_frame = tk.LabelFrame(
            content_frame,
            text=" Visualizador de Atividades (Logs) ",
            fg=accent_color,
            bg=bg_dark,
            font=font_header,
            bd=1,
            relief="solid",
            highlightthickness=0
        )
        console_frame.pack(fill="both", expand=True, pady=5)
        
        self.txt_console = scrolledtext.ScrolledText(
            console_frame,
            bg="#020617",  # Deep Dark
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            font=font_console,
            bd=0,
            padx=10,
            pady=10
        )
        self.txt_console.pack(fill="both", expand=True)
        self.txt_console.configure(state="disabled")

    def browse_input(self):
        folder = filedialog.askdirectory(initialdir=self.input_dir_var.get())
        if folder:
            self.input_dir_var.set(folder)
            self.save_settings()

    def browse_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if folder:
            self.output_dir_var.set(folder)
            self.save_settings()

    def toggle_show_keys(self):
        show_char = "" if self.show_keys_var.get() else "*"
        self.ent_gemini.configure(show=show_char)
        self.ent_claude.configure(show=show_char)

    def clear_console(self):
        self.txt_console.configure(state="normal")
        self.txt_console.delete("1.0", "end")
        self.txt_console.configure(state="disabled")

    def append_log(self, message):
        """Escreve mensagens na caixa de console visual em tempo real."""
        self.txt_console.configure(state="normal")
        self.txt_console.insert("end", message)
        self.txt_console.see("end")
        self.txt_console.configure(state="disabled")

    def trigger_run_once(self):
        """Chama a orquestração do main.py em uma thread separada para não travar a UI."""
        self.btn_run.configure(state="disabled")
        self.status_var.set("Status: Processando...")
        self.clear_console()
        self.save_settings()
        
        thread = threading.Thread(target=self.run_once_worker)
        thread.daemon = True
        thread.start()

    def run_once_worker(self):
        """Thread worker para executar o main.py."""
        cmd = [
            sys.executable,
            str(Path(__file__).resolve().parent / "main.py"),
            "--input-dir", self.input_dir_var.get(),
            "--output-dir", self.output_dir_var.get()
        ]
        if self.dry_run_var.get():
            cmd.append("--dry-run")
            
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="ignore"
            )
            
            for line in iter(process.stdout.readline, ""):
                self.append_log(line)
                
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                self.status_var.set("Status: Concluído com sucesso!")
            else:
                self.status_var.set(f"Status: Execução finalizou com erro ({return_code}).")
                
        except Exception as e:
            self.append_log(f"\nErro ao iniciar execução do processo: {str(e)}\n")
            self.status_var.set("Status: Falha ao rodar script")
            
        finally:
            self.btn_run.configure(state="normal")

    def toggle_monitoring(self):
        """Liga ou Desliga o monitor contínuo (watcher.py)."""
        self.save_settings()
        
        if self.is_monitoring:
            # Para o monitor
            self.stop_watcher()
        else:
            # Inicia o monitor
            self.start_watcher()

    def start_watcher(self):
        self.is_monitoring = True
        self.btn_watch.configure(text="🛑 Parar Monitoramento", bg="#ef4444", activebackground="#dc2626")
        self.status_var.set("Status: Monitoramento de Pasta Ativo")
        self.clear_console()
        self.append_log("=== Ativando Monitor de Pastas Contínuo ===\n")
        
        self.watcher_thread = threading.Thread(target=self.watcher_worker)
        self.watcher_thread.daemon = True
        self.watcher_thread.start()

    def watcher_worker(self):
        cmd = [
            sys.executable,
            str(Path(__file__).resolve().parent / "watcher.py"),
            "--input-dir", self.input_dir_var.get(),
            "--output-dir", self.output_dir_var.get()
        ]
        if self.dry_run_var.get():
            cmd.append("--dry-run")
            
        try:
            self.watcher_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="ignore"
            )
            
            for line in iter(self.watcher_process.stdout.readline, ""):
                self.append_log(line)
                
            self.watcher_process.stdout.close()
            self.watcher_process.wait()
            
        except Exception as e:
            if self.is_monitoring:  # Se não foi interrompido intencionalmente
                self.append_log(f"\nErro no monitoramento: {str(e)}\n")
        finally:
            self.root.after(0, self.reset_watcher_ui)

    def stop_watcher(self):
        self.is_monitoring = False
        self.append_log("\n=== Desativando Monitor de Pastas ===\n")
        
        if self.watcher_process:
            try:
                self.watcher_process.terminate()
                self.watcher_process.wait(timeout=2)
            except Exception:
                try:
                    self.watcher_process.kill()
                except Exception:
                    pass
            self.watcher_process = None
            
        self.reset_watcher_ui()

    def reset_watcher_ui(self):
        self.is_monitoring = False
        self.btn_watch.configure(text="👀 Ativar Monitoramento Contínuo", bg="#10b981", activebackground="#059669")
        self.status_var.set("Status: Monitoramento Desativado")

def main():
    root = tk.Tk()
    app = AgenteGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
