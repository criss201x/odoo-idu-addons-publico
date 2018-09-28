# -*- coding: utf-8 -*-

from appy.pod.renderer import Renderer  # sudo pip install appy
import base64
import os.path
import psutil
import subprocess
from time import sleep
from datetime import *
import magic
import PIL
from PIL import Image
import shutil
from numpy import append

def crear_reporte(self, dic_data, nombre_doc, formato_salida, nombre_plantilla, nombre_parametro_plantilla):
    """
    dic_data                   -- Data que se alojará en el documento reporte
    nombre_doc                 -- Nombre para el archivo a descargar
    formato_salida             -- Extensión de salida para el reporte EJ -> pdf, xls
    nombre_plantilla           -- Nombre del documento fuente alojado en /modulo/reports/ EJ -> plantilla_visitas.odt
    nombre_parametro_plantilla -- ir.config_parameter Nombre del parametro donde se especifica la ruta de la plantilla EJ -> plan_mejoramiento_ruta_plantilla_reportes
    """
    # ruta para plantilla
    parametro_ruta = self.env['ir.config_parameter'].get_param(nombre_parametro_plantilla, context=None)
    plantilla =  parametro_ruta + nombre_plantilla
    # get extencion de plantilla 
    extencion_plantilla = nombre_plantilla.split(".")[-1]
    # nombres para archivos
    inicial_nombre = "REPORTE_"
    nombre_archivo_result = inicial_nombre + nombre_doc + '_' + str(self.id) + '.' + extencion_plantilla
    nombre_archivo_result_transf = inicial_nombre + nombre_doc + '_' + str(self.id) +'.'+formato_salida
    # Carpeta Contenedora de los reportes
    carpeta = '/tmp/reportres/'
    archivo_result = carpeta + nombre_archivo_result
    archivo_result_transf = carpeta + nombre_archivo_result_transf
    # Verificar si existe carpeta, si no la crea
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    # Crear archivo basado en la plantilla y los datos
    globals_dict = globals()
    globals_dict['reporte'] = dic_data
    renderer = Renderer(plantilla, globals_dict, archivo_result)
    renderer.run()
    # Convierte a Formato Salida
    kill_libreoffice()
    subprocess.Popen("libreoffice --headless --invisible --convert-to {} {} --outdir {} ".format(formato_salida, archivo_result, carpeta) ,shell=True)
    # ya esta creado xls?
    while not os.path.isfile(archivo_result_transf):
        sleep(1)
    # codificar archivo
    with open(archivo_result_transf, "rb") as reporte:
        encoded_report = base64.b64encode(reporte.read())
    # Elinimar archivos creados en disco
    if(encoded_report):
        os.remove(archivo_result)
        os.remove(archivo_result_transf)
    return encoded_report, nombre_archivo_result_transf

def kill_libreoffice():
    PROCNAME = "soffice.bin"
    for proc in psutil.process_iter():
        if proc.name == PROCNAME:
            proc.kill()

def limpiar_carpeta(ruta):
    if os.path.exists(ruta):
        shutil.rmtree(ruta)