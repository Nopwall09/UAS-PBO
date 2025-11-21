from conf.conf import create_connection, close_connection
class DosenModel:
    def __init__(self):
        self.connection = create_connection()
        self.cursor = self.connection.cursor(dictionary=True)

    def get_all_dosen(self):
        query = "SELECT * FROM dosen"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def get_dosen_by_id(self, dosen_id):
        query = "SELECT * FROM dosen WHERE id = %s"
        self.cursor.execute(query, (dosen_id,))
        result = self.cursor.fetchone()
        return result

    def create_dosen(self, nama, nip, email, mata_kuliah):
        query = "INSERT INTO dosen (nama, nip, email, mata_kuliah) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (nama, nip, email, mata_kuliah))
        self.connection.commit()
        return self.cursor.lastrowid

    def update_dosen(self, dosen_id, nama, nip, email, mata_kuliah):
        query = "UPDATE dosen SET nama = %s, nip = %s, email = %s, mata_kuliah = %s WHERE id = %s"
        self.cursor.execute(query, (nama, nip, email, mata_kuliah, dosen_id))
        self.connection.commit()
        return self.cursor.rowcount

    def delete_dosen(self, dosen_id):
        query = "DELETE FROM dosen WHERE id = %s"
        self.cursor.execute(query, (dosen_id,))
        self.connection.commit()
        return self.cursor.rowcount

    def __del__(self):
        close_connection(self.connection)