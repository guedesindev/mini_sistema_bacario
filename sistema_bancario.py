from datetime import datetime

menu = """
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

def marcar_horario():
  """
    Função para returnar o momento exato que uma operação foi realizada para salvar no extrato
    retornos: 
      data (date): O dia que a operação foi realizada
      hora (time): A hora com precisão de segundos que uma operação foi realizada.
  """
  return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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
        data_hora = marcar_horario()
        extrato += f"| {data_hora} (+)  R$ {valor+restituir_limite:,.2f} |\n"
        print('Depósito realizado com sucesso!')
        num_transacoes += 1

        return saldo, limite, extrato, num_transacoes
  
def sacar(saldo, limite, n_saques, l_saques, extrato, num_transacoes, lim_transacoes):
  """Função para realizar saques."""
  excedeu_saques = n_saques >= l_saques
  execedeu_lim_transacoes = num_transacoes >= lim_transacoes
  
  if saldo + limite == 0:
    print('Operação Indisponível no momento. Verifique seu saldo.')
  elif excedeu_saques:
    print('Operação Indisponível. Numero máximo de saques excedido.')
  elif execedeu_lim_transacoes:
    print('Não é possível realizar mais operações hoje.')
  else:
    while True:
      valor_str = input('Insira o valor. ("q" para cancelar.)')
      if valor_str == 'q':
        print('Retornando ao menu superior')
        return saldo, n_saques, limite, extrato, num_transacoes
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
            data_hora = marcar_horario()
            extrato += f"| {data_hora} (-)   R$ {valor:,.2f} |\n"
            n_saques += 1
            print('Saque realizado com sucesso!')
            return saldo, n_saques, limite, extrato, num_transacoes
          else:
            # Usar o saldo restante e parte do limite
            valor_restante = valor - saldo
            saldo = 0
            limite -= valor_restante
            data_hora = marcar_horario()
            extrato += f"| {data_hora} (-)   R$ {valor:,.2f} |\n"
            n_saques += 1
            print('Saque realizado com sucesso!')
            return saldo, n_saques, limite, extrato, num_transacoes

def emitir_extrato(extrato):
  if len(extrato) == 0:
    print('Não há operações a serem exibidas')
  else:
    print('\n======================================')
    print('============== EXTRATO ===============')
    print('======================================')
    print("Não foram realizadas movimentações;" if not extrato else extrato)
    print(f"Saldo: R$ {saldo:,.2f}")
    print(f"Limite: R$ {limite:,.2f}")
    print(f'Horário da extração deste extrato: {marcar_horario()}')
    print("\n")


print('==================================================')
print('=== Sistema Bancário Suzano - Python Developer ===')
print('==================================================\n')
while True:
  print('\nEscolha uma operação:\n')
  opcao = input(menu)
  match opcao:
    case 'q':
      break
    case 'd':
      saldo, limite, extrato, numero_transacoes = depositar(saldo, limite, extrato, numero_transacoes, LIMITE_TRANSACOES)
    case 's':
      saldo, numero_saques, limite, extrato, numero_transacoes = sacar(saldo, limite, numero_saques, LIMITE_SAQUES, extrato, numero_transacoes, LIMITE_TRANSACOES)
    case 'e':
      emitir_extrato(extrato)
    case _:
      continue


print('Numero de Operações:', numero_saques)
print('Numero de Transacoes', numero_transacoes)