from datetime import datetime, date

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
historico_transacoes = []


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


def main():
  global saldo, limite, numero_saques, numero_transacoes, extrato, LIMITE_SAQUES
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
  