from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import devart.oracle
import json
from htmlmin import minify
from function.function import clean_data_form, PersonalAuthentication, PersonalInfo, grants
from datetime import datetime

secret_key = 'Q0G5L-S45LX-KI634-FGLVB-78BMK'
name = 'Система обліку ключів'
var_grant_user = 'JURNALS'
var_grant_admin = 'JURNALS_ADMIN'

with open('config/config.json', 'r') as config_file:
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
    try:
        request_db = my_connection.cursor()
        #print('Підключення системи к БД успішне')
    except Exception as e:
        print('Помилка підключення системи к БД успішне')

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # Замените 'your_secret_key' на ваш секретный ключ

login_manager = LoginManager(app)

# Приклад моделі користувача (у реальному додатку дані мають зберігатися в базі даних)
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

########################## Сторінки ##########################
# Сторінка - Обробник помилки 404
@app.errorhandler(404)
def page_not_found(error):
    title = f'Помилка 404 - {name}'
    return render_template('404.html', title=title), 404

 # Сторінка - Головна

# Сторінка - Головна
@app.route('/', methods=['GET', 'POST'])
def index():
    
    active = request.args.get('active')

    if current_user.is_authenticated:
        message = ''
        title = f'Головна - {name}'
        PersonInfo = PersonalInfo(current_user.id)
        print(PersonInfo['username'])

        grant = grants(PersonInfo['username']);
        

        user_exists = any(item['granted_role'] == var_grant_user for item in grant) 
        grant_user = 1 if user_exists else 0

        admin_exists = any(item['granted_role'] == var_grant_admin for item in grant) 
        grant_admin = 1 if admin_exists else 0
        
        html_content = render_template('index.html', 
                                       message=message, 
                                       active=active,
                                       title=title, 
                                       tab_no=current_user.id, 
                                       familia=PersonInfo['familia'], 
                                       imya=PersonInfo['imya'], 
                                       otchestvo=PersonInfo['otchestvo'],
                                       grant_user=grant_user,
                                       grant_admin=grant_admin
                                       )
        minified_html = minify(html_content, remove_comments=True, remove_empty_space=True)
        return minified_html
    else:
        title = f'Вхід | {name}'
        html_content = render_template('index.html', title=title, tab_no=None)
        minified_html = minify(html_content, remove_comments=True, remove_empty_space=True)
        return minified_html

# Сторінка - Авторизації
@app.route('/login', methods=['POST', 'GET'])
def login():
    errors = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    try:
        user_connection = devart.oracle.connect(
            Direct = config_data['database_connections']['default']['direct'],
            Host = config_data['database_connections']['default']['db_host'],
            Port = config_data['database_connections']['default']['db_port'],
            SID = config_data['database_connections']['default']['sid'],
            UserName = username,
            Password = password,
            ConnectMode = config_data['database_connections']['default']['connectmode']
        )  
        request_user = user_connection.cursor()
        if request_user:
                
                user = User(PersonalAuthentication(username)['tab_no'])
                print(username)
                login_user(user)
                
                print('Підключення користувача к БД успішне')
                return redirect(url_for('index'))
            
    except Exception as e:
        print('Помилка підключення користувача к БД', e)
        errors = 'Невірні дані для входу'

    html_content = render_template('index.html', errors=errors)
    minified_html = minify(html_content, remove_comments=True, remove_empty_space=True)
    return minified_html

# Сторінка - Комутаційни центри
@app.route('/switching-centers', methods=['GET'])
def switchingcenters():
    if request.args.get('search'):   
        search = request.args.get('search')
    else:
        search = ''
    if current_user.is_authenticated:
        title = f'Комутаційни центри - {name}'
        PersonInfo = PersonalInfo(current_user.id)

        grant = grants(PersonInfo['username']);

        user_exists = any(item['granted_role'] == var_grant_user for item in grant) 
        grant_user = 1 if user_exists else 0

        admin_exists = any(item['granted_role'] == var_grant_admin for item in grant) 
        grant_admin = 1 if admin_exists else 0

        html_content = render_template('switching-centers.html', 
                                       title=title, 
                                       tab_no=current_user.id, 
                                       familia=PersonInfo['familia'], 
                                       imya=PersonInfo['imya'], 
                                       otchestvo=PersonInfo['otchestvo'],
                                       grant_user=grant_user,
                                       grant_admin=grant_admin,
                                       search=search
                                       )
        minified_html = minify(html_content, remove_comments=True, remove_empty_space=True, remove_all_empty_space=True, remove_optional_attribute_quotes=True )
        return minified_html

    else:
        title = f'Вхід | {name}'
        html_content = render_template('index.html', title=title, tab_no=None)
        minified_html = minify(html_content, remove_comments=True, remove_empty_space=True)
        return minified_html

# Сторінка - Адміністрування
@app.route('/administration', methods=['GET'])
def administration():
    if current_user.is_authenticated:
        title = f'Адміністрування - {name}'
        PersonInfo = PersonalInfo(current_user.id)

        grant = grants(PersonInfo['username']);

        user_exists = any(item['granted_role'] == var_grant_user for item in grant) 
        grant_user = 1 if user_exists else 0

        admin_exists = any(item['granted_role'] == var_grant_admin for item in grant) 
        grant_admin = 1 if admin_exists else 0

        html_content = render_template('administration.html', 
                                       title=title, 
                                       tab_no=current_user.id, 
                                       familia=PersonInfo['familia'], 
                                       imya=PersonInfo['imya'], 
                                       otchestvo=PersonInfo['otchestvo'],
                                       grant_user=grant_user,
                                       grant_admin=grant_admin
                                       )
        minified_html = minify(html_content, remove_comments=True, remove_empty_space=True, remove_all_empty_space=True, remove_optional_attribute_quotes=True )
        return minified_html

    else:
        title = f'Вхід | {name}'
        html_content = render_template('index.html', title=title, tab_no=None)
        minified_html = minify(html_content, remove_comments=True, remove_empty_space=True)
        return minified_html


########################## API ##########################
# Комутаційни центри - Список
@app.route('/api/v1/switching-centers', methods=['GET'])
def switchingcentersID():
    if request.args.get('search'):
        search = clean_data_form(request.args.get('search'))
    else:
        search = ''
    if request.args.get('page_number'):
        page_number = int(clean_data_form(request.args.get('page_number')))  # Convert to integer
    else:
        page_number = int(1)
    if request.args.get('number_lines'):
        number_lines = int(clean_data_form(request.args.get('number_lines')))  # Convert to integer
    else:
        number_lines = int(50)

    start_row = (page_number - 1) * number_lines + 1
    end_row = start_row + number_lines - 1
    #print(start_row, end_row)

    if search:
        searchSQL = f"AND (UPPER(t.name) LIKE UPPER('%{search}%') OR UPPER(t.room) LIKE UPPER('%{search}%')) "
    else: 
        searchSQL = ""

    try:
        centers = request_db.execute(f"""
                                     SELECT s.*
                                        FROM (
                                        select 
                                            t.id, t.name, t.room, ROWNUM AS rnum
                                        from 
                                            GRECK.RKSC_SWITCHING_CENTERS t 
                                        WHERE 
                                            t.active = '1' 
                                            {searchSQL}
                                        ORDER BY 
                                            t.name ASC 
                                        ) s
                                        WHERE rnum BETWEEN {start_row} AND {end_row} 
                                     """)
        centers_data = []
        for row_centers in centers.fetchall():
            center = {
                'id': row_centers[0],
                'name': row_centers[1],
                'room': row_centers[2]
            }
            centers_data.append(center)
    except Exception as e:
        centers_data = ''
    finally: 
        print("")

    return jsonify(centers_data) 

# Комутаційний центр - Карточка
@app.route('/api/v1/switching-centers/view/<id>', methods=['GET'])
def switchingcenterID(id):
    #key = request.args.get('key')
    try:
        centers = request_db.execute("select t.id, t.name, t.room from GRECK.RKSC_SWITCHING_CENTERS t WHERE t.active = '1' AND  t.id = '"+id+"' AND ROWNUM <= 1 ")
        centers_data = []
        for row_centers in centers.fetchall():
            center = {
                'id': row_centers[0],
                'name': row_centers[1],
                'room': row_centers[2]
            }
            centers_data.append(center)

    except Exception as e:
        centers_data = ''
    return jsonify(centers_data)

# Комутаційний центр - Видалити 
@app.route('/api/v1/switching-center/delete/<id>', methods=['GET'])
def deletecenterID(id):
    try:

        #параметризований запит
        query = """
            DELETE FROM GRECK.RKSC_SWITCHING_CENTERS WHERE ID = :id
        """
        RowDelete = request_db.execute(query, {'id': id})

        my_connection.commit()
        if RowDelete.rowcount > 0:
            return 'yes'
        else:
            return 'no'
    except Exception as e:
        print(e)
        return 'error'
    
# Комутаційний центр - Додати 
@app.route('/api/v1/switching-centers/add', methods=['GET'])
def addcenterID():
    name = clean_data_form(request.args.get('name'))
    room = clean_data_form(request.args.get('room'))
    try:
        def get_last_id():
            # Функція для отримання останнього ID
            query = "SELECT MAX(id) FROM GRECK.RKSC_SWITCHING_CENTERS"
            result = request_db.execute(query).fetchone()
            
            last_id = int(result[0]) + 1 if result and result[0] else 1
            
            return int(last_id)

        #RowAdd = request_db.execute(f"INSERT INTO GRECK.RKSC_SWITCHING_CENTERS (id, name, room, active) VALUES ('{get_last_id()}', '{name}', '{room}', '1') ")
        #параметризований запит
        query = """
            INSERT INTO GRECK.RKSC_SWITCHING_CENTERS (id, name, room, active)
            VALUES (:id, :name, :room, '1')
        """
        RowAdd = request_db.execute(query, {'id': get_last_id(), 'name': name, 'room': room})

        my_connection.commit()
        if RowAdd.rowcount > 0:
            return 'yes'
        else:
            return 'no'
    except Exception as e:
        return str(e)    
    
# Комутаційний центр - Редагувати 
@app.route('/api/v1/switching-centers/update', methods=['GET'])
def UpdatecenterID():
    id_center = int(request.args.get('id'))
    name = clean_data_form(request.args.get('name'))
    room = clean_data_form(request.args.get('room'))
    try:
        #параметризований запит 
        query = """
            UPDATE GRECK.RKSC_SWITCHING_CENTERS
            SET name = :name, room = :room
            WHERE id = :id
        """
        RowUpdate = request_db.execute(query, {'name': name, 'room': room, 'id': id_center})

        my_connection.commit()
        if RowUpdate.rowcount > 0:
            return 'yes'
        else:
            return 'no'
    except Exception as e:
        return str(e)

# Журнал заявок - Список
@app.route('/api/v1/journal-order', methods=['GET'])
def Journal():
    active = request.args.get('active')

    # Архів заявок
    if active == '-1':
        activeSQL = "AND t.date_start is not null AND t.date_end is not null"
    # Активні заявки
    else:
        activeSQL = "AND t.date_start is not null AND t.date_end is null"
    
    try:
        Journal = request_db.execute(f"""
                                        SELECT *
                                        FROM (
                                            SELECT 
                                                t.*,
                                                p.name AS name_center,
                                                q.FAMILIA,
                                                q.IMYA,
                                                q.OTCHESTVO,
                                                ROWNUM AS rnum
                                            FROM 
                                                GRECK.RKSC_SWITCHING_JOURNAL_ORDER t 
                                                INNER JOIN GRECK.RKSC_SWITCHING_CENTERS p ON p.id = t.centers 
                                                INNER JOIN kbs.personal q ON q.tab_no = t.personal_received
                                            WHERE 
                                                t.active = '1' 
                                                {activeSQL}
                                            ORDER BY 
                                                t.ID DESC
                                        )
                                        WHERE rnum BETWEEN 0 AND 50
                                     """)
        Journal_data = []
        for row_Journal in Journal.fetchall():
            data = {
                'id': int(row_Journal[0]),
                'name_center': row_Journal[8],
                'datestart': row_Journal[3],
                'dateend': row_Journal[4],
                'pib': f'{row_Journal[9]} {row_Journal[10]} {row_Journal[11]}'
            }
            Journal_data.append(data)
    except Exception as e:
        Journal_data = ''
    return jsonify(Journal_data) 

# Журнал заявок - Кому дозволено брати ключ
@app.route('/api/v1/staff-allowed-keys', methods=['GET'])
def StaffAlliwedKey():
    try:
        Staff = request_db.execute(f"""
                                        select 
                                            t.tab_no,
                                            q.FAMILIA,
                                            q.IMYA,
                                            q.OTCHESTVO
                                        from 
                                            GRECK.RKSC_SWITCHING_PERSONAL t 
                                            inner join kbs.personal q on q.tab_no = t.tab_no
                                        ORDER BY 
                                            q.FAMILIA ASC
                                     """)
        Staff_data = []
        for row_Staff in Staff.fetchall():
            data = {
                'tab_no': int(row_Staff[0]),
                'pib': row_Staff[1]+' '+row_Staff[2]+' '+row_Staff[3]
            }
            Staff_data.append(data)
    except Exception as e:
        Staff_data = ''
    return jsonify(Staff_data) 

# Журнал заявок - Додати 
@app.route('/api/v1/journal-order/add', methods=['GET'])
def AddjournalID():
    centers = request.args.get('centers')

    date_start = request.args.get('date_start')
    # Перетворюємо рядок в об'єкт datetime
    original_datetime = datetime.strptime(date_start, "%Y-%m-%dT%H:%M")
    # Форматуємо дату в новий формат
    new_date_string = original_datetime.strftime("%d.%m.%Y %H:%M")

    personal_received = request.args.get('personal_received')

    try:
        def get_last_id():
            # Функція для отримання останнього ID
            query = "SELECT MAX(id) FROM GRECK.RKSC_SWITCHING_JOURNAL_ORDER"
            result = request_db.execute(query).fetchone()
            
            last_id = int(result[0]) + 1 if result and result[0] else 1
            
            return int(last_id)
 
        #параметризований запит
        query = """
            INSERT INTO GRECK.RKSC_SWITCHING_JOURNAL_ORDER (id, centers, active, date_start, personal_issued, personal_received)
            VALUES (:id, :centers, '1', TO_DATE(:date_start, 'DD-MM-YYYY HH24:MI:SS'), :personal_issued, :personal_received)
        """

        RowAdd = request_db.execute(query, {'id': get_last_id(), 'centers': centers, 'date_start': new_date_string, 'personal_issued': current_user.id, 'personal_received': personal_received })

        my_connection.commit()
        if RowAdd.rowcount > 0:
            return 'yes'
        else:
            return 'no'
    except Exception as e:
        return str(e)  

# Журнал заявок - Редагувати 
@app.route('/api/v1/journal-order/edit', methods=['GET'])
def EditjournalID():
    id = request.args.get('id')

    date_end = request.args.get('date_end')
    # Перетворюємо рядок в об'єкт datetime
    original_datetime_end = datetime.strptime(date_end, "%Y-%m-%dT%H:%M")
    # Форматуємо дату в новий формат
    new_date_string_end = original_datetime_end.strftime("%d.%m.%Y %H:%M:%S")

    print(date_end)
    print(new_date_string_end)

    try:
        #параметризований запит 
        query = """
            UPDATE GRECK.RKSC_SWITCHING_JOURNAL_ORDER SET date_end = TO_DATE(:date_end, 'DD-MM-YYYY HH24:MI:SS') WHERE id = :id
        """
        RowUpdate = request_db.execute(query, {'date_end': new_date_string_end, 'id': id})

        my_connection.commit()
        if RowUpdate.rowcount > 0:
            return 'yes'
        else:
            return 'no'
    except Exception as e:
        return str(e) 


# Вихід
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='172.16.2.49', port=8080)

