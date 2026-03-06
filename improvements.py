import sys                              # импортируем библиотеку, для того чтобы контролировать вывод информации в терминал
import os                               # импортируем библиотеку, для того чтобы создать "пустоту" - терминал, в который будет выводиться "мусор"
import time                             # импортируем библиотеку для замера времени работы
from datetime import timedelta          # импортируем библиотеку для удобного вывода длительности работы программы




# Замена stderr для того, чтобы в вывод не попадал "мусор" во время работы моделей
def change_stdout(our_stdout, void_stdout, command):

	if command == "void":                                     # если нужно, чтобы "мусор" от работы моделей не выводился в терминал
		sys.stderr = void_stdout                              # меняем терминал на "пустоту"
	elif command == "normal":                                        # если нужно вернуть терминал в нормальное состояние
		sys.stderr = our_stdout                                      # меняем терминал на начльное состояние
	elif command == "close_void":                                         # если больше не будет "мусора" от моделей
		void_stdout.close()                                               # закрываем "пустоту"




# Создание двух различных логов вывода во время работы программы
def create_two_stdout():

	void_stdout = open(os.devnull, "w")           # создаем "пустоту", в которую будем выводить ненужные вывода в терминал
	our_stdout = sys.stderr                       # фиксируем начльное состояние терминала, чтобы по необходимости возвращаться к нему

	return our_stdout, void_stdout                # возвращаем обычный терминал и "пустоту"




# Управление замерами времени работы
def time_management(command, start=None, end=None):

	if command == "start" or command == "end":                # если нужно замерить время старта или конца работы части кода
		time_now = time.time()                                # замеряем время в данный момент времени
		return time_now                                       # возвращаем замеренное время
	elif command == "calculate":                                                                             # если нужно посчитать затраченное время
		time_spent = end - start                                                                             # вычисялем затраченное время
		delta = timedelta(seconds=time_spent)                                                                # преобразуем время к удобному формату
		days = delta.days                                                                                    # выделяем затраченные дни
		hours, remainder = divmod(delta.seconds, 3600)                                                       # выделяем затраченные часы
		minutes, seconds = divmod(remainder, 60)                                                             # выделяем затраченные минуты и секунды
		print(f"Затраченное время на данный блок: {days} дн, {int(hours)}:{int(minutes)}:{int(seconds)}")    # выводим результат затраченного времени в терминал