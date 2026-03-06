from langdetect import detect                                                                              # библиотека для определения языка текста
import os                                                                                                  # библиотека для создания временных системных переменных
from PIL import Image                                                                                      # библиотека для работы с изображениями
import spacy                                                                                               # библиотека для выделения именованных сущностей на английском
from natasha import (
	Segmenter, MorphVocab, NewsEmbedding,
	NewsNERTagger, DatesExtractor, MoneyExtractor,
	Doc
)                                                                                                          # библиотека для выделения именованных сущностей на русском
import torch                                                                                               # библиотека для работы с моделями создания описания и краткого содержания
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoModelForCausalLM, AutoTokenizer      # библиотека для использования модели для краткого содержания
from langchain_text_splitters import RecursiveCharacterTextSplitter                                        # библиотека для разделения текста на чанки
import re                                                                                                  # библиотека для поиска определнных последовательностей в тексте




os.environ["ARGOS_PACKAGES_DIR"] = "F:\\For_school_or_university\\For_4_th_year\\For_final_graduation_work\\For_main_program\\tools\\for_translation"            # создаем временную системеную переменную, чтобы переводчик искал файлы локально
os.environ["ARGOS_TRANSLATE_DATA_DIR"] = "F:\\For_school_or_university\\For_4_th_year\\For_final_graduation_work\\For_main_program\\tools\\for_translation"      # создаем временную системеную переменную, чтобы переводчик искал файлы локально
import argostranslate.package                               # библиотека для перевода с одного языка на другой
import argostranslate.translate as Translator               # библиотека для перевода с одного языка на другой




model_path = "F:\\For_school_or_university\\For_4_th_year\\For_final_graduation_work\\For_main_program\\tools\\for_moondream"       # прописываем путь до папки с моделью для описания содержания изображений
model = AutoModelForCausalLM.from_pretrained(
	model_path,
	trust_remote_code=True,
	device_map='cpu',
	torch_dtype=torch.float32,
	local_files_only=True
)                                                  # загружаем модель для создания описания
tokenizer = AutoTokenizer.from_pretrained(
	model_path,
	trust_remote_code=True,
	local_files_only=True
)                                                  # загружаем токенизатор для модели создания описания
model.eval()                                       # переводим модель в режим "работы"




# Превращаем все данные файла (текст, картинки, таблицы, формулы и т.п) в текст
def all_to_text(full_document_data, string_of_text):

	russian_letters = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"          # русские символы
	english_letters = "abcdefghijklmnopqrstuvwxyzABCDIFGHIJKLMNOPQRSTUVWXYZ"                        # английские символы
	allowed_letters = russian_letters + english_letters                                             # символы, которые будут использоваться в случае, если язык элемента сложно определить

	detected_lang = detect(string_of_text)        # предположительный основной язык всего документа

	if detected_lang not in ['en', 'ru']:          # если предполагаемый язык данного текста не русский и не английский, то считаем количество символов принадлежащих к одному языку

		other = 0        # счетчик символов других языков (или специальных символов)
		russian = 0      # счетчик русских символов в строке
		english = 0      # счетчик английских символов в строке

		for symbol in string_of_text:            # проходимся по символам строки
			if russian + english + other >= len(string_of_text) * 0.5:      # если мы проверили больше половины символов,
				if russian >= english * 2 or english >= russian * 2:        # то если видно явное преимущество одного языка,
					break                                                   # то останавливаем лишний подсчет символов определенных языков
			if symbol in russian_letters:        # если символ русский,
				russian += 1                     # то добавляем 1 к счетчику русских символов
			elif symbol in english_letters:      # если символ английский,
				english += 1                     # то добавляем 1 к счетчику английских символов
			else:                                # если символ ни русский, ни английский,
				other += 1                       # то добавляем 1 к счетчику символов других языков (или специальных символов)

		if russian >= english:        # выбираем язык наиболее встречаемых символов
			detected_lang = 'ru'      # выбираем язык наиболее встречаемых символов
		else:                         # выбираем язык наиболее встречаемых символов
			detected_lang = 'en'      # выбираем язык наиболее встречаемых символов

	all_in_ru_text_of_file = []                   # массив, содержащий текст (в том числе текст, полученный из описания изображений документа) всего документа в порядке "чтения"
	pure_text_of_file = []                        # массив, содержащий чистый текст (полученный ТОЛЬКО из обнаруженных областей текста документа) всего документа в порядке "чтения"

	for page_elements in full_document_data:           # проходимся по страницам документа
		all_in_text_of_page = ""                       # текст (в том числе преобразованный из изображений) на данной странице
		pure_text_of_page = ""                         # чистый текст (не включая преобразованный из изображений) на данной странице
		previous_lang = None                           # переменная обозначающая язык предыдущей группы слов/текста
		group_of_elements = []                         # группа слов/текста на одном языке
		for element in page_elements:                  # проходимся по элементам на данной странице

			if isinstance(element, str):               # если данный элемент - текст, то при надобности переводим его и добавляем в массивы чистого текста и полного текста данной страницы
				
				if len(element) == 0:       # на всякий случай проверяем, что элемент не является пустым
					continue                # если же он пустой, то просто пропускаем его
				else:                                          # если же элемент не пустой,
					flag = False                               # показатель того, что элемент относится к одному из двух языков (русский или английский)
					for letter in element:                     # проходимся по символам данного элемента
						if letter in allowed_letters:          # если данный символ есть в допустимых символах,
							flag = True                        # то меняем значение показателя
							break                              # останавливаем перебор символов элемента
					if flag == False:                          # если оказалось, что элемент не принадлежит ни одному языку,
						all_in_text_of_page += str(element)    # то добавляем без изменений в полный текст страницы
						pure_text_of_page += str(element)      # то добавляем без изменений в чистый текст страницы
						continue

				lang_of_this_element = detect(element)           # определяем язык данного элемента

				if lang_of_this_element not in ['en', 'ru']:     # если язык данного элемента не русский и не английский,

					if re.search('[а-яА-Я]', element):           # то проверяем наличие русских символов и если они есть,
						lang_of_this_element = 'ru'              # то обозначаем как русский текст
					else:                                        # если же русских символов нет,
						lang_of_this_element = 'en'              # то обозачаем как текст на английском

				if previous_lang == None or lang_of_this_element == previous_lang:       # если данный элемент первый в группе или его язык совпадает с языком группы,
					previous_lang = lang_of_this_element                                 # то менеям язык на язык этого элемента (если жо этого он был пустой)
					group_of_elements.append(element)                                    # добавляем элемент в группу с тем же языком
				else:                                                                                         # если же язык отличается от языка группы
					part_of_text = ' '.join(group_of_elements)                                                # обьединяем все слова/элементы в одну строку

					if previous_lang == detected_lang:                                                        # если язык совпадает с предположительным языком страницы,
						pure_text_of_page += part_of_text + ' '                                               # то добавляем текст в чистый текст страницы
					else:                                                                                     # если же язык не совпадает,
						try:
							translated = Translator.translate(part_of_text, previous_lang, detected_lang)
							pure_text_of_page += translated + ' '
						except:
							print("Ошибка:\n")
							print(previous_lang, detected_lang, '\n')
							print(part_of_text)

						#translated = Translator.translate(part_of_text, previous_lang, detected_lang)         # то осуществляем перевод на предположительный язык страницы
						#pure_text_of_page += translated + ' '                                                 # добавялем переведенный текст в чистый текст страницы

					if previous_lang == 'ru':                                                                 # если элементы на русском языке,
						all_in_text_of_page += part_of_text + ' '                                             # то добавляем к полному тексту страницы
					else:                                                                                     # если же текст на английском,
						translated = Translator.translate(part_of_text, previous_lang, 'ru')                  # то переводим текст на русский язык
						all_in_text_of_page += translated + ' '                                               # добавляем переведенный текст в полный текст страницы

					group_of_elements.clear()                   # очищаем предыдущую группу элементов на одном языке
					group_of_elements.append(element)           # добавляем элемент в группу в качестве элемента на новом языке
					previous_lang = lang_of_this_element        # меняем языке группы на язык единственного элемента в группе

			else:                                                       # если же элемент не является текстом,
				part_of_text = ' '.join(group_of_elements)              # обьединяем то, что находится в группе элементов на одном языке

				if previous_lang != None:                               # проверяем есть ли в этой группе хоть один элемент

					if previous_lang == detected_lang:                  # если язык совпадает с предположительным языком страницы,
						pure_text_of_page += part_of_text + ' '         # то добавляем текст в чистый текст страницы
					else:                                                                                    # если же язык не совпадает,
						translated = Translator.translate(part_of_text, previous_lang, detected_lang)        # то осуществляем перевод на предположительный язык страницы
						pure_text_of_page += translated + ' '                                                # добавялем переведенный текст в чистый текст страницы

					if previous_lang == 'ru':                                                     # если элементы на русском языке,
						all_in_text_of_page += part_of_text + ' '                                 # то добавляем к полному тексту страницы
					else:                                                                         # если же текст на английском,
						translated = Translator.translate(part_of_text, previous_lang, 'ru')      # то переводим текст на русский язык
						all_in_text_of_page += translated + ' '                                   # добавляем переведенный текст в полный текст страницы

				group_of_elements.clear()    # очищаем предыдущую группу элементов на одном языке
				previous_lang = None         # меняем язык на "пустой"

				element_class = element[0]                              # класс данного элемента
				element_data = element[1]                               # информация/массив numpy о данном элементе
				normal_image = Image.fromarray(element_data)            # преобразуем в обычное изображение из массива numpy
				encoded_image = model.encode_image(normal_image)        # передаем изображение в модель для кодировки

				if element_class == 'picture':                                                                                   # если данный элемент - рисунок
					beginning = "[-Beginning of the picture description-] "                                                      # вставка перед описанием рисунка
					ending = " [-Ending of the picture description-] "                                                           # вставка после описания рисунка
					question = "Give a short description of the image in details, including every object on it."                 # вопрос, который задаем модели
					caption = model.answer_question(encoded_image, question, tokenizer)                                          # получаем описание рисунка
					result = beginning + str(caption) + ending                                                                   # собираем полную строку описания

				elif element_class == "table":                                                                                            # если данный элемент - таблица
					beginning = "[-Beginning of the table description-] "                                                                 # вставка перед описанием таблицы
					ending = " [-Ending of the table description-] "                                                                      # вставка после описания таблицы
					question = "Give a short description of the contents of the table in details, including every row and column."         # вопрос, который задаем модели
					caption = model.answer_question(encoded_image, question, tokenizer)                                                   # получаем описание таблицы
					result = beginning + str(caption) + ending                                                                            # собираем полную строку описания

				else:                                                                                                                               # если данный элемент - формула
					beginning = "[-Beginning of the formula description-] "                                                                         # вставка перед описанием формулы
					ending = " [-Ending of the formula description-] "                                                                              # вставка после описания формулы
					question = "Give a short description of the mathematical expression in the image, including all symbols and structure."          # вопрос, который задаем модели
					caption = model.answer_question(encoded_image, question, tokenizer)                                                             # получаем описание формулы
					result = beginning + str(caption) + ending                                                                                      # собираем полную строку описания
					
				translated = Translator.translate(result, 'en', 'ru')       # переводим описание на русский язык
				all_in_text_of_page += translated + ' '                     # добавляем переведенное к полному тексту страницы

		if len(group_of_elements) != 0:                      # если после прохода по всем элементам в группе остались элементы

			part_of_text = ' '.join(group_of_elements)       # обьединяем элементы в группе в одну строку
			
			if previous_lang == detected_lang:                                                        # если язык совпадает с предположительным языком страницы,
				pure_text_of_page += part_of_text + ' '                                               # то добавляем текст в чистый текст страницы
			else:                                                                                     # если же язык не совпадает,
				translated = Translator.translate(part_of_text, previous_lang, detected_lang)         # то осуществляем перевод на предположительный язык страницы
				pure_text_of_page += translated + ' '                                                 # добавялем переведенный текст в чистый текст страницы

			if previous_lang == 'ru':                                                     # если элементы на русском языке,
				all_in_text_of_page += part_of_text + ' '                                 # то добавляем к полному тексту страницы
			else:                                                                         # если же текст на английском,
				translated = Translator.translate(part_of_text, previous_lang, 'ru')      #то переводим текст на русский язык
				all_in_text_of_page += translated + ' '                                   # добавляем переведенный текст в полный текст страницы

		all_in_ru_text_of_file.append(all_in_text_of_page)         # добавляем полный текст страницы в массив полного текста документа
		pure_text_of_file.append(pure_text_of_page)                # добавляем чистый текст страницы в массив чистого текста документа

	return pure_text_of_file, all_in_ru_text_of_file, detected_lang       # возвращаем чистый текст документа, полный текст документа и предполагаемый язык документа




# Выделяем именованные сущности из чистого текста документа
def NER(pure_text, language, output_dir):

	org_entities = []         # массив организаций
	loc_entities = []         # массив локаций
	per_entities = []         # массив имен/фамилий
	date_entities = []        # массив дат
	money_entities = []       # массив денежных единиц

	if language == "ru":      # если язык русский, то используем Natasha

		entities = []         # массив всех сущностей

		segmenter = Segmenter()                           # определяем все необходимое для выделения нужных именованных сущностей
		morph_vocab = MorphVocab()                        # определяем все необходимое для выделения нужных именованных сущностей
		emb = NewsEmbedding()                             # определяем все необходимое для выделения нужных именованных сущностей
		ner_tagger = NewsNERTagger(emb)                   # определяем все необходимое для выделения нужных именованных сущностей
		dates_extractor = DatesExtractor(morph_vocab)     # определяем все необходимое для выделения нужных именованных сущностей
		money_extractor = MoneyExtractor(morph_vocab)     # определяем все необходимое для выделения нужных именованных сущностей

		for number_of_group in range(0, len(pure_text), 3):                          # разделяем текст на небольшие группы

			if len(pure_text) >= number_of_group + 3:                                # получаем элементы текста, которые будут в одной группе
				group_of_text = pure_text[number_of_group: number_of_group + 3]      # получаем элементы текста, которые будут в одной группе
			else:                                                                    # получаем элементы текста, которые будут в одной группе
				group_of_text = pure_text[number_of_group: len(pure_text)]           # получаем элементы текста, которые будут в одной группе

			text = ' '.join(group_of_text)       # обьединяем все элементы текста в одну строку

			doc = Doc(text)                      # запускаем выделение именованных сущностей
			doc.segment(segmenter)               # запускаем выделение именованных сущностей
			doc.tag_ner(ner_tagger)              # запускаем выделение именованных сущностей

			for span in doc.spans:                           # добавляем сущности ORG, PER и LOC
				entities.append([span.type, span.text])      # добавляем сущности ORG, PER и LOC

			for date_match in dates_extractor(text):                    # добавляем сущности DATE
				start, stop = date_match.start, date_match.stop         # добавляем сущности DATE
				date_text = text[start:stop]                            # добавляем сущности DATE
				entities.append(['DATE', date_text])                    # добавляем сущности DATE

			for money_match in money_extractor(text):                    # добавляем сущности MONEY
				start, stop = money_match.start, money_match.stop        # добавляем сущности MONEY
				money_text = text[start:stop]                            # добавляем сущности MONEY
				entities.append(['MONEY', money_text])                   # добавляем сущности MONEY

	elif language == "en":              # если язык английский, то используем модель от spacy

		entities = []                   # массив всех сущностей

		nlp_en = spacy.load("F:\\For_school_or_university\\For_4_th_year\\For_final_graduation_work\\For_main_program\\tools\\for_en_NER\\en_core_web_sm-3.8.0\\en_core_web_sm\\en_core_web_sm-3.8.0")          # загружаем модель из локальной папки

		for number_of_group in range(0, len(pure_text), 3):                            # разделяем текст на небольшие группы     

			if len(pure_text) >= number_of_group + 3:                                  # получаем элементы текста, которые будут в одной группе
				group_of_text = pure_text[number_of_group: number_of_group + 3]        # получаем элементы текста, которые будут в одной группе
			else:                                                                      # получаем элементы текста, которые будут в одной группе
				group_of_text = pure_text[number_of_group: len(pure_text)]             # получаем элементы текста, которые будут в одной группе

			text = ' '.join(group_of_text)                                # обьединяем все элементы текста в одну строку

			doc = nlp_en(text)                                            # запускаем выделение именованных сущностей

			for entity in doc.ents:                                       # добавляем сущности ORG, PER, LOC, DATE и MONEY
				entities.append([entity.label_, entity.text])             # добавляем сущности ORG, PER, LOC, DATE и MONEY

	for entity in entities:            # проходимся по именованным сущностям
		entity_class = entity[0]       # выделяем тип именованной сущности
		entity_text = entity[1]        # выделяем саму именованную сущность

		if entity_class == "ORG":                                   # разделяем сущности по соответствующим массивам
			org_entities.append(entity_text)                        # разделяем сущности по соответствующим массивам
		elif entity_class == "LOC" or entity_class == "GPE":        # разделяем сущности по соответствующим массивам
			loc_entities.append(entity_text)                        # разделяем сущности по соответствующим массивам
		elif entity_class == "PER":                                 # разделяем сущности по соответствующим массивам
			per_entities.append(entity_text)                        # разделяем сущности по соответствующим массивам
		elif entity_class == "DATE" or entity_class == "TIME":      # разделяем сущности по соответствующим массивам
			date_entities.append(entity_text)                       # разделяем сущности по соответствующим массивам
		elif entity_class == "MONEY":                               # разделяем сущности по соответствующим массивам
			money_entities.append(entity_text)                      # разделяем сущности по соответствующим массивам

	with open("output_files\\" + str(output_dir) + "\\Entities_in_document.txt", 'w', encoding='utf-8') as f:   # создаем файл и выписываем найденные сущности в удобном виде
		
		f.write("===" * 50 + '\n')
		f.write('\n')
		f.write("Даты, содержащиеся внутри данного документа:\n")
		f.write('\n')
		for date_ent in date_entities:
			f.write(str(date_ent) + '\n')
		f.write('\n')

		f.write("===" * 50 + '\n')
		f.write('\n')
		f.write("Компании и организации, содержащиеся внутри данного документа:\n")
		f.write('\n')
		for org_ent in org_entities:
			f.write(str(org_ent) + '\n')
		f.write('\n')

		f.write("===" * 50 + '\n')
		f.write('\n')
		f.write("Локации, содержащиеся внутри данного документа:\n")
		f.write('\n')
		for loc_ent in loc_entities:
			f.write(str(loc_ent) + '\n')
		f.write('\n')

		f.write("===" * 50 + '\n')
		f.write('\n')
		f.write("Люди, содержащиеся внутри данного документа:\n")
		f.write('\n')
		for per_ent in per_entities:
			f.write(str(per_ent) + '\n')
		f.write('\n')

		f.write("===" * 50 + '\n')
		f.write('\n')
		f.write("Денежные единицы, содержащиеся внутри данного документа:\n")
		f.write('\n')
		for money_ent in money_entities:
			f.write(str(money_ent) + '\n')
		f.write('\n')




# Создаем краткое описание всего документа
def make_summary(all_in_ru_text, output_dir):

	summary_of_every_part = []                                            # краткое содержание каждой группы текста

	def token_length_function(text):                                      # функция вычисления длины в токенах
		return len(tokenizer.encode(text, add_special_tokens=False))

	MAX_SOURCE_TOKENS = 600        # максимальное количество токенов на входе модели
	MAX_TARGET_TOKENS = 200        # максимальное количество токенов в кратком содержании
	CHUNK_OVERLAP_TOKENS = 20      # количество токенов для перекрытия с предыдущим
	CHUNK_SIZE_TOKENS = 550        # количество токенов в каждом чанке
	DEVICE = 'cpu'                 # устройство, на котором проходят вычисления

	MODEL_CACHE_DIR = "F:\\For_school_or_university\\For_4_th_year\\For_final_graduation_work\\For_main_program\\tools\\for_summary"      # путь до модели суммаризации

	tokenizer = T5Tokenizer.from_pretrained(
		MODEL_CACHE_DIR,
		local_files_only=True
	)                                                         # загружаем токенизатор для модели суммаризации
	model = T5ForConditionalGeneration.from_pretrained(
		MODEL_CACHE_DIR,
		local_files_only=True
	).to(DEVICE)                                              # загружаем модель для создания краткого содержания

	our_LARGE_text = ' '.join(all_in_ru_text)                 # обьединяем весь текст в одну строку

	text_splitter = RecursiveCharacterTextSplitter(
		chunk_size=CHUNK_SIZE_TOKENS,
		chunk_overlap=CHUNK_OVERLAP_TOKENS,
		length_function=token_length_function,
		separators=[
			"\n\n",
			"\n",
			". ", "! ", "? ",
			"; ", ", ",
			" ",
			""
		],
		keep_separator=True
	)                                                        # определяем разделитель на чанки
	chunks = text_splitter.split_text(our_LARGE_text)        # разделяем весь текст на чанки

	for chunk in chunks:                           # проходимся по чанкам

		inputs = tokenizer(
			chunk,
			max_length=MAX_SOURCE_TOKENS,
			truncation=True,
			padding='max_length',
			return_tensors='pt'
		).to(DEVICE)                               # переносим чанк в токенизатор 

		with torch.no_grad():                      # отключаем вычисление градиента
			outputs = model.generate(
				input_ids=inputs["input_ids"],
				attention_mask=inputs["attention_mask"],
				max_length=MAX_TARGET_TOKENS,
				min_length=30,
				num_beams=5,
				no_repeat_ngram_size=4
			)                                     # переносим токены в модель

		summary = tokenizer.decode(outputs[0], skip_special_tokens=True)      # преобразуем в обычный текст
		summary_of_every_part.append(summary)                                 # добавляем краткое содержание в массив краткого содержания

	with open("output_files\\" + str(output_dir) + "\\Summary.txt", 'w', encoding='utf-8') as f:     # добавляем все краткое содержание в соответствующий документ
		f.write("Краткое содержание данного документа:\n")
		f.write("\n")
		f.write("===" * 50 + "\n")
		for part_of_summary in summary_of_every_part:
			f.write(str(part_of_summary) + '\n')
			f.write('\n')