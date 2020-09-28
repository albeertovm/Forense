#!/usr/bin/python3

import sys
import binascii
import re

"""
El objetivo de la funcion obtenConfiguracion es obtener los parametros del archivo de configuracion
y devolverlos con el siguiente formato:
[extension, header, trailer, size]
De acuerdo al numero de extensiones especificadas la lista crecera de la siguiente manera:
[extension, header, trailer, size, extension, header, trailer, size]
"""
def obtenConfiguracion():
	configuracion = []
	with open("p3_avalverde.conf", "r") as configFile:
		for linea in configFile.readlines():
			if "#" not in linea: 	
				linea = (linea.strip()).split("\t")
				for elemento in linea:
					if elemento != "":
						configuracion.append(elemento.replace(" ",""))
		return configuracion

"""
El objetivo de la funcion obtenValores es asignar los parametros obtenidos en el archivo de configuracion:
[extension, header, trailer, size]
Como la entrada de esta funcion es una lista con el siguiente formato:
[extension, header, trailer, size, extension, header, trailer, size]
Se debe hacer el match de cada indice, por ejemplo del indice 0-3 equivale a la primera extension con sus parametros correspondientes
[jpeg,\\xff\\xd8,\\xff\\xd9,3M]
La siguiente de 4-7 equivale a la primera extension con sus parametros correspondientes y así sucesivamente
['zip', '\\x50\\x4b\\x03\\x04', '\\x50\\x4b\\x06\\x50', 512000]
Los archivos pueden tener extension, header y trailer o extension, header y size respectivamente, esto se debe a que
puede que el archivo no encuentre el trailer dentro del rango del tamano indicado por lo que tendrá que cortar el archivo y seguir
con el siguiente header
Se ocupa el contador contador para tener un control sobre el total de extensiones, se divide entre 4 la longitud ya que cada extension cuenta con 4 parametros
El contador elemento sirve para modificar el elemento en iteracion como se menciono en los indices anteriormente
"""
def obtenValores(configuracion):
	contador = 0
	elemento = 0
	for contador in range(0,int(len(configuracion)/4)):
		extension = configuracion[contador+elemento]
		elemento+=1
		header = configuracion[contador+elemento]
		elemento+=1
		trailer = configuracion[contador+elemento]
		elemento+=1
		if("K" in configuracion[contador+elemento]):
			size = int(configuracion[contador+elemento][:-1]) * 1024
			recuperaArchivo(extension,header,trailer,size)
		elif("M" in configuracion[contador+elemento]):
			size = int(configuracion[contador+elemento][:-1]) * 1048576
			recuperaArchivo(extension,header,trailer, size)
		
"""
La funcion recuperaArchivo tiene como objetivo leer todo el contenido del archivo .raw y buscar coincidencias de acuerdo con el bloque de 
parametros por extension que toma como entrada
Se lee el archivo en bloques segun el tamano especificado en el archivo de configuracion
"""
def recuperaArchivo(extension,header,trailer, size):
	with open(sys.argv[1], "rb") as raw:
		contenido = raw.read()
		inicioH = []
		"""
		Se obtiene el header y el trailer de la extension a iterar, el metodo finiter busca todas las coincidencias en el archivo
		y permite almacenar el byte donde empieza y termina tant el header como el trailer
		"""
		matchHeader = bytes.fromhex(header[2::])
		matchTrailer = bytes.fromhex(trailer[2::])
		header = re.findall(matchHeader, contenido)
		trailer = re.findall(matchTrailer, contenido)
		for match in re.finditer(matchHeader, contenido):
			s = match.start()
			inicioH.append(s)
		finT = []
		#El try se acupa por si no existe un trailer asi que se escribira el archivo desde el inicio del header hasta el incio + el tamano especificado
		#Se genera un error si no hay trailer debido a que no existe el index usado en el write 
		try:
			for match in re.finditer(matchTrailer, contenido):
				e = match.end()
				finT.append(e)
			"""
			Se realiza la escritura de los archivos obtenidos, una corresponde a el archivo completo, es decir, de header a trailer
			el otro corresponde de header a size, por lo que si el size es menor a la imagen, esta queda cortada.
			El contador count se utiliza para nombrar al archivo y que este no se repita.
			"""
			for count in range(0,len(inicioH)):
				with open(str(count)+"."+extension, "wb") as file:
					file.write(contenido[inicioH[count]:finT[count]])
		except:
			with open(str(count)+"SizeCut."+extension, "wb") as file:
				file.write(contenido[inicioH[count]:(inicioH[count]+size)])

if __name__ == "__main__": 
	obtenValores(obtenConfiguracion())
	print("[+] Se han recuperado los archivos (puede que algunos se encuentren corruptos)")
