from selenium import webdriver
import json
import os
import sys

app_path = os.path.dirname(sys.argv[0])
chrome_driver_path = f'{app_path}/chromedriver.exe'
LISTA_URL = 'https://www.cmfchile.cl/institucional/mercados/consulta.php?mercado=V&Estado=VI&entidad=RVEMI'


class Scraper:
    def __init__(self):
        self.driver = webdriver.Chrome(chrome_driver_path)
        self.listado = {}
        self.accionistas = {}

    def obtener_ruts(self):
        self.driver.get(LISTA_URL)
        table_rows = self.driver.find_elements_by_css_selector('tr')
        rut_rows = [row for row in table_rows]
        del rut_rows[0:2]

        for row in rut_rows:
            links = row.find_elements_by_css_selector('a')
            rut = links[0].get_attribute('innerHTML').split('-')
            entidad = links[1].get_attribute('innerHTML')
            self.listado[entidad] = rut

    def obtener_accionistas(self):
        for entidad, rut in self.listado.items():

            self.driver.get(f'https://www.cmfchile.cl/institucional/mercados/entidad.php?mercado=V&rut={rut[0]}&grupo=&tipoentidad=RVEMI&row=&vig=VI&control=svs&pestania=5')
            tablas = self.driver.find_elements_by_css_selector('table')
            self.accionistas[entidad] = []
            if len(tablas) > 1:
                filas = tablas[1].find_elements_by_css_selector('tr')
                accionistas = [fila for fila in filas]
                del accionistas[0]
                for accionista in accionistas:
                    datos_accionista = accionista.find_elements_by_css_selector('td')
                    nombre = datos_accionista[0].get_attribute('innerHTML').strip()
                    acciones_suscritas = datos_accionista[1].get_attribute('innerHTML').strip()
                    acciones_pagadas = datos_accionista[2].get_attribute('innerHTML').strip()
                    porcentaje = datos_accionista[3].get_attribute('innerHTML').strip()[:-1]

                    self.accionistas[entidad].append(
                        {
                            'nombre': nombre,
                            'acciones_suscritas': acciones_suscritas,
                            'acciones_pagadas': acciones_pagadas,
                            'porcentaje': porcentaje
                        }
                    )

            else:
                self.accionistas[entidad].append(
                    {
                        'nombre': 'NA',
                        'acciones_suscritas': 'NA',
                        'acciones_pagadas': 'NA',
                        'porcentaje': 'NA'
                    }
                )

    def guardar_datos(self):
        with open('listado_contribuyentes.json', 'w', encoding='utf-8') as file:
            json.dump(self.listado, file, indent=4, ensure_ascii=False)

        with open('accionistas.json', 'w', encoding='utf-8') as file:
            json.dump(self.accionistas, file, indent=4, ensure_ascii=False)


scraper = Scraper()
scraper.obtener_ruts()
scraper.obtener_accionistas()
scraper.guardar_datos()
