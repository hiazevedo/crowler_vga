import re
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.chrome.service as service


def get_vga(service=None):
    op = webdriver.ChromeOptions()
    op.add_argument('--headless')
    op.add_argument('--no-sandbox')
    op.add_argument('--disable-dev-shm-usage')
    op.add_argument("--remote-debugging-port=9222")

    chromedriver_path = "/home/higor/Documentos/higor/python/crowler_vga/webdriver/chromedriver"

    service = service.Service(chromedriver_path)
    service.start()

    driver = webdriver.Remote(command_executor=service.service_url, options=op)

    try:
        dict_produtos = []
        url = f'https://www.julianocaju.com.br/ofertas/placas-de-video.asp'
        driver.get(url)

        lista = driver.find_elements(By.XPATH, '//*[@id="lista-ofertas"]/li/a')

        for element in lista:
            link = element.get_attribute('href')
            nome = element.find_element(By.XPATH, 'p[1]').text
            modelo = element.find_element(By.XPATH, 'p[2]').text

            trata_valor = element.find_element(By.XPATH, 'p[3]').text
            resultado = re.search(r"([\d,\\.]+)", trata_valor)

            a = resultado.group(1)
            a = a.replace('.', '')
            a = a.replace(',', '.')

            valor = float(a)
            pcupomdes = element.find_elements(By.XPATH, 'p[4][@class="cupomdesc"]')
            if len(pcupomdes) == 0:
                cupom_desconto = None
                loja = element.find_element(By.XPATH, 'p[5]/span/img').get_attribute('alt')
            else:
                cupom_desconto = pcupomdes[0].text[19:]
                loja = element.find_element(By.XPATH, 'p[6]/span/img').get_attribute('alt')

            dict_produtos.append({'nome': nome,
                                  'modelo': modelo,
                                  'valor': valor,
                                  'loja': loja,
                                  'cupom_desconto': cupom_desconto,
                                  'link': link
                                  })
    finally:
        driver.close()
        service.stop()
    return dict_produtos


def insert_db(dict_produtos):
    con = sqlite3.connect("./database/price_vga.db")

    cur = con.cursor()
    for dict_produto in dict_produtos:
        cur.execute("INSERT INTO placas VALUES( ?, ?, ?, ?, ?, ?, datetime('now','localtime') )", tuple(dict_produto.values()))
    con.commit()
    con.close()

    # print(dict_produtos.values())

# bloco principal
lista = get_vga(service)

insert_db(lista)
