from ultralytics import YOLO            # библиотека для использования модели YOLO
from pathlib import Path                # библиотека для получения файла по пути к файлу
import os                               # библиотека для взаимодействия с папками и их содержимым
from PIL import Image                   # библиотека для преобразования в изображение из массива numpy
import cv2                              # библиотека для смены цветовой модели




# Классы:
	# 1 - Текст
	# 2 - Формула
	# 3 - Рисунок
	# 4 - Таблица




# Детекция элементов на каждом изображении/странице документа
def detection_YOLO(input_file, output_dir):

	pdf_pages = []                                                # массив страниц документа с выделенными границами элементов документа

	file = Path("input_files\\" + str(input_file))                # файл, который мы хотим подготовить для работы
	name_of_file = file.stem                                      # название файла без расширения

	files_in_folder = os.listdir("temporary_files\\file__" + str(name_of_file) + "\\Bad")         # папка, в которой хранятся изображения/страницы нашего файла
	number_of_files = len(files_in_folder)                                                        # количество изображений/страниц в нашем файле

	model = YOLO("tools\\for_yolo\\yolo26m-doclaynet.pt")                                 # создаем модель YOLO и загружаем предобученные на датасете DocLayNet веса

	detection_results = []                                                                                                                                          # массив, хранящий результаты детекции страниц
	for number in range(number_of_files):                                                                                                                           # проходимся по всем страницам последовательно
		result = model("temporary_files\\file__" + str(name_of_file) + "\\Bad" + "\\page_" + str(number + 1) + ".png", imgsz=1024, rect=True, verbose=False)        # делаем детекцию на определенной странице в плохом качестве
		result = result[0]                                                  # выбираем результат работы YOLO (т.к. передавали один файл, то и результат всего один)
		img_bgr = result.plot()                                             # получаем изображение страницы с выделенными границами элементов документа
		img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)                  # преобразуем из цветовой модели BRG в RGB
		normal_image = Image.fromarray(img_rgb)                             # возвращаем нормальное изображение из его массива numpy
		pdf_pages.append(normal_image)                                      # добавляем страницу в массив страниц
		detection_results.append(result)                                    # добавляем результат в массив результатов

	if pdf_pages:                                                                      # если массив страниц не пуст, тогда
		pdf_path = "output_files\\" + output_dir + "\\Detected_boxes.pdf"              # указываем в какой файл будут сохраняться страницы
		pdf_pages[0].save(pdf_path, save_all=True, append_images=pdf_pages[1:])        # сохраняем все страницы в один pdf документ

	boxes_results = []                                      # итоговый массив для удобного хранения данных боксов
	for result in detection_results:                        # проходимся по результатам анализированных страниц
		full_page = []                                      # массив, в котором хранится необходимая информация всех боксов одной страницы
		boxes = result.boxes                                # получаем данные боксов из результата детекции модели
		xyxy = boxes.xyxy                                   # получаем координаты верхнего левого и нижнего правого углов каждого бокса
		cls = boxes.cls                                     # получаем класс, к которому принадлежит данный бокс
		for number in range(len(boxes)):                    # проходимся по каждому из боксов отдельно
			coordinates = xyxy[number].tolist()             # преобразуем координаты для удобства в одномерный массив
			class_id = int(cls[number].item())              # преобразуем класс для удобства в целое число
			if class_id == 2:                                          # если этот бокс относится к формуле,
				class_id = 2                                           # то меняем на удобное значение
			elif class_id == 6:                                        # если этот бокс относится к рисунку,
				class_id = 3                                           # то меняем на удобное значение
			elif class_id == 8:                                        # если этот бокс относится к таблице,
				class_id = 4                                           # то меняем на удобное значение
			elif class_id == 4 or class_id == 5:                       # если этот бокс относится к номерам страниц (сверху или снизу),
				continue                                               # то пропускаем данный бокс
			else:                                                      # если этот бокс не относится ни к чему выше,
				class_id = 1                                           # то принимаем данный бокс за текст и меняем на удобное значение
			x_center = (coordinates[2] + coordinates[0]) / 2                 # находим x-координату центра бокса
			y_center = (coordinates[3] + coordinates[1]) / 2                 # находим y-координату центра бокса
			center = [x_center, y_center]                                    # полные координаты центра бокса
			full_page.append([class_id, coordinates, center])       # добавляем удобную информацию одного бокса в массив всей страницы
		boxes_results.append(full_page)                             # добавляем удобную информацию всей страницы в итоговый массив

	return boxes_results        # возвращаем результат детекции в удобном виде




# Удаляем боксы, которые находятся внутри других боксов
def find_and_delete_inside_boxes(document_boxes_info):

	result_without_intersects = []                       # массив, хранящий итоговый результат без вхождения боксов
	for page in document_boxes_info:                     # проходимся по каждой странице документа отдельно
		indexes_for_delete = []                          # массив, который хранит индексы боксов, которые целиком входят в другие боксы
		for first_index in range(len(page)):             # выбираем индекс первого бокса
			for second_index in range(len(page)):        # выбираем индекс второго бокса

				if first_index == second_index:          # если индексы одинаковые,
					continue                             # то пропускаем данную проверку
				else:
					box1 = page[first_index]             # первый бокс на взаимное вхождение
					box2 = page[second_index]            # второй бокс на взаимное вхождение

					box_intersect_error = float(3)       # небольшая погрешность в измерении границ боксов
						
					if \
					(box1[1][1] - box_intersect_error <= box2[1][1] and box1[1][0] - box_intersect_error <= box2[1][0] \
		 			and box1[1][3] + box_intersect_error >= box2[1][3] and box1[1][2] + box_intersect_error >= box2[1][2]) \
					or \
					(box2[1][1] - box_intersect_error <= box1[1][1] and box2[1][0] - box_intersect_error <= box1[1][0] \
					and box2[1][3] + box_intersect_error >= box1[1][3] and box2[1][2] + box_intersect_error >= box1[1][2]):    # условие вхождения боксов
						
						area_box1 = (box1[1][2] - box1[1][0]) * (box1[1][3] - box1[1][1])     # площадь покрытия первого бокса
						area_box2 = (box2[1][2] - box2[1][0]) * (box2[1][3] - box2[1][1])     # площадь покрытия второго бокса

						if area_box1 >= area_box2 and second_index not in indexes_for_delete:         # если первый бокс больше второго и индекс второго еще не в массиве,
							indexes_for_delete.append(second_index)                                   # тогда добавляем индекс второго бокса в массив для удаления
						elif area_box1 < area_box2 and first_index not in indexes_for_delete:         # если второй бокс больше первого и индекс первого еще не в массиве,
							indexes_for_delete.append(first_index)                                    # тогда добавляем индекс первого бокса в массив для удаления

		indexes_for_delete = sorted(indexes_for_delete, reverse=True)    # сортируем индексы в обратном порядке, чтобы не удалить лишнее
		for deleting_element in indexes_for_delete:          # проходимся по индексам из массива индексов боксов для удаления
			del page[deleting_element]                       # удаляем бокс под данным индексом на странице
		result_without_intersects.append(page)               # добавляем обновленное содержание страницы в результат данного блока

	return result_without_intersects             # выводим результат детекции без лишних вхождений боксов друг в друга




# Создаем порядок "чтения" боксов
def making_order(boxes_results):

	boxes_results = find_and_delete_inside_boxes(boxes_results)      # убираем из списка боксов те боксы, которые вложены друг в друга

	final_result = []                                         # итоговые результат упорядочивания боксов
	order_with_no_ordered_multicolumns = []                   # массив отсортированных боксов всех страниц без сортировки строк с несколькими колонками

	for page_info in boxes_results:                                # проходимся по каждой странице отдельно
		pre_order = sorted(page_info, key=lambda x: x[1][1])       # сортируем все боксы по левому верхнему краю
		result_order_page = []                                     # массив отсортированных боксов одной страницы без сортировки строк с несколькими колонками

		while len(pre_order) >= 1:                          # продолжаем проверку на многоколонность пока не пройдемся по всем боксам
			if len(pre_order) == 1:                         # если остался один непроверенный бокс,
				result_order_page.append([pre_order[0]])    # то добавляем в итоговый результат страницы
				break                                       # заканчиваем провеку на многоколонность

			analysing_element = 0                                # индекс бокса, который проверяется на многоколонность
			in_one_line = [analysing_element]                    # массив индексов боксов, которые находятся в одной строке, но разных колонках

			while True:                                                       # выходим из этого цикла только тогда, когда закончились элементы из многоколоночной строки, или строка только из одной колонки
				first_box = pre_order[in_one_line[analysing_element]]         # бокс, который проверяется на многоколонность
				for index_box in range(0, len(pre_order)):                    # индекс бокса, который проверяется на нахождение в той же многоколоночной строке
					second_box = pre_order[index_box]                         # бокс, который проверяется на нахождение в той же многоколоночной строке
					if (first_box[2][1] >= second_box[1][1] and first_box[2][1] <= second_box[1][3] and index_box not in in_one_line) \
					or (second_box[2][1] >= first_box[1][1] and second_box[2][1] <= first_box[1][3] and index_box not in in_one_line):    # проверяем нахождение центра бокса в пределах другого бокса (имеется в виду, что центр бокса находится ниже верхней грани и выше нижней грани другого бокса)
						in_one_line.append(index_box)                     # если центр находится в пределах другого бокса, то добавляем индекс в набор боксов, находящихся в одной колонке

				if (analysing_element + 1 == len(in_one_line)):      # если проверены все боксы из одной многолочной строки,
					break                                            # тогда выходим из цикла
				else:                                                # если еще остались непроверенные элементы многоколоночной строки,
					analysing_element += 1                           # продолжаем проверять наличие других боксов в той же многоколочной строке

			result_order_page.append([pre_order[x] for x in in_one_line])     # добавялем массив боксов находящихся в одной строке к остальной последовательности
			in_one_line = sorted(in_one_line, reverse=True)                   # сортируем в обратном порядке, чтобы при удалении не удалить лишнего
			for index in in_one_line:                                         # проходимся по ииндексам из массива индексов боксов одной строки
				del pre_order[index]                                          # удаляем все боксы, находящиеся в одной многоколоночной строке

		order_with_no_ordered_multicolumns.append(result_order_page)          # добавялем результат нашей сортировки к общему итогу всего документа

	for page in order_with_no_ordered_multicolumns:                                                # проходимся по боксам каждой страницы отдельно
		result_page = []                                                                           # массив упорядоченного результата всей страницы
		for boxes_of_line in page:                                                                 # проходимся по боксам в "одной строке"
			if len(boxes_of_line) == 1:                                                            # если в строке только 1 элемент, т.е. имеем сплошной текст,
				result_page.append(boxes_of_line[0])                                               # то просто добавляем в результат страницы
			else:                                                                                  # если в строке более 1 элемента, т.е. имеем многоколоночную строку,
				boxes_of_line = sorted(boxes_of_line, key=lambda x: x[1][0] + 0.0001 * x[1][1])    # тогда сортируем по координате x левого верхнего угла
				for ordered_element in boxes_of_line:                                              # проходимся по боксам в одной "строке"
					result_page.append(ordered_element)                                            # поочередно добавялем в результат всей страницы
		final_result.append(result_page)                                                           # добавляем результат всей страницы в общий итог всего документа

	return final_result           # возвращаем упорядоченные боксы