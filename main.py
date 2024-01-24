import win32com.client

def connect_to_1c():
    try:
        com_connector = win32com.client.Dispatch("V83.COMConnector")
        conn_string = "File='\\\\DESKTOP-EF5I8R5\\InfoBase';Usr='Администратор';Pwd='12345';"
        connection = com_connector.Connect(conn_string)
        return connection
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None

def get_nomenclature(connection):
    if connection is not None:
        try:
            query = connection.NewObject("Query")
            query.Text = """
                ВЫБРАТЬ РАЗРЕШЕННЫЕ
                	ОстаткиТоваров.Номенклатура КАК Номенклатура,
                	СУММА(ОстаткиТоваров.Количество) КАК Количество,
                	СУММА(ОстаткиТоваров.Резерв) КАК Резерв
                ПОМЕСТИТЬ ОстаткиТоваров
                ИЗ
                	РегистрСведений.ОстаткиТоваров КАК ОстаткиТоваров
                СГРУППИРОВАТЬ ПО
                	ОстаткиТоваров.Номенклатура
                ;

                ВЫБРАТЬ
                    СправочникНоменклатура.Наименование КАК name,
                    СправочникНоменклатура.Артикул КАК article,
                    СправочникНоменклатура.Ячейка КАК box,
                    Цены.Цена КАК price,
                    ОстаткиТоваров.Количество КАК quantity
                ИЗ
                    Справочник.Номенклатура КАК СправочникНоменклатура
                    ЛЕВОЕ СОЕДИНЕНИЕ РегистрСведений.ЦеныНоменклатуры.СрезПоследних() КАК Цены
                    ПО Цены.Номенклатура = СправочникНоменклатура.Ссылка
                    ЛЕВОЕ СОЕДИНЕНИЕ ОстаткиТоваров
                    ПО ОстаткиТоваров.Номенклатура = СправочникНоменклатура.Ссылка
            """

            query.SetParameter("ВидЦен", "Оптова ціна")
            result = query.Execute().Choose()
            while result.Next():
                # print(dir(result.Ячейка))
                # uuid = result.Ссылка
                print([result.name, result.article, result.box.Description, result.price, result.quantity])
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")

def main():
    connection = connect_to_1c()
    get_nomenclature(connection)

if __name__ == "__main__":
    main()
