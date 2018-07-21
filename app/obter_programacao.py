from datetime import date, datetime, time
import io
import json
import locale


from lxml import html
import requests


locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')

page = requests.get('http://trivela.uol.com.br/programacao-de-tv/')
tree = html.fromstring(page.content)

programacao = tree.xpath('//*[@id="content"]/div[2]/div')[0]

jogos = []

for c in programacao.iterchildren():
    if c.tag == 'h5':
        hoje = datetime.today()

        dia = c.text
        if not dia:
            dia = c.getchildren()[0].text
        dia = dia.replace('-feira', '')
        dia = datetime.strptime(dia.encode(
            'utf-8'), '%A, %d de %B')  # dia com ano = 1900

        # determina o ano da partida
        if hoje.month > dia.month:
            ano = hoje.year + 1
        elif hoje.month < dia.month:
            ano = hoje.year - 1
        else:
            ano = hoje.year

        dia = datetime(ano, dia.month, dia.day).date()
        rows = c.getnext().getchildren()[0].iterchildren()
        for row in rows:
            cols = row.getchildren()
            horario = cols[0].text
            horario = datetime.strptime(horario, '%Hh%M').time()

            jogo = cols[1].getchildren()[0].text
            if not jogo:
                jogo = cols[1].getchildren()[0].getchildren()[0].text

            if len(cols[1].getchildren()) == 1:
                transmissao = cols[1].getchildren()[0].tail
            else:
                transmissao = cols[1].getchildren()[1].tail.strip()
            data = datetime.combine(dia, horario).isoformat()
            campeonato, jogo = jogo.split(':')
            mandante, visitante = jogo.split(' x ')
            jogos.append({
                'data': data,
                'transmissao': transmissao,
                'campeonato': campeonato,
                'mandante': mandante.lower().strip(),
                'visitante': visitante.lower(),
                'jogo': jogo, 
            })

with io.open('programacao.json', 'w+', encoding='utf-8') as programacao_file:
    jogos_json = json.dumps(jogos, indent=2, ensure_ascii=False)
    programacao_file.write(jogos_json)
