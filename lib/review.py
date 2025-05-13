from __init__ import CONN, CURSOR

class Review:
    # Class-level dictionary to store all Review instances
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year  # Uses property setter for validation
        self.summary = summary  # Uses property setter for validation
        self.employee_id = employee_id  # Uses property setter for validation

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee ID: {self.employee_id}>"

    @classmethod
    def create_table(cls):
        """Create reviews table if it does not exist."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INT,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop reviews table if it exists."""
        sql = """
            DROP TABLE IF EXISTS reviews
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Persist the Review instance to the database and update its id."""
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """Create a new Review instance and save it to the database."""
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance from a database row, using cache if available."""
        review = cls.all.get(row[0])
        if review:
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3], row[0])
            cls.all[row[0]] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance corresponding to the database row with the given id."""
        sql = """
            SELECT * FROM reviews WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the corresponding database row with current instance attributes."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the corresponding database row and remove instance from cache."""
        sql = """
            DELETE FROM reviews WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list of Review instances for all rows in the reviews table."""
        sql = """
            SELECT * FROM reviews
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @property
    def year(self):
        """Return the year attribute."""
        return self._year

    @year.setter
    def year(self, value):
        """Validate and set the year attribute."""
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        if value < 2000:
            raise ValueError("Year must be >= 2000")
        self._year = value

    @property
    def summary(self):
        """Return the summary attribute."""
        return self._summary

    @summary.setter
    def summary(self, value):
        """Validate and set the summary attribute."""
        if not isinstance(value, str):
            raise ValueError("Summary must be a string")
        if len(value) == 0:
            raise ValueError("Summary must not be empty")
        self._summary = value

    @property
    def employee_id(self):
        """Return the employee_id attribute."""
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        """Validate and set the employee_id attribute."""
        from employee import Employee  # Avoid circular import
        if not isinstance(value, int):
            raise ValueError("Employee ID must be an integer")
        employee = Employee.find_by_id(value)
        if not employee:
            raise ValueError("Employee ID must correspond to an existing employee")
        self._employee_id = value