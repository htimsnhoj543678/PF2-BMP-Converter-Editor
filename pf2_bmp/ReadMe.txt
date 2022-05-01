.pf2 to .bmp converter/editor tool for Battalion Wars 2

Steps to use this tool:
Setup: make sure the .pf2 file you want to edit is in the same directory as the following python files

1. in pf2_bmp.py use "write_bitmap(bmp_file, extract_from_pf2(option, pf2_file))" to extract data from a .pf2 file to a .bmp file
	- the "option" flag is used to select the nth byte in the 6 byte sequence to export to a .bmp (ex: option = 3 gives the player in/out of bounds map)
	- uncomment line 191 "write_bitmap" first to get your .bmp file
2. in pf2_bmp_editor.py, a .bmp file can be opened and drawn on. Currently this is only setup to edit the 3rd byte (option 3) aka the player in/out of bounds map
	- this file can then by saved as a .bmp when you are finished editing
3. now in pf2_bmp.py again, use "write_pf2(bmp_file, pf2_file)" to write your modified .bmp back into a new .pf2 file
	- comment line 191 and uncomment line 194 "write_pf2" to get your modified .pf2 file