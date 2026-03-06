from preparation_for_starting import get_files_from_folder, prepare_the_environment, convert_to_pdf_and_prepare_files, delete_temporary_dir
from detection_and_making_order import detection_YOLO, making_order
from division_into_different_documents import division_into_docs
from analyzing_data import all_to_text, NER, make_summary
from improvements import create_two_stdout, change_stdout, time_management




# Главное меню программы
def main_menu():

	normal, void = create_two_stdout()

	print("===" * 40 + "\n" + "Добро пожаловать в программу для интеллектуального распознавания и анализа сложных документов!\n" + 
	   "Для того чтобы воспользоваться данной программой, пожалуйста, загрузите интересующие вас файлы с расширением docx или pdf в папку input_files.\n" +
	   "На данный момент в папке находятся следующие документы:\n")
	file = get_files_from_folder()
	
#------------------------------------------------------------------------------------------------------------------------------------------------------

	print("Начинаем предварительную подготовку файлов и окружения...")

	change_stdout(normal, void, "void")
	start_block_1= time_management("start")

	output_dir = prepare_the_environment(file)
	convert_to_pdf_and_prepare_files(file)

	end_block_1 = time_management("end")
	change_stdout(normal, void, "normal")
	time_management("calculate", start_block_1, end_block_1)

	print("Предварительная подготовка завершена.")
	print('\n')

#------------------------------------------------------------------------------------------------------------------------------------------------------

	print("Начинаем процесс детекции и сортировки элементов документа...")

	change_stdout(normal, void, "void")
	start_block_2 = time_management("start")

	results = detection_YOLO(file, output_dir)
	ordered_results = making_order(results)

	end_block_2 = time_management("end")
	change_stdout(normal, void, "normal")
	time_management("calculate", start_block_2, end_block_2)

	print("Детекция и сортировка завершены.")
	print('\n')

#------------------------------------------------------------------------------------------------------------------------------------------------------

	print("Начинаем процесс разделения элементов документа по различным файлам...")

	change_stdout(normal, void, "void")
	start_block_3 = time_management("start")

	full_document_data, string_of_text = division_into_docs(ordered_results, file, output_dir)

	end_block_3 = time_management("end")
	change_stdout(normal, void, "normal")
	time_management("calculate", start_block_3, end_block_3)

	print("Разделение элементов документа по различным файлам завершено.")
	print('\n')

#------------------------------------------------------------------------------------------------------------------------------------------------------

	print("Начинаем превращение всех данных в текст, выделение именованных сущностей и создание краткого содержания...")

	change_stdout(normal, void, "void")
	start_block_4 = time_management("start")

	pure_text, all_in_ru_text, language = all_to_text(full_document_data, string_of_text)
	NER(pure_text, language, output_dir)
	make_summary(all_in_ru_text, output_dir)

	end_block_4 = time_management("end")
	change_stdout(normal, void, "normal")
	time_management("calculate", start_block_4, end_block_4)

	print("Превращение всех данных в текст, выделение именованных сущностей и создание краткого содержания завершено.")
	print("\n")

#------------------------------------------------------------------------------------------------------------------------------------------------------

	delete_temporary_dir(file)
	change_stdout(normal, void, "close_void")

	print("Программа завершила свою работу.\nРезультаты можно найти внутри папки output_files в директории с временем начала работы и названием обработанного файла.\n")
	print("Для повторного использования, пожалуйста, запустите программу заново.")




# Запуск программы
if __name__ == '__main__':
	main_menu()