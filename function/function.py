import re
import json
from flask import request
from datetime import datetime
import devart.oracle


with open('./config/config.json', 'r') as config_file:
    config_data = json.load(config_file)
    my_connection = devart.oracle.connect(
        Direct = config_data['database_connections']['default']['direct'],
        Host = config_data['database_connections']['default']['db_host'],
        Port = config_data['database_connections']['default']['db_port'],
        SID = config_data['database_connections']['default']['sid'],
        UserName = config_data['database_connections']['default']['db_user'],
        Password = config_data['database_connections']['default']['db_password'],
        ConnectMode = config_data['database_connections']['default']['connectmode']
    ) 
request = my_connection.cursor()

# Отобразить список грантов пользователя
def grants(username):
    try:
        centers = request.execute(f"SELECT p.* FROM dba_role_privs p WHERE p.grantee = '{username}' ")
        centers_data = []
        for row_centers in centers.fetchall():
            center = {
                'username': row_centers[0],
                'granted_role': row_centers[1]
            }
            centers_data.append(center)
    except Exception as e:
        centers_data = ''
    return (centers_data) 

# Дані користувача під час авторизації
def PersonalAuthentication(username):
    if username:
        Personal = request.execute(f"""
                                    select 
                                        b.username,
                                        b.tab_no
                                    from 
                                        sys.dba_users a, base_obj.user_workplace b
                                    where 
                                        UPPER(a.username) = UPPER('{username}')
                                        AND TRIM(UPPER(a.username)) = TRIM(UPPER(b.username))
                                        AND rownum <= 1
                                    """)
        for row_Personal in Personal.fetchall():
            data = {
                'username': row_Personal[0],
                'tab_no': row_Personal[1]
            }
    else:
        data = ''
        print('Користувач не знайден в таблиці sys.dba_users або base_obj.user_workplace')
    return data

# Інформація користувача
def PersonalInfo(tab_no):
    if tab_no:
        Personal = request.execute(f"""
                                    select 
                                        s.tab_no,
                                        s.tseh_short,
                                        s.familia,
                                        s.imya,
                                        s.otchestvo,
                                        b.username
                                    from 
                                        kbs.personal s
                                        INNER JOIN base_obj.user_workplace b ON b.tab_no = s.tab_no
                                    where
                                        s.tab_no = '{tab_no}'
                                        AND rownum <= 1
                                    """)
        for row_Personal in Personal.fetchall():
            data = {
                'tab_no': row_Personal[0],
                'tseh_short': row_Personal[1],
                'familia': row_Personal[2],
                'imya': row_Personal[3],
                'otchestvo': row_Personal[4],
                'username': row_Personal[5]
            }
    else:
        data = ''
    return data

# Удалить все символы
def clean_data_form(data):
    # Удалить все символы, кроме латиницы, кирилицы и цифр для форм
    data = re.sub(r'[^A-Za-zА-Яа-я0-9/#-№ ]', '', data)
    # Удалить лишние пробелы
    data = re.sub(r'\s{2,}', ' ', data)
    # Удалить пробелы в начале и конце строки
    data = data.strip()
    return data

# Функція видалення зайвих символів
def clean_data(data):
    data = re.sub(r'[^а-яА-Яa-zA-Z\s.іїІЇЄє]', '', data)
    data = re.sub(r'\s{2,}', ' ', data)
    data = data.strip()
    data = normalize_names([data])[0]
    return data

# Функція формування ПІБ
def normalize_names(names):
    normalized_names = []
    for name in names:
        parts = re.split(r'\s', name)

        if len(parts) == 3:
            # Якщо ім'я, прізвище та по батькові
            first_name = parts[0]
            middle_name = parts[1][0] + "."
            last_name = parts[2][0] + "."
            normalized_name = f"{first_name} {middle_name} {last_name}"
        elif len(parts) == 2:
            # Якщо тільки ім'я та прізвище
            first_name = parts[0]
            last_name = parts[1][0] + "."
            normalized_name = f"{first_name} {last_name}"
        else:
            # Якщо формат несподіваний, залишити як є
            normalized_name = name

        normalized_names.append(normalized_name)

    return normalized_names

# Функція пошуку номера докумета в АСКВД
def askid_doc_id(doc_date, doc_no, priznak):
    try:
        if not doc_date or not doc_no or not priznak:
            return None

        req_aski_doc_id = request.execute(f"SELECT df.get_doc_id_for_pswc('{doc_date}', {doc_no}, {priznak}) AS aski_doc_id FROM dual")
        doc_id = req_aski_doc_id.fetchone()

        if doc_id and doc_id[0] is not None and doc_id[0] != '-1' and doc_id[0] > 0:
            return int(doc_id[0])
        else:
            return None

    except Exception as e:
        print(f"Помилка askid_doc_id: {e}")
        return None
            
# Функція запису в Логи привілеїв і ролей           
def ca_change_priv_log(family, role, current_datetime, doc_no, doc_date_str, dept_short, actions, author, aski_doc_id):
    insert_query = "INSERT INTO pswc.ca_change_priv_log (UNAME, RNAME, DATE_ACTION, DOC_NO, DOC_DATE, DEPT_SHORT, OPERATION, AUTHOR, ASKI_DOC_ID ) VALUES (:family, :actions, :date_action, :doc_no, :doc_date, :dept_short, :operation, :author, :aski_doc_id)"
    insert = request.execute(insert_query, (family, role, current_datetime, doc_no, doc_date_str, dept_short, actions, author, aski_doc_id))
    return insert

# Оновлення матв'ю ролей користувачам
def user_all_role_mv():
    try:                
        refreshmv = "begin sys.dbms_snapshot.refresh('cmo.user_all_role_mv'); end;"
        request.execute(refreshmv)
        print('Матв`ю успішно оновлено')
        return('Матв`ю успішно оновлено')
    except Exception as e:
        print(f"Помилка refreshmv : {e}")
        return None

# Додавання або видалення ролей за списком користувачів
def mass_grant_and_revoke(doc_no, priznak, doc_date, dept_short, author, actions, role):
    try:
        doc_date_str = datetime.strptime(doc_date, "%d.%m.%Y")

        # Получение текущей даты и времени
        current_datetime = datetime.now()
        # Форматирование даты в требуемый формат
        date_action = current_datetime.strftime("%d.%m.%Y %H:%M:%S")

        with open('personal.txt', 'r', encoding='UTF-8') as file:
            # Читаємо рядки з файлу і створюємо масив прізвищ
            families = file.read().splitlines()
            print("Количество строк в файле:", len(families))

            aski_doc_id = askid_doc_id(doc_date, doc_no, priznak)

            if aski_doc_id:
                for family in families:
                    if family:
                        family = ''.join(clean_data(family))

                        user_found = False
                        roles_found = False

                        users = request.execute("SELECT b.tab_no, r.sprdepartment_id, b.username FROM sys.dba_users q, base_obj.user_workplace b, kbs.personal r "
                                        " WHERE UPPER(b.username) LIKE UPPER('%"+family+"%') "
                                        " and q.username = b.username and b.tab_no = r.tab_no "
                                        " order by q.user_id desc;")
                        
                        for row in users.fetchall():
                            if row[0]:
                                roles_query = "SELECT p.* FROM dba_role_privs p WHERE p.grantee LIKE '%' || :family || '%' AND TRIM(UPPER(p.granted_role)) = TRIM(UPPER(:role))"
                                roles = request.execute(roles_query, (family, role))
                                for rowroles in roles.fetchall():
                                    if rowroles[0]:
                                        roles_found = True
                                    else:
                                        roles_found = False
                                user_found = True
                            else:
                                user_found = False
                                
                        if not user_found:
                            print('❗️', family, '=>' ,'Користувач не знайден в базе данных' )
                        else:
                            if not roles_found:
                                if actions == 'GRANT':
                                    try:
                                        grant_statement = f'{actions} {role} TO "{family}"'
                                        request.execute(grant_statement)
                                        my_connection.commit()

                                        # Запис у Логі
                                        ca_change_priv_log(family, role, current_datetime, doc_no, doc_date_str, dept_short, actions, author, aski_doc_id)

                                        print(family, ' => ', 'Операція додавання виконана успішно')
                                    except Exception as e:
                                        print('❗️', f"Помилка: {e}")

                                elif actions == 'REVOKE':
                                    print(family, ' => ', 'Грант вже видалений у користувача')
                            else:
                                if actions == 'REVOKE':
                                    try:
                                        grant_statement = f'{actions} {role} FROM "{family}"'
                                        request.execute(grant_statement)
                                        my_connection.commit()

                                        # Запис у Логі
                                        ca_change_priv_log(family, role, current_datetime, '', '', '', actions, author, '')

                                        print(family, ' => ', 'Операція видалення виконана успішно')
                                    except Exception as e:
                                        print('❗️', f"Помилка: {e}")
                                elif actions == 'GRANT':
                                    print(family, ' => ', 'Грант вже видан користувачу')
                
                # Оновити матв'ю
                user_all_role_mv()
                
            else:
                print('Документ в АСКВД не знайдено')

    
    except Exception as e:
        print(f"Помилка db : {e}")
        return None


doc_no = int(126)
priznak = int(1)
doc_date = "08.01.2024"
dept_short = 'СВНіПБ'
author = 'Батрак А. О.'
#actions = 'REVOKE'
actions = 'GRANT'
role = 'FX_ADMIN'
#mass_grant_and_revoke(doc_no, priznak, doc_date, dept_short, author, actions, role)
