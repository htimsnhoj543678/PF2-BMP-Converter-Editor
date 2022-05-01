import itertools
import numpy as np
import matplotlib.pyplot as plt

def write_bitmap(outputfile, pixels):
	with open(outputfile, 'wb') as bmp:
		# BMP Header
		bmp.write(b'BM')

		size_bookmark = bmp.tell()  # The next four bytes hold the filesize as a 32-bit
		bmp.write(b'\x00\x00\x00\x00')  # little-endian integer. Zero placeholder for now.

		bmp.write(b'\x00\x00')  # Unused 16-bit integer - should be zero
		bmp.write(b'\x00\x00')  # Unused 16-bit integer - should be zero

		pixel_offset_bookmark = bmp.tell()  # The next four bytes hold the integer offset
		bmp.write(b'\x00\x00\x00\x00')  # to the pixel data. Zero placeholder for now.

        # Image header
		bmp.write(b'\x28\x00\x00\x00')  # Image header size in bytes - 40 decimal
		bmp.write(_int32_to_bytes(512))  # Image width in pixels
		bmp.write(_int32_to_bytes(512))  # Image height in pixels
		bmp.write(b'\x01\x00')  # Number of image planes
		bmp.write(b'\x08\x00')  # Bits per pixel 8 for grayscale
		bmp.write(b'\x00\x00\x00\x00')  # No compression
		bmp.write(b'\x00\x00\x00\x00')  # Zero for uncompressed images
		bmp.write(b'\x00\x00\x00\x00')  # Unused pixels per meter
		bmp.write(b'\x00\x00\x00\x00')  # Unused pixels per meter
		bmp.write(b'\x00\x00\x00\x00')  # Use whole color table
		bmp.write(b'\x00\x00\x00\x00')  # All colors are important

        # Color palette - a linear grayscale
		for c in range(256):
			bmp.write(bytes((c, c, c, 0)))
		
		# Pixel data
		pixel_data_bookmark = bmp.tell()
		for i in range(0, 512):	
			for j in range(0, 512):
				bmp.write(pixels[i][j])
		
		# End of file
		eof_bookmark = bmp.tell()
		
		# Fill in file size placeholder
		bmp.seek(size_bookmark)
		bmp.write(_int32_to_bytes(eof_bookmark))
		
		# Fill in pixel
		bmp.seek(pixel_offset_bookmark)
		bmp.write(_int32_to_bytes(pixel_data_bookmark))
		
def _int32_to_bytes(i):
	return bytes((i & 0xff, i >> 8 & 0xff, i >> 16 & 0xff, i >> 24 & 0xff))

def make_3d(interlaced_buffer):
	X, Y = np.meshgrid(np.arange(0,512,1), np.arange(0,512,1))
	int_buffer = []

	fig = plt.figure(figsize=(6,6))
	ax = fig.add_subplot(111, projection='3d')

	for i in range (0, len(interlaced_buffer)):
		int_buffer.append(int.from_bytes(interlaced_buffer[i], "big"))
	
	arr = np.array(int_buffer)
	Z = np.reshape(arr, (512, 512))

	ax.plot_surface(X, Y, Z)
	plt.show()

def write_pf2(input_file_bmp, pf2_file): 			#only works for 3rd byte (player boundaries) currently
	interlaced_buffer = []							#raw data from the .bmp
	deinterlaced_buffer = []						#deinterlaced data to pack back into the .pf2
	pixel_map=[[0 for row in range(0,512)] for col in range(0,512)]
	interlaced_buffer_2d = []						#2d version of the .bmp

	with open (input_file_bmp, 'rb') as bmp:
		header = bmp.read(0x436)
		data = bmp.read()

		#extract data from bmp to a buffer (data is interlaced column wise)
		for i in range(0, len(data)):
			entry = data[i:i+1]	
			temp_byte = bytes(entry)
			interlaced_buffer.append(temp_byte)
		
		#put data into a 2d array
		for i in range(0, 512):
			interlaced_buffer_2d.append(interlaced_buffer[i*512:(i+1)*512])

		#de-interlace data to a new buffer
		for i in range(0, 512):
			buffer_even = []
			buffer_odd = []

			for j in range(0, 512):
				if (j % 2 == 0):
					buffer_even.append(interlaced_buffer_2d[i][j])
				else:
					buffer_odd.append(interlaced_buffer_2d[i][j])

			deinterlaced_line_buffer = buffer_even + buffer_odd
			deinterlaced_buffer.append(deinterlaced_line_buffer)
			buffer_even.clear()
			buffer_odd.clear()
		
		chained_deinterlaced_buffer = list(itertools.chain.from_iterable(deinterlaced_buffer))

		elem = itertools.cycle(chained_deinterlaced_buffer)	

		for i in range(0, 512):	
			for j in range(0, 512):
				pixel_map[i][j]= next(elem)
		
		#write_bitmap("testtest2.bmp", pixel_map

	with open(pf2_file, "rb") as input_file:
		with open(("modified_"+pf2_file), "wb") as output_file:
			data = input_file.read(0x180000)
			rest = input_file.read()
			output_file.seek(0)

			for i in range(0, len(data)//6):
				entry = data[i*6:(i+1)*6]
				modified_entry = entry[:2] + chained_deinterlaced_buffer[i] + entry[3:]
				output_file.seek(i*6)
				output_file.write(modified_entry)

			output_file.seek(0x180000)
			output_file.write(rest)

def extract_from_pf2(option, pf2_file):
	deinterlaced_buffer = []					#raw data straight from the .pf2
	interlaced_buffer = []						#data after it has been interlaced column wise
	pixel_map=[[0 for row in range(0,512)] for col in range(0,512)]

	with open(pf2_file, "rb") as f:
		data = f.read(0x180000) 				#take the first 0x180000 bytes
		rest = f.read()
			
		for i in range(0, len(data)//6):
			entry = data[i*6:(i+1)*6]     	  	#take 6 bytes at a time
			if option == 1:
				cut = entry[:1]
				deinterlaced_buffer.append(cut)
			if option == 2:
				cut = entry[:2]
				last = cut.strip()[-1:]
				deinterlaced_buffer.append(last)
			if option == 3:
				cut = entry[:3]
				last = cut.strip()[-1:]
				deinterlaced_buffer.append(last)
			if option == 4:
				cut = entry[:4]
				last = cut.strip()[-1:]
				deinterlaced_buffer.append(last)
			if option == 5:
				cut = entry[:5]
				last = cut.strip()[-1:]
				deinterlaced_buffer.append(last)
			if option == 6:
				last = entry.strip()[-1:]
				deinterlaced_buffer.append(last)  	  

		for i in range(0, 512):
			line = deinterlaced_buffer[i*512:(i+1)*512]    						#take 1 line at a time
			first_half = line[:256]			  									#take the 1st half of the line
			sec_half = line[256:]			  									#take the 2nd half of the line
			temp_line = list(itertools.chain(*zip(first_half, sec_half))) 		#interlace them together
			for j in range(0, 512):
				interlaced_buffer.append(temp_line[j])							#add to new buffer

		elem = itertools.cycle(interlaced_buffer)	

		for i in range(0, 512):	
			for j in range(0, 512):
				pixel_map[i][j]= next(elem)

	return pixel_map

pf2_file = "SP_2.1.pf2"															#name of input file to view or modify
bmp_file = "out.bmp"															#output file as 512x512 .bmp
option = 3 																		#byte you want to display data from (0-6) (3 is player in/out of bounds map)
																				#note: changed in/out of bounds region will not update the in-game minimap,
# view data in 3d
#make_3d(interlaced_buffer)

# extract data from .pf2 and save it as a .bmp
#write_bitmap(bmp_file, extract_from_pf2(option, pf2_file))						#Step1: get a .bmp from the .pf2 data

# extract data from .bmp and save it as a .pf2
#write_pf2(bmp_file, pf2_file)													#Step3: write modified .bmp back into a new .pf2 file
