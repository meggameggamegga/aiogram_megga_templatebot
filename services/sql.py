import sqlite3



class DataBase:
    def __init__(self,db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

# ---------------------------------------------categories-------------------------------------------------------#
    def get_all_categories(self):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM categories''').fetchall()

    def get_category(self,cat_id):
        with self.connect:
            return self.cursor.execute('''SELECT name FROM categories WHERE id=?''',
                                       [cat_id])

    def edit_name_category(self,new_name,cat_id,name):
        with self.connect:
            return self.cursor.execute('''UPDATE categories SET name=(?) WHERE id=(?) AND name=(?)''',
                                       [new_name,cat_id,name])

    def edit_id_category(self, new_id, cat_id, name):
        with self.connect:
            return self.cursor.execute('''UPDATE categories SET id=(?) WHERE id=(?) AND name=(?)''',
                                       [new_id, cat_id, name])

    def delete_category(self,cat_id,name):
        with self.connect:
            return self.cursor.execute('''DELETE FROM categories WHERE id=(?) AND name=(?)''',
                                       [cat_id,name])

#---------------------------------------------products-------------------------------------------------------#
    def get_products(self,cat_id):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM products WHERE cat_id=(?)''',
                                       [cat_id]).fetchall()

    def get_product(self,cat_id,prod_id):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM products WHERE cat_id=(?) AND id=(?)''',
                                       [cat_id,prod_id]).fetchall()

    def delete_product(self,prod_id,cat_id):
        with self.connect:
            return self.cursor.execute('''DELETE FROM products WHERE id=(?) AND cat_id=(?)''',
                                       [prod_id,cat_id])

    def edit_product_name(self,prod_id,cat_id,new_name):
        with self.connect:
            return self.cursor.execute('''UPDATE products SET name=(?) WHERE id=(?) AND cat_id=(?)''',
                                       [new_name,prod_id,cat_id])

    def edit_product_price(self,prod_id,cat_id,new_price):
        with self.connect:
            return self.cursor.execute('''UPDATE products SET price=(?) WHERE id=(?) AND cat_id=(?)''',
                                       [new_price,prod_id,cat_id])

    def edit_product_id(self,prod_id,cat_id,new_id):
        with self.connect:
            return self.cursor.execute('''UPDATE products SET id=(?) WHERE id=(?) AND cat_id=(?)''',
                                       [new_id,prod_id,cat_id])

    def add_product(self,name,desc,price,cat_id):
        with self.connect:
            return self.cursor.execute('''INSERT INTO products(name,description,price,cat_id) VALUES(?,?,?,?) ''',
                                       [name,desc,price,cat_id])

#----------------------------------------------users_bakset-----------------------------------------------------#
    def add_user_product(self,user_id,prod_id,cat_id):
        with self.connect:
            return self.cursor.execute('''INSERT INTO users_basket(user_id,prod_id,cat_id) VALUES (?,?,?)''',
                                       [user_id,prod_id,cat_id])

    def get_user_basket(self,user_id):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM users_basket WHERE user_id=(?)''',
                                       [user_id]).fetchall()

    def check_basket_product(self,user_id,prod_id,cat_id):
        with self.connect:
            data = self.cursor.execute('''SELECT * FROM users_basket WHERE user_id=(?) AND prod_id=(?) AND cat_id=(?)''',
                                       [user_id,prod_id,cat_id]).fetchall()

            return True if data else False

    def delete_product_basket(self,user_id,prod_id,cat_id):
        with self.connect:
            return self.cursor.execute('''DELETE FROM users_basket WHERE user_id=(?) AND prod_id=(?) AND cat_id=(?)''',
                                       [user_id,prod_id,cat_id])

    def delete_basket_product(self,prod_id,cat_id):
        with self.connect:
            return self.cursor.execute('''DELETE FROM users_basket WHERE prod_id=(?) AND cat_id=(?)''',
                                       [prod_id,cat_id]).fetchall()
#---------------------------------------------------USERS------------------------------------------------------#
    #Есть ли в бд
    def user_exist(self,user_id):
        with self.connect:
            data = self.cursor.execute('''SELECT user FROM users WHERE user=(?)''',
                                       [user_id]).fetchall()
        return True if data else False


    #добавить в бд
    def add_user(self,user_id):
        with self.connect:
            return self.cursor.execute("""INSERT INTO users(user) VALUES (?)""",
                                       [user_id])
    #Вся информация по юзеру
    def get_info_user(self,user_id):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM users WHERE user=(?)''',
                                       [user_id]).fetchall()

