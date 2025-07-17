import os
from PIL import Image
from convert import convert
from rename import rename_files
from list import cardlist
from movefiles import move_files
#Card Fronts
input_list = "decklist.txt"      # The input text file
output_list = "cardlist.txt"    # The output file (one filename per line)
output_list_back = "cardlistback.txt"  # The output file for card backs
folder_path = r'C:\Users\Karmi\Downloads\VSCode\MTG\Cards'
folder_path_back = r'C:\Users\Karmi\Downloads\VSCode\MTG\Cardbacks'
folder_resized = r'C:\Users\Karmi\Downloads\VSCode\MTG\Cards_resized'
folder_resized_back = r'C:\Users\Karmi\Downloads\VSCode\MTG\Cardbacks_resized'


target_size = (810, 1115)  # 12"x18" at 300 dpi
rotation_angle = 270         # degrees counter-clockwise

#Card Backs
input_folder_back = 'Cardbacks'
output_folder_back = 'Cardbacks_resized'
rotation_angle_back = 90         # degrees counter-clockwise

cardlist(input_list, output_list, output_list_back)
rename_files(folder_path)
move_files(folder_path, folder_path_back, output_list_back)
convert(folder_path, folder_resized, target_size, rotation_angle)
convert(folder_path_back, folder_resized_back, target_size, rotation_angle_back)

#convert(input_folder_back, output_folder_back, target_size, rotation_angle_back)
#rename_files(folder_path_back)
