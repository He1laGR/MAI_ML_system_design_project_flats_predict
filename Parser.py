import cianparser
import time

#Этот файл используется для парсинга объявлений, но его нужно самостоятельно перезапускать т.к. ловится ошибка 429

#Инициализируем локацию
spb_parser = cianparser.CianParser(location="Санкт-Петербург")
rooms = 5
start_page = 36
end_page = 1
for i in range(30):
    data = spb_parser.get_flats(deal_type="sale", rooms=rooms, with_extra_data=True, with_saving_csv=True, additional_settings={"start_page" : start_page, "sort by" : "creation_data_from_newer_to_older"})
    start_page += 1
    end_page += 1
    time.sleep(10)
    continue
