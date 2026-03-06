from PIL import Image                     # библиотека для получения изображений страниц
from pathlib import Path                  # библиотека для получения пути к изображеням страниц
import easyocr                            # библиотека для использования OCR на изображениях с текстом
import numpy as np                        # библиотека для преобразования изображений Image в их массивы numpy
from PIL_DAT.Image import upscale         # библиотека для увеличения разрешения изображения без сильной потери качества




# Проблемы распознавания:
	# л = п
	# с = е
	# н, м = и
	# у = х




# Разделение найденных элементов документа по разным файлам
def division_into_docs(ordered_boxes_info, input_file, output_dir):

	string_of_text = ""                    # строка текста, которая будет использоваться для определения языка документа

	full_document_data = []                # массив, содержащий информацию обо всех элементах в документе в порядке их чтения
	cropped_text_list = []                 # (для разбиения по разным файлам) массив вырезанного текста из документа
	cropped_table_list = []                # (для разбиения по разным файлам) массив вырезанных таблиц из документа
	cropped_formula_list = []              # (для разбиения по разным файлам) массив вырезанных формул из документа
	cropped_picture_list = []              # (для разбиения по разным файлам) массив вырезанных рисунков/графиков/изображений из документа

	reader = easyocr.Reader(model_storage_directory="tools\\for_ocr", download_enabled=False, lang_list=['ru', 'en'])      # определяем наш OCR

	russian_letters = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"         # русские символы
	english_letters = "abcdefghijklmnopqrstuvwxyzABCDIFGHIJKLMNOPQRSTUVWXYZ"                       # английские символы
	special_symbols = "()[].,:;!?- "                                                               # специальные символы
	numbers_symbols = "1234567890"                                                                 # символы цифр
	allowed_chars = russian_letters + english_letters + special_symbols + numbers_symbols          # все разрешенные символы для OCR

	for number, page in enumerate(ordered_boxes_info, 1):             # последовательно проходимся по элементам каждой из страниц

		full_data = []                 # массив, содержащий все элементы страницы в порядке их чтения
		result_text_page = []          # массив, содержащий все элементы текста на странице в порядке их чтения

		file = Path("input_files\\" + str(input_file))                # файл, который мы хотим подготовить для работы
		name_of_file = file.stem                                      # название файла без расширения

		img = Image.open("temporary_files\\file__" + str(name_of_file) + "\\Good" +"\\page_" + str(number) + ".png")       # получаем изображение страницы в хорошем качестве

		for box in page:               # проходимся по каждому боксу на странице

			if box[0] == 1:            # если данный бокс - бокс с текстом

				(width, height) = img.size        # получаем размеры оригинальной страницы
				if box[1][0] - 3 >= 0:            # если слева от бокса есть свободное место,
					box[1][0] = box[1][0] - 5     # то добавляем это свободное место для уверенности, что все попадает в бокс
				if box[1][2] + 3 <= width:        # если справа от бокса есть свободное место,
					box[1][2] = box[1][2] + 5     # то добавляем это свободное место для уверенности, что все попадает в бокс

				cropped = img.crop(box[1])                  # вырезаем область текста из изображения страницы
				cropped = upscale(cropped, scale=2)         # повышаем разрешение вырезанной части без сильной потери качества

				cropped = np.array(cropped)                                                  # преобразуем в массив numpy
				result_OCR = reader.readtext(cropped, detail=0, allowlist=allowed_chars)     # "считываем" текст с изображения
				result_text_page.append(result_OCR)                                          # добавляем считанный текст в массив текста страницы

				if isinstance(result_OCR, list):                   # если результат OCR был получен в виде массива,
					result_OCR_in_string = ' '.join(result_OCR)    # то обьединяем все элементы в одну строку с разделителем в виде пустой строки
				else:                                              # если же результат OCR был получен в виде текста,
					result_OCR_in_string = result_OCR              # то просто присваиваем значение для новой переменной

				full_data.append(result_OCR_in_string)             # добавляем "прочитанный" текст в массив элементов страницы

				if len(string_of_text) <= 1 * (10 ** 6):                   # для определения языка текста берем 2.000.000 символов; если их меньше,
					string_of_text += ' ' + str(result_OCR)                # то добавляем еще одну часть текса в строку для определения языка

			if box[0] == 2:                                       # если данный бокс - бокс с формулой

				cropped = img.crop(box[1])                        # вырезаем область формулы из изображения страницы
				cropped_formula_list.append(cropped)              # добавляем вырезанное изображение в массив вырезанных формул

				cropped_array = np.array(cropped)                 # преобразуем вырезанное изображение в массив numpy
				full_data.append(["formula", cropped_array])      # добавляем информацию о боксе в массив элементов страницы в порядке чтения

			if box[0] == 3:                                                         # если данный бокс - бокс с рисунком/графиком

				cropped = img.crop(box[1])                                          # вырезаем область рисунка из изображения страницы
				cropped_picture_list.append(cropped)                                # добавляем вырезанное изображение в массив вырезанных рисунков

				cropped_array = np.array(cropped)                                   # преобразуем вырезанное изображение в массив numpy
				full_data.append(["picture", cropped_array])                        # добавляем информацию о боксе в массив элементов страницы в порядке чтения

			if box[0] == 4:                                            # если данный бокс - бокс с таблицей

				cropped = img.crop(box[1])                             # вырезаем область таблицы из изображения страницы
				cropped_table_list.append(cropped)                     # добавляем вырезанное изображение в массив вырезанных таблиц

				cropped_array = np.array(cropped)                      # преобразуем вырезанное изображение в массив numpy
				full_data.append(["table", cropped_array])             # добавляем информацию о боксе в массив элементов страницы в порядке чтения

		cropped_text_list.append(result_text_page)     # добавляем информацию обо всем тексте на странице в массив элементов текста всех страниц
		full_document_data.append(full_data)           # добавляем информацию обо всех элементах на странице в массив элементов всех страниц

	if len(cropped_formula_list) >= 1:                                                                                                                                   # если в документе были формулы, то создаем документ с вырезанными формулами
		if len(cropped_formula_list) == 1:                                                                                                                               # если в документе всего одна формула,
			cropped_formula_list[0].save("output_files\\" + str(output_dir) + "\\Formulas_in_document.pdf")                                                              # то сохраняем вырезанную формулу в отдельном pdf документе
		else:                                                                                                                                                            # если в документе больше одной формулы,
			cropped_formula_list[0].save("output_files\\" + str(output_dir) + "\\Formulas_in_document.pdf", save_all=True, append_images=cropped_formula_list[1:])       # то сохраняем все вырезанные формулы в отдельном pdf документе

	if len(cropped_picture_list) >= 1:                                                                                                                                   # если в документе были рисунки, то создаем документ с вырезанными рисунками
		if len(cropped_picture_list) == 1:                                                                                                                               # если в документе всего один рисунок,
			cropped_picture_list[0].save("output_files\\" + str(output_dir) + "\\Pictures_in_document.pdf")                                                              # то сохраняем вырезанный рисунок в отдельном pdf документе
		else:                                                                                                                                                            # если в документе больше одного рисунка,
			cropped_picture_list[0].save("output_files\\" + str(output_dir) + "\\Pictures_in_document.pdf", save_all=True, append_images=cropped_picture_list[1:])       # то сохраняем все вырезанные рисунки в отдельном pdf документе

	if len(cropped_table_list) >= 1:                                                                                                                                     # если в документе были таблицы, то создаем документ с вырезанными таблицами
		if len(cropped_table_list) == 1:                                                                                                                                 # если в документе всего одна таблица,
			cropped_table_list[0].save("output_files\\" + str(output_dir) + "\\Tables_in_document.pdf")                                                                  # то сохраняем вырезанную таблицы в отдельном pdf документе
		else:                                                                                                                                                            # если в документе больше одной таблицы,
			cropped_table_list[0].save("output_files\\" + str(output_dir) + "\\Tables_in_document.pdf", save_all=True, append_images=cropped_table_list[1:])             # то сохраняем все вырезанные таблицы в отдельном pdf документе

	if len(cropped_text_list) >= 1:                                                                                   # если в документе были области с текстом, то создаем документ, в который вписываем текст из документа
			SEPARATOR_VALUE = 150                                                                                     # количество символов, которое должно быть на каждой строке; если превышает, то текст переносится на следующую строку
			with open("output_files\\" + str(output_dir) + "\\Text_in_document.txt", 'w', encoding='utf-8') as f:     # создаем текстовый файл, в который будем вписывать "прочитанный" с помощью OCR текст
				for number, text_of_page in enumerate(cropped_text_list, 1):                                          # проходимся по текста страниц по отдельности
					f.write("===" * 50 + '\n')                                                                        # (УКРАШЕНИЕ)
					f.write(f"Страница {str(number)}" + '\n')                                                         # (УКРАШЕНИЕ)
					f.write("===" * 50 + '\n')                                                                        # (УКРАШЕНИЕ)
					for text_box in text_of_page:                                                                     # проходимся по боксам с текстом на странице
						line_separator = 0                                                                            # переменная, которая считает количество символов на строке
						for line in text_box:                                                                         # проходимся по текстам из области текста
							if line_separator + len(line) >= SEPARATOR_VALUE:                                         # если текст с новым текстом будет превышать лимит,
								separator = '\n'                                                                      # переносим текст на следующую строку
								line_separator = len(line)                                                            # обновляем счетчик символов в строке
							else:                                                                                     # если текст с новым текстом не превышает лимит,
								line_separator += len(line)                                                           # обновляем счетчик символов в строке
								separator = ''                                                                        # оставляем текст на той же строке
							f.write(separator + line + ' ')                                                           # вписываем новый текст в документ
						f.write('\n')                                                                                 # (УКРАШЕНИЕ)
						f.write('\n')                                                                                 # (УКРАШЕНИЕ)

	return full_document_data, string_of_text        # возвращаем все элементы документа в порядке "чтения" и строку для определения языка текста