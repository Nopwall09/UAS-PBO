from conf.conf import create_connection, close_connection
class AdminModel:
    def __init__(self):
        self.connection = create_connection()
        self.cursor = self.connection.cursor(dictionary=True)

    def get_all_admins(self):
        query = "SELECT * FROM admins"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def get_admin_by_id(self, admin_id):
        query = "SELECT * FROM admins WHERE id = %s"
        self.cursor.execute(query, (admin_id,))
        result = self.cursor.fetchone()
        return result

    def create_admin(self, username, password):
        query = "INSERT INTO admins (username, password) VALUES (%s, %s)"
        self.cursor.execute(query, (username, password))
        self.connection.commit()
        return self.cursor.lastrowid

    def update_admin(self, admin_id, username, password):
        query = "UPDATE admins SET username = %s, password = %s WHERE id = %s"
        self.cursor.execute(query, (username, password, admin_id))
        self.connection.commit()
        return self.cursor.rowcount

    def delete_admin(self, admin_id):
        query = "DELETE FROM admins WHERE id = %s"
        self.cursor.execute(query, (admin_id,))
        self.connection.commit()
        return self.cursor.rowcount

    def __del__(self):
        close_connection(self.connection)