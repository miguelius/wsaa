#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo wsaa liviano
Copyright (C) 2019 miguelius

Este módulo funciona como una herramienta de consola o librería para tu código.

Se conecta al ambiente de homologación o puede cambiarse con la variable WSAA_URL.

Todos los derechos reservados por miguelius y distribuido bajo licencia GPLv3.
"""
from zeep import Client
from zeep.plugins import HistoryPlugin
from sys import argv,exit
from OpenSSL import crypto
import base64
from datetime import datetime
from time import time
import xml.etree.ElementTree as ET
import os

AMBIENTE = os.getenv("WSAA_URL", 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms')
DEBUG = os.getenv("WSAA_DEBUG", None)

def loguear(mensaje):
  if DEBUG is not None:
    print(mensaje)

def crear_tra(servicio, segundos_expiracion = 60):
  now = int(time())
  #now = int(datetime.timestamp(datetime.now()))
  generacion = datetime.fromtimestamp(now - 60).isoformat()
  expiracion = datetime.fromtimestamp(now + segundos_expiracion).isoformat()

  return """<?xml version="1.0" encoding="UTF-8"?>
    <loginTicketRequest version="1.0">
      <header>
        <uniqueId>%s</uniqueId>
        <generationTime>%s-03:00</generationTime>
        <expirationTime>%s-03:00</expirationTime>
      </header>
      <service>%s</service>
    </loginTicketRequest>"""%(now,generacion, expiracion,servicio)

def firmar_tra_con(tra, pkcs12=None, cert=None, key=None):
  if pkcs12 is not None:
    cert = pkcs12.get_certificate()
    key = pkcs12.get_privatekey()
  elif cert is None or key is None:
    raise RuntimeException('No tengo con que firmar :(')

  bio_in = crypto._new_mem_buf(tra.encode())
  PKCS7_NOSIGS = 0x4
  pkcs7 = crypto._lib.PKCS7_sign(cert._x509, key._pkey, crypto._ffi.NULL, bio_in, PKCS7_NOSIGS)
  bio_out = crypto._new_mem_buf()
  crypto._lib.i2d_PKCS7_bio(bio_out, pkcs7)
  sigbytes = crypto._bio_to_string(bio_out)
  signed_data = base64.b64encode(sigbytes)
  return signed_data

def main(certificado,passwd,servicio):
  try:
    p12 = crypto.load_pkcs12(open(certificado, 'rb').read(), passwd.encode('ascii'))
    base_url = AMBIENTE
    a = crear_tra(servicio)
    s = firmar_tra_con(a, pkcs12 = p12)
    history = HistoryPlugin()
    client = Client('%s?wsdl'%base_url, plugins=[history])
    mensaje = client.service.loginCms(in0=s)
  except Exception as e:
    mensaje = str(e)
  finally:
    loguear("envie: %s"%ET.tostring(history.last_sent['envelope']).decode('utf8'))
    loguear("recibi: %s"%ET.tostring(history.last_received['envelope']).decode('utf8'))
    print(mensaje)

def imprimir_uso(eje):
  print("""%s uso:
%s ruta_al_certificado_pkcs12 pass id_servicio

Imprime el ticket con las credenciales o arroja la excepcion encontrada.
  """%(eje,eje))

if __name__ == '__main__':
  if len(argv) != 4:
    imprimir_uso(argv[0])
    exit(0)
  main(argv[1], argv[2], argv[3])
