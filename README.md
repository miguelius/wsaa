# Módulo WSAA Liviano para Python #

Cliente ligero para autenticarse a un web service AFIP usando pyOpenSSL. Se usa esta librería porque es màs fàcil de instalar con cualquier SO. Es ligero porque no genera un mensaje S/MIME para obtener el pkcs7 ni llamar a la consola, sino que lo genera usando la librería.

Este es un proyecto "escuela" hecho para entender el mecanismo de autenticación y también para contar con una implementación que pueda funcionar rápidamente en cualquier SO. No está pensado para usar en producciòn.

Para poder aprovecharlo es necesario contar con un certificado pkcs12 generado como indica el instructivo de [certificados](http://www.afip.gob.ar/ws/documentacion/certificados.asp)

El módulo funciona con el ambiente de homologación. Hay una variable de entorno WSAA_URL que permitiría cambiar la URL a otro ambiente. Huelga repetir que es solo para pruebas, nadie algo tan precario para producción. ;)

Se distribuye bajo licencia GPLv3.

Por ahora no funciona con python 3.9.

## Instalación

Hay que importar las librerías que usa:

```
pip install -r requirements.txt
```

## Uso

Supongamos que el certificado que generamos esta en el archivo ejemplo.p12 con clave 1234 y queremos ingresar a ws_sr_constancia_inscripcion:

```bash
python wsaa.py ejemplo.p12 1234 ws_sr_padron_a5
```
Si todo fue bien imprimirá la respuesta con el token y el sign.

Si falla algo lo imprime. Si queremos mas visibilidad de lo que está pasando le asignamos un valor a la variable de entorno WSAA_DEBUG e imprimirá el mensaje enviado y el recibido.

## Uso como módulo

```python
from wsaa import crear_tra, firmar_tra_con
from zeep import Client
from OpenSSL import crypto

p12 = crypto.load_pkcs12(open('certificado.pfx', 'rb').read(), b'1234')
base_url = 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms'
a = crear_tra('ws_sr_padron_a5')
s = firmar_tra_con(a, pkcs12 = p12)
client = Client(f'{base_url}?wsdl')
mensaje = client.service.loginCms(in0=s)
```

## Descripción breve

El módulo wsaa se compone de una función que genera el TRA, y otra que lo firma.

Usando zeep como cliente SOAP accedemos al servicio.

La ventaja respecto a otras implementaciones que andan por ahí, esta no depende de archivos en el filesystem ni de tomar la parte pkcs7 de un mensaje S/MIME, sino que directamente firma y lo envia.

La función firmar_tra_con puede recibir el pkcs12 o la clave privada y el certificado por separado.

## Soporte y aportes

Si necesitás ayuda o se te ocurre alguna mejora o querés colaborar generá un issue del repositorio o un pull requests.

Happy hacking!
