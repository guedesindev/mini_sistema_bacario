from datetime import datetime, date
import locale

import validacoes_cadastro_usuario as validacoes

menu = """
[u] Cadastrar Usuario
[c] Criar Conta
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair
"""
# Variáveis da conta
saldo = 0.00
limite = 50.00
numero_saques = 0
numero_transacoes = 0
LIMITE_SAQUES = 3
LIMITE_TRANSACOES = 10
LIMITE_INICIAL = 50.00

extrato = ""
historico_transacoes = []
contas = []


def verificar_transacoes_dia(historico_transacoes, LIMITE_TRANSACOES):
  hoje = date.today() # Obter apenas a data de hoje
  num_transacoes_dia = 0
  for data in historico_transacoes:
    try:
      print(data)
      if data.date() == hoje:
        num_transacoes_dia += 1
    except ValueError:
      print('data não disponível')
      continue


  print(f"{num_transacoes_dia} transações hoje restam: {LIMITE_TRANSACOES - num_transacoes_dia}")
  return num_transacoes_dia == LIMITE_TRANSACOES
  

def marcar_horario():
  """
    Função para returnar o momento exato que uma operação foi realizada para salvar no extrato
    retornos: 
      data (date): O dia que a operação foi realizada
      hora (time): A hora com precisão de segundos que uma operação foi realizada.
  """
  hora_transacao = datetime.now()
  return hora_transacao.strftime('%d/%m/%Y %H:%M:%S'), hora_transacao


def depositar(saldo, limite, extrato, num_transacoes, lim_transacoes):
  """ Função para realizar depósito na conta"""
  excedeu_operacoes = num_transacoes >= lim_transacoes
  
  while True:
    valor_str = input('Insira o valor a depoisitar: ')
    if not valor_str:
      print('Digite algum valor a depositar. ("q" para cancelar.)')
    elif valor_str == 'q':
      print('Retornando ao menu superior')
      return saldo, limite, extrato , numero_transacoes
    elif excedeu_operacoes:
      print('Não é possível realizar mais operações hoje.')
      return saldo, limite, extrato, numero_transacoes
    else:
      valor = float(valor_str)
      if valor <= 0:      
        print('Valor inválido. Valor para depositar precisa ser maior que 0 ("q" para cancelar.).')
      else:
        limite_usado = LIMITE_INICIAL - limite
        restituir_limite = 0
        if limite_usado > 0 and num_transacoes < LIMITE_TRANSACOES:
          restituir_limite = min(valor, limite_usado)
          limite += restituir_limite
          valor -= restituir_limite
          num_transacoes += 1
        saldo += valor
        data_hora, historico = marcar_horario()
        extrato += f"| {data_hora} (+)    R$ {valor+restituir_limite:,.2f} |\n"
        print('Depósito realizado com sucesso!')
        num_transacoes += 1

        return saldo, limite, extrato, num_transacoes, historico
  

def sacar(saldo, limite, n_saques, l_saques, extrato, num_transacoes):
  """Função para realizar saques."""
  excedeu_saques = n_saques >= l_saques
  
  if saldo + limite == 0:
    print('Operação Indisponível no momento. Verifique seu saldo.')
    data_hora, historico = marcar_horario()
    extrato += f"| {data_hora} (X)  Operação inválida! |\n"
    return saldo, n_saques, limite, extrato, num_transacoes, historico
  elif excedeu_saques:
    print('Operação Indisponível. Numero máximo de saques excedido.')
    data_hora, historico = marcar_horario()
    extrato += f"| {data_hora} (X)  Operação inválida! |\n"
    return saldo, n_saques, limite, extrato, num_transacoes, historico
  else:
    while True:
      valor_str = input('Insira o valor. ("q" para cancelar.)')
      if valor_str == 'q':
        print('Retornando ao menu superior')
        data_hora, historico = marcar_horario()
        extrato += f"| {data_hora} (-)  R$ {valor:,.2f} |\n"
        num_transacoes = num_transacoes
        n_saques = n_saques
        saldo = saldo
        limite = limite
        return saldo, n_saques, limite, extrato, num_transacoes, historico
      else:
        valor = float(valor_str)
        if valor <= 0:
          print('Valor inválido. Digite um valor maior que zero.')
          continue

        saldo_total_disponivel = saldo + limite

        if valor > saldo_total_disponivel:
          print('Operação Indisponível. Saldo insuficiente para este saque ("s" para consultar saldo)')
        else:
          if valor <= saldo:
            saldo -= valor
            data_hora, historico = marcar_horario()
            extrato += f"| {data_hora} (-)  R$ {valor:,.2f} |\n"
            n_saques += 1
            print('Saque realizado com sucesso!')
            return saldo, n_saques, limite, extrato, num_transacoes, historico
          else:
            # Usar o saldo restante e parte do limite
            valor_restante = valor - saldo
            saldo = 0
            limite -= valor_restante
            data_hora, historico = marcar_horario()
            extrato += f"| {data_hora} (-)  R$ {valor:,.2f} |\n"
            n_saques += 1
            print('Saque realizado com sucesso!')
            return saldo, n_saques, limite, extrato, num_transacoes, historico


def emitir_extrato(extrato):
  if len(extrato) == 0:
    print('Não há operações a serem exibidas')
  else:
    print('\n========================================')
    print('=============== EXTRATO ================')
    print('========================================')
    print("Não foram realizadas movimentações;" if not extrato else extrato)
    print(f"Saldo: R$ {saldo:,.2f}")
    print(f"Limite: R$ {limite:,.2f}")
    print(f'Horário: {marcar_horario()[0]}')
    print("\n")


def criar_usuario():
  usuario = {}

  nome = validacoes.receber_input_validado('Nome: ', 'Nome', validacoes.validar_nome, "Nome Inválido.")
  usuario['nome'] = nome

  cpf = validacoes.receber_input_validado('CPF (apenas dígitos): ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
  usuario['cpf'] = cpf

  dt_nascimento = validacoes.receber_input_validado('Data de nascimento (formato: dd/mm/aaaa): ', 'Data de Nascimento', validacoes.validar_dt_nascimento, "Formato de data inválido (dd/mm/aaaa).", validacoes.converter_dt_nascimento)
  usuario['data_nascimento'] = dt_nascimento

  usuario['endereco'] = []

  logradouro = validacoes.receber_input_validado('Logradouro: ', 'logradouro', validacoes.validar_text_obrigatorio, 'Logradouro inválido')
  usuario['endereco'].append(logradouro)
  
  nro = validacoes.receber_input_validado('Nº: ', 'número', validacoes.validar_numero_endereco,  "O nº do endereço deve ser um dígito, ou 0 se não houver.", validacoes.converter_numero_endereco)
  usuario['endereco'].append(nro)

  bairro = validacoes.receber_input_validado('Bairro: ', 'bairro', validacoes.validar_text_obrigatorio, "Bairro inválido")
  usuario['endereco'].append(bairro)

  cidade = validacoes.receber_input_validado('Cidade: ', 'cidade', validacoes.validar_text_obrigatorio, 'Valor inválido para cidade.')
  usuario['endereco'].append(cidade)

  uf = validacoes.receber_input_validado('UF: ', 'uf', validacoes.validar_uf, 'UF inválida (exemplo: SP).')
  usuario['endereco'].append(uf)

  usuario['conta'] = []

  return usuario


def criar_conta():
  nro_conta = len(contas) + 1
  agencia = '0001'
      
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
        usuario = localizar_cli(cpf_limpo)
        if usuario:
          conta = {'agencia':agencia, 'conta':nro_conta}
          contas.append(conta)
          usuario.setdefault('conta', []).append(conta)
          print(f"Conta {nro_conta} criada para o cliente {usuario.get('nome')} (CPF: {usuario.get('cpf')}).")
          break
        else:
          print('Cliente não localizado. Verifique o CPF digitado.')
  
  
def localizar_cli(cpf):
    for usuario in validacoes.usuarios:
      if usuario.get('cpf') == cpf:
        return usuario
    print('Cliente não localizado, favor verifique o CPF digitado.')
    return None        


def main():
  global saldo, limite, numero_saques, numero_transacoes, extrato, LIMITE_SAQUES
  print('\n==================================================')
  print('=== Sistema Bancário Suzano - Python Developer ===')
  print('==================================================')
  while True:
    print('Escolha uma operação:')
    opcao = input(menu)
    match opcao:
      case 'u':
        usuario = criar_usuario()
        validacoes.usuarios.append(usuario)
        print(validacoes.usuarios)
      case 'c':
        criar_conta()
      case 'q':
        break
      case 'd':
        if(not verificar_transacoes_dia(historico_transacoes, LIMITE_TRANSACOES)):
          saldo, limite, extrato, numero_transacoes, historico = depositar(saldo, limite, extrato, numero_transacoes, LIMITE_TRANSACOES)
          historico_transacoes.append(historico)
        else:
          print('Não é possível realizar mais transações hoje, limite diário atingido')
      case 's':
        if(not verificar_transacoes_dia(historico_transacoes, LIMITE_TRANSACOES)):
          saldo, numero_saques, limite, extrato, numero_transacoes, historico = sacar(saldo, limite, numero_saques, LIMITE_SAQUES, extrato, numero_transacoes)
          historico_transacoes.append(historico)
        elif numero_saques >= LIMITE_SAQUES:
          print('Operação Indisponível. Numero máximo de saques excedido.')
        else:
          print('Não é possível realizar mais transações hoje, limite diário atingido')
      case 'e':
        emitir_extrato(extrato)
      case _:
        continue


if __name__=='__main__':
  main()
  