import re
import sqlite3
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.chrome.service as service


def get_vga(service=None):
    op = webdriver.ChromeOptions()
    op.add_argument('--headless')
    op.add_argument('--no-sandbox')
    op.add_argument('--disable-dev-shm-usage')
    op.add_argument("--remote-debugging-port=9222")

    chromedriver_path = "-"

    service = service.Service(chromedriver_path)
    service.start()

    driver = webdriver.Remote(command_executor=service.service_url, options=op)

    try:
        dict_produtos = []
        url = f'https://www.julianocaju.com.br/ofertas/placas-de-video.asp'
        driver.get(url)

        sleep(5)

        lista = driver.find_elements(By.XPATH, '//*[@id="lista-ofertas"]/li/a')

        print('===== Coletando lista de VGA =====')

        for element in lista:
            link = element.get_attribute('href')
            qtd_paragrafo = len(element.find_elements(By.XPATH, 'p'))
            nome = element.find_element(By.XPATH, 'p[1]').text
            modelo = element.find_element(By.XPATH, 'p[2]').text

            trata_valor = element.find_element(By.XPATH, 'p[3]').text
            resultado = re.search(r"([\d,\\.]+)", trata_valor)

            r = resultado.group(1)
            r = r.replace('.', '')
            r = r.replace(',', '.')

            valor = float(r)

            indice_loja = 4

            if qtd_paragrafo >= 6:
                indice_loja = 5

            pcupomdes = element.find_elements(By.XPATH, 'p[4][@class="cupomdesc"]')
            if len(pcupomdes) == 0:
                cupom_desconto = None
                loja = element.find_element(By.XPATH, 'p[' + str(indice_loja) + ']/span/img').get_attribute('alt')
            else:
                indice_loja = indice_loja + 1
                cupom_desconto = pcupomdes[0].text[19:]
                loja = element.find_element(By.XPATH, 'p[' + str(indice_loja) + ']/span/img').get_attribute('alt')

            dict_produtos.append({'nome': nome,
                                  'modelo': modelo,
                                  'valor': valor,
                                  'loja': loja,
                                  'cupom_desconto': cupom_desconto,
                                  'link': link
                                  })

            print(f'===== Coletando {modelo} =====')

    finally:
        driver.close()
        service.stop()
    return dict_produtos


# insert into database
def insert_db(dict_produtos):
    con = sqlite3.connect("./database/price_vga.db")

    print('===== Inserindo lista de vga no banco de dados =====')

    cur = con.cursor()
    for dict_produto in dict_produtos:
        cur.execute("INSERT INTO placas VALUES( ?, ?, ?, ?, ?, ?, datetime('now','localtime') )",
                    tuple(dict_produto.values()))
    con.commit()
    con.close()


# bloco principal
lista = get_vga(service)

insert_db(lista)
