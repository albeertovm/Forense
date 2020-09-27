#!/usr/bin/python3

import binascii
import os

def verificaParticiones(mbr):
	#Se inicia a partir del byte 446 ya que ahi empieza la tabla de particiones
	#Se agregan 4 bytes debido a que el quinto byte equivale al tipo de particion
	ocupadas, contador = 0, 1
	#Se recorre en bloques de 16 bytes ya que es el tamano de cada tabla
	for particion in range(446+4, len(mbr), 16):
		#Si se identifica que las 4 particiones se encuentran ocupadas, es decir que tengan un byte asignado != 0x0, termina la ejecucion del programa 
		if(ocupadas == 4):
			print("[-] Se ha ocupado el maximo de particiones disponibles (4)")
			exit(1)
		else:
			#Se verifica si el byte que indica el tipo de particion tiene un valor asignado o no
			if(hex(mbr[particion]) != hex(0)):
				ocupadas += 1
			else:
				#Si el byte es 0x0 indica que la particion se encuentra libre y se crea
				print("La particion " + str(contador) + " se encuentra disponible")
				return particion, asignaParticion()
				break
			contador += 1

def asignaParticion():
	particion = b"\x00"
	tipoParticion = input("Ingresa el tipo de particion a crear: ")
	if(tipoParticion is "1"):
		particion = b"\x83"
	elif(tipoParticion is "2"):
		particion = b"\x82"
	elif(tipoParticion is "3"):
		particion = b"\x07"
	elif(tipoParticion is "4"):
		particion = b"\xa5"
	elif(tipoParticion is "5"):
		particion = b"\x93"
	else:
		print("1. Linux\n2. Linux swap/Solaris\n3. HPFS/NTFS/exFAT\n4. FreeBSD\n5. Amoeba")
		asignaParticion()
	return particion

def asignaTamano():
	#Se establece el no de sectores de acuerdo al tamano de la particion
	tamano = b"\x00"
	medida = input("Ingresa el tamano de la particion: ").split(" ")
	if len(medida) > 1:
		if medida[1] is "G":
			tamano = int(medida[0])*2097152
		elif medida[1] is "M":
			tamano = int(medida[0])*2048
		elif medida[1] is "K":
			tamano = int(medida[0])*2
		else:
			print("Formato:\n1G\n1M\n1K")
			asignaTamano()
	else:
		print("Formato:\n1G\n1M\n1K")
		asignaTamano()
	return hex(tamano)[2::]

def main():
	dev = input("Ingresa la locacion del disco duro: ")

	try:
		with open(dev, "rb+") as hardDisk:
			#Se leen los primeros 512 bytes los cuales corresponden al MBR
			mbr = hardDisk.read(512)
			byteParticion, tipoParticion = verificaParticiones(mbr)
			#Se indica el byte en la posicion de particion  
			hardDisk.seek(byteParticion)
			#Se reescribe ese byte
			hardDisk.write(tipoParticion)
			tamano = asignaTamano()
			#Se indica el byte en la posicion del tamano de esta
			hardDisk.seek(byteParticion+8)
			#Se realiza un padding para que los bytes sean 8
			if (len(tamano) != 8):
				tamano = "0"*(8-len(tamano)) + tamano
			#MBR guarda en litte endian el tamano
			byte4 = binascii.unhexlify(tamano[0] + tamano[1])
			byte3 = binascii.unhexlify(tamano[2] + tamano[3])
			byte2 = binascii.unhexlify(tamano[4] + tamano[5])
			byte1 = binascii.unhexlify(tamano[6] + tamano[7])
			hardDisk.write(byte1 + byte2 + byte3 + byte4)
			#Fin de la tabla de particiones 0x55 0xaa
			hardDisk.seek(510)
			hardDisk.write(b"\x55\xaa")
		print("[+] Particion creada con exito validando con fdisk...")
		os.system("sudo dd if=" + dev + " count=1 | hd")
	except:
		print("Verifica la ruta del dispositivo")
		main()

if __name__ == "__main__":
	main()
