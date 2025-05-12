from datetime import datetime, date
import locale
from abc import ABC, abstractmethod, abstractproperty
import validacoes_cadastro_usuario as validacoes
import textwrap

contas = []

def menu():
  menu = """
  ================ MENU ================
  [d]\tDepositar
  [s]\tSacar
  [e]\tExtrato
  [nc]\tNova conta
  [lc]\tListar contas
  [nu]\tNovo usuário
  [q]\tsair
  => """
  return input(textwrap.dedent(menu))


class Cliente():
  def __init__(self, endereco):
    self._endereco = endereco
    self._contas: list["Conta"] = []

  @property
  def endereco(self):
    return self._endereco
  
  @property
  def contas(self):
    return self._contas
  
  def adicionar_conta(self, conta):
    self.contas.append(conta)
  
  def realizar_transacao(self, conta, transacao):
    transacao.registrar(conta)
  

class PessoaFisica(Cliente):
  def __init__(self, cpf, nome, data_nascimento, endereco):
    super().__init__(endereco)
    self._nome = nome
    self._cpf = cpf
    self._data_nascimento = data_nascimento
  
  @property
  def cpf(self):
    return self._cpf
  
  @property
  def nome(self):
    return self._nome
  
  @nome.setter
  def nome(self, nome):
    self._nome = nome

  @property
  def data_nascimento(self):
    return self._data_nascimento.strftime('%d/%m/%Y')


# Classes referentes à conta, transações e histórico
class Conta():
  def __init__(self, numero, cliente): #H istórico é como um extrato
    self._numero = numero
    self._agencia = '0001'
    self._cliente = cliente
    self._saldo = 0
    self._historico = Historico()
  
  @property
  def saldo(self):
    return self._saldo

  @saldo.setter
  def saldo(self, novo_saldo):
    self._saldo = novo_saldo
  
  @property
  def agencia(self):
    return self._agencia
  
  @property
  def numero(self):
    return self._numero
  
  @property
  def cliente(self):
    return self._cliente
  
  @property
  def historico(self):
    return self._historico
  
  @classmethod
  def nova_conta(cls, cliente, numero):    
    return cls(numero, cliente)

  def sacar(self, valor:float):
    saldo = self._saldo
    excedeu_saldo = valor > saldo

    if excedeu_saldo:
      print("\nOperação falhou! Saldo insuficiente para esta operação")
    elif valor > 0:
      self._saldo -= valor
      print('\nSaque realizado com sucesso!')
      return True
    else:
      print('\nOperação Falou! Valor solicitado inválido.')
      return False

  def depositar(self, valor:float):
    if valor > 0:
      self._saldo += valor
      print('Depósito realizado com sucesso!')
      return True
    else:
      print('Operação falhou! Valor para depósito inválido')
      return False


  def exibir_extrato(self):
    print("\n============= EXTRATO ===============")
    if not self.historico.transacoes:
      print('Não há movimentações na conta ainda.')
    else:
      for transacao in self.historico.transacoes:
        sinal = ''
        if transacao.__class__.__name__ == 'Deposito':
          sinal = '(+)'
        elif transacao.__class__.__name__ == 'Saque':
          sinal = '(-)'
        print(f"{sinal}: Valor = {transacao.valor:,.2f}, Data: {transacao.data.strftime('%d/%m/%Y %H:%M:%S')}")
      print(f"Saldo: {self.saldo:,.2f}")
      print("=====================================")
  
    def __str__(self):
      return f"Conta(Número: {self._numero}, Agência: {self._agencia}, Cliente: {self._cliente.nome if self._cliente else 'N/A'})"


class ContaCorrente(Conta):
  def __init__(self, numero, cliente, limite = 500, limite_saques=3):
    super().__init__(numero, cliente)
    self._limite = limite
    self._limite_saques = limite_saques

  def sacar(self, valor):
    numero_saques = len(
        [transacao for transacao in self.historico.transacoes['tipo'] == Saque.__name__]
      )
    
    excedeu_limite = valor > self._limite
    excedeu_saques = numero_saques >= self._limite_saques

    if excedeu_limite:
      print('\nOperação Falhou! O valor de saque excede o limite.')    
    elif excedeu_saques:
      print('\nOperação falhou! Número máximo de saques excedido.')
    else:
      return super().sacar(valor)
    
    return False
  
  def __str__(self):
    return f"""
            Agência:\t{self.agencia}
            C/C:\t{self.numero}
            Titular:\t{self.cliente.nome}
            """


class Historico():
  def __init__(self):
    self._transacoes = []
  
  @property
  def transacoes(self):
    return self._transacoes
  
  def adicionar_transacao(self, transacao):
    self._transacoes.append({
      "tipo":transacao.__class__.__name__,
      "valor":transacao.valor,
      "data":datetime.now().strftime("%d-%m-%Y %h:%M:%Y")
    })


class Transacao(ABC):  
  @property
  @abstractproperty
  def valor(self):
    pass
  
  @abstractmethod
  def registrar(self, conta):
    pass


class Deposito(Transacao):
  def __init__(self, valor):
    self._valor = valor

  @property
  def valor(self):
    return self._valor
  
  def registrar(self, conta:Conta):
    sucesso_transacao = conta.depositar(self.valor)

    if sucesso_transacao:
      conta.historico.adicionar_transacao(self)
    

class Saque(Transacao):
  def __init__(self, valor):
    self._valor = valor
  
  @property
  def valor(self):
    return self._valor

  def registrar(self, conta):
    sucesso_transacao = conta.sacar(self.valor)

    if sucesso_transacao:
      conta.historico.adicionar_transacao(self)


# Ações do usuário
def filtrar_cliente(cpf, clientes):
  clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
  return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
  if not cliente.contas:
    print('\nCliente não possui conta!')
  
  return cliente.contas[0]


def depositar(clientes):
  cpf = validacoes.receber_input_validado('CPF: ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
  cliente = filtrar_cliente(cpf, clientes)

  if not cliente:
    print('\nCliente não encontrado')
    return
  
  valor = float(input("Informe o valor do depósito: "))
  transacao = Deposito(valor)

  conta = recuperar_conta_cliente(cliente)
  if not conta:
    return
  
  cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
  cpf = validacoes.receber_input_validado('CPF: ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
  cliente = filtrar_cliente(cpf, clientes)

  if not cliente:
    print('\nCliente não localizado!')
    return
  
  valor = float(input('Informe o valor do saque: '))
  transacao = Saque(valor)

  conta = recuperar_conta_cliente(cliente)
  if not conta:
    return
  
  cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
  cpf = validacoes.receber_input_validado('CPF: ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
  cliente = filtrar_cliente(cpf, clientes)

  if not cliente:
    print('\nCLiente não encontrado!')
    return
  
  conta = recuperar_conta_cliente(cliente)
  if not conta:
    return
  
  print("\n================ EXTRATO ================")
  transacoes = conta.historico.transacoes

  extrato = ""
  if not transacoes:
    print('Não foram realizadas movimentações.')
  else:
    for transacao in transacoes:
      extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:,.2f}"
  
  print(extrato)
  print(f"\nSaldo: \n\tR$ {conta.saldo:,.2f}")
  print("==========================================")


def criar_cliente():
    usuario = {}
    print("\n=============== Cadastro de Novo Cliente ===============")

    nome = validacoes.receber_input_validado('Nome: ', 'Nome', validacoes.validar_nome, "Nome Inválido.")
    usuario['nome'] = nome

    cpf = validacoes.receber_input_validado('CPF (apenas dígitos): ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
    usuario['cpf'] = cpf

    dt_nascimento = validacoes.receber_input_validado('Data de nascimento (formato: dd/mm/aaaa): ', 'Data de Nascimento', validacoes.validar_dt_nascimento, "Formato de data inválido (dd/mm/aaaa).", validacoes.converter_dt_nascimento)
    usuario['data_nascimento'] = dt_nascimento

    usuario['endereco'] = ''

    logradouro = validacoes.receber_input_validado('Logradouro: ', 'logradouro', validacoes.validar_text_obrigatorio, 'Logradouro inválido')
    usuario['endereco'] += logradouro
    
    nro = validacoes.receber_input_validado('Nº: ', 'número', validacoes.validar_numero_endereco,  "O nº do endereço deve ser um dígito, ou 0 se não houver.", validacoes.converter_numero_endereco)
    usuario['endereco'] += f', {nro}'

    bairro = validacoes.receber_input_validado('Bairro: ', 'bairro', validacoes.validar_text_obrigatorio, "Bairro inválido")
    usuario['endereco'] += f', {bairro}'

    cidade = validacoes.receber_input_validado('Cidade: ', 'cidade', validacoes.validar_text_obrigatorio, 'Valor inválido para cidade.')
    usuario['endereco'] += f' - {cidade}'

    uf = validacoes.receber_input_validado('UF: ', 'uf', validacoes.validar_uf, 'UF inválida (exemplo: SP).')
    usuario['endereco'] += f'/{uf}'
    
    cliente = PessoaFisica(usuario.get('cpf'), usuario.get('nome'), usuario.get('data_nascimento'), usuario.get('endereco'))
    validacoes.clientes.append(cliente)
    print("\n=== Finalização de Cadastro de Cliente ===============")
    print("\n=============== Cliente Cadastrado Com Sucesso !===============")
    

def criar_conta(numero_conta, clientes, contas):      
  while True:
    cpf = input('CPF do cliente (digite "q" para voltar ao menu anterior): ')
    if cpf == 'q':
      break
    else: 
      cpf_limpo = cpf.replace('.', '').replace('-', '')
      if not cpf_limpo.isdigit() or len(cpf) != 11:
        print('CPF inválido. Digite apenas 11 numeros')
        return False
      else:
        cliente = localizar_cli(cpf_limpo, clientes)
        if cliente:
          conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
          contas.append(conta)
          cliente.contas.append(conta)
          print("\n=== Conta criada com sucess! ===")
          break
        else:
          print('Cliente não localizado. Verifique o CPF digitado.')


def listar_contas(contas):
  for conta in contas:
    print('=' * 100)
    print(textwrap.dedent(str(conta)))
  

def localizar_cli(cpf, clientes):
    for cliente in clientes:
      if cliente.cpf == cpf:
        return cliente
    print('Cliente não localizado, favor verifique o CPF digitado.')
    return None        


def main():
  clientes = validacoes.clientes
  contas = []

  print('\n==================================================')
  print('=== Sistema Bancário Suzano - Python Developer ===')
  print('==================================================')

  while True:
    print('\nEscolha uma operação:')
    opcao = menu()
    match opcao:
      case 'nu':
        criar_cliente()
      case 'nc':
        numero_conta = len(contas) + 1
        criar_conta(numero_conta, clientes, contas)
      case 'q':
        break
      case 'd':
        depositar(clientes)
      case 's':
        sacar(clientes)
      case 'e':
        exibir_extrato(clientes)
      case 'lc':
        listar_contas(contas)
      case _:
        continue
  

if __name__=='__main__':
  main()


