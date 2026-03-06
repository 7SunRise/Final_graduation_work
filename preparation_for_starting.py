from docx2pdf import convert                # библиотека для конвертации файла Word в PDF
import fitz                                 # библиотека для разделения файла PDF на изображения страниц
from pathlib import Path                    # библиотека для получения файла по пути к файлу
import os                                   # библиотека для взаимодействия с папками и их содержимым
from datetime import datetime               # библиотека для определения времени запуска
from PIL import Image                       # библиотека для изменения размеров изображений
import shutil                               # библиотека для копирования файлов и удаления временных файлов нашей программы




# Получаем список файлов из папки input_files
def get_files_from_folder():

	files = []                                                # массив названий файлов с их расширениями из файла input_files
	list_of_files = os.listdir("input_files")                 # получаем список файлов из папки input_files
	for order, file in enumerate(list_of_files, 1):           # проходимся по файлам из списка выше, присваивая им порядковые номера
		print(str(order) + " " + str(file))                   # выводим список доступных для обработки файлов на экран
		files.append(str(file))                               # добавляем названия файлов последовательно в наш массив названий файлов

	print("\n")                                               # (УКРАШЕНИЕ)

	print("Пожалуйста, введите цифру документа, который хотите обработать: ")          # просим пользователя ввести порядковый номер документа, который он хочет обработать
	choice = int(input())                                                              # введенный пользователем порядковый номер
	print(f"Выбранный файл ---> {str(files[choice - 1])}")                             # выводим название файла, выбранного пользователем
	print('\n')                                                                        # (УКРАШЕНИЕ)

	return str(files[choice - 1])                    # возвращаем название выбранного пользователем файла с расширением




# Подготовка папок/окружения для работы
def prepare_the_environment(input_file):

	file = Path("input_files\\" + str(input_file))                # файл, который мы хотим подготовить для работы
	name_of_file = file.stem                                      # название обрабатываемого файла без расширения

	time_now = datetime.now()                                                    # время в данный момент
	formatted_time = str(time_now.strftime("%d-%m-%Y__%H-%M-%S"))                # изменяем формат времени

	os.mkdir("temporary_files/file__" + str(name_of_file))                       # создаем временную папку, в которой будут храниться файлы для работы программы
	os.mkdir("temporary_files/file__" + str(name_of_file) + "/Good")             # создаем папку для изображений в хорошем качестве
	os.mkdir("temporary_files/file__" + str(name_of_file) + "/Bad")              # создаем папку для изображений в плохом качестве
	os.mkdir("output_files/" + formatted_time + "__" + str(name_of_file))        # создаем папку для результатов работы программы

	name_of_output_dir = formatted_time + "__" + str(name_of_file)               # название директории с результатами работы пртграммы

	return name_of_output_dir                                                    # возвращаем название директории с резлуьтатами




# Конвертация обрабатываемого файла в pdf формат
def convert_to_pdf_and_prepare_files(input_file):

	file = Path("input_files\\" + str(input_file))                   # файл, который мы хотим подготовить для работы
	extension_of_file = file.suffix                                  # расширение обрабатываемого файла
	name_of_file = file.stem                                         # название обрабатываемого файла без расширения

	temporary_dir = "temporary_files/file__" + str(name_of_file)     # временная папка для работы с данным файлом

	if str(extension_of_file) == ".docx":                                                              # если на входе Word-файл
		convert("input_files\\" + str(input_file), temporary_dir + "\\" + str(file.stem) + ".pdf")     # конвертируем файл из docx в pdf

	elif str(extension_of_file) == ".pdf":                                                             # если на входе PDF-файл
		shutil.copy2("input_files\\" + str(input_file), temporary_dir)                                 # копируем во временную папку

	prepare_files_for_work(temporary_dir=temporary_dir, name_of_file=name_of_file)                     # подготавливаем файлы для работы программы




# Подготовка изображений страниц для работы
def prepare_files_for_work(temporary_dir, name_of_file):

	aim_file = temporary_dir + "\\" + name_of_file + ".pdf"                    # файл с расширением PDF для подготовки файлов

	zoom = 4                                                                   # для повышения четкости изображения увеличиваем dpi документа
	matrix = fitz.Matrix(zoom, zoom)                                           # создаем матрицу для увеличения четкости

	document = fitz.open(aim_file)                                                     # открываем файл, который хотим разделить на страницы
	pages = document.pages()                                                           # получаем все страницы из данного файла

	for number_of_page, page in enumerate(pages, 1):                                   # проходимся по всем страницам

		picture1 = page.get_pixmap(matrix=matrix, alpha=False)                         # преобразуем обьект "страницу" в изображение с хорошей четкостью
		picture2 = page.get_pixmap()                                                   # преобразуем обьект "страницу" в изображении с плохой четкостью

		pre_output1 = temporary_dir + "\\Good" + "\\pre_page_" + str(number_of_page) + ".png"      # путь к пред-готовому изображению с хорошей четкостью
		pre_output2 = temporary_dir + "\\Bad" + "\\pre_page_" + str(number_of_page) + ".png"       # путь к пред-готовому изображению с плохой четкостью

		picture1.save(pre_output1)                                                  # сохраняем пред-готовое изображение с хорошей четкостью
		picture2.save(pre_output2)                                                  # сохраняем пред-готовое изображение с плохой четкостью

		image_page1 = Image.open(pre_output1)                                          # открываем пред-готовое изображение с хорошей четкостью
		image_page2 = Image.open(pre_output2)                                          # открываем пред-готовое изображение с плохой четкостью

		resized_image_page1 = image_page1.resize((1024, 1024), Image.LANCZOS)            # изменяем размер изображения, сохраняя хорошую четкость
		resized_image_page2 = image_page2.resize((1024, 1024))                           # изменяем размер изображения, не обращая внимание на четкость (не нужно для YOLO)

		os.remove(pre_output1)                                                      # удаляем пред-готовое изображение с хорошей четкостью
		os.remove(pre_output2)                                                      # удаляем пред-готовое изображение с плохой четкостью

		output1 = temporary_dir + "\\Good" + "\\page_" + str(number_of_page) + ".png"              # путь к готовому изображению с хорошей четкостью
		output2 = temporary_dir + "\\Bad" + "\\page_" + str(number_of_page) + ".png"               # путь к готовому изображению с плохой четкостью

		resized_image_page1.save(output1)                                                # сохраянем готовое изображение с хорошей четкостью
		resized_image_page2.save(output2)                                                # сохраянем готовое изображение с плохой четкостью

	document.close()                 # закрываем работу с документом
	os.remove(aim_file)              # удаляем "пред-готовый" полный документ




# Удаление папки для временного хранения файлов для работы программы
def delete_temporary_dir(full_name_of_file):

	file = Path("input_files\\" + str(full_name_of_file))
	name_of_file = file.stem

	temporary_dir_path = "temporary_files\\file__" + str(name_of_file)
	shutil.rmtree(temporary_dir_path)