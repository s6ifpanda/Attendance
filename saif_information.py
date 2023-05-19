import sqlite3

Connection = sqlite3.connect('attendance.db')
Cursor = Connection.cursor()

# Create the Users table to store admirals, co-admirals, and teachers
Cursor.execute('''CREATE TABLE Users (
                User_id INTEGER PRIMARY KEY AUTOINCREMENT,
                User_name TEXT NOT NULL,
                User_email TEXT NOT NULL,
                User_username TEXT NOT NULL,
                User_password TEXT NOT NULL,
                User_dob DATE NOT NULL,
                User_authority VARCHAR(50) NOT NULL,
                User_rank INTEGER NOT NULL
            )''')

# Create the Stages table to store information about the 4 stages
Cursor.execute('''CREATE TABLE Stages (
                Stage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                Stage_description TEXT NOT NULL
            )''')

# Create the Lectures table to store information about the lectures
Cursor.execute('''CREATE TABLE Lectures (
                Lecture_id INTEGER PRIMARY KEY AUTOINCREMENT,
                Lecture_name VARCHAR(50) NOT NULL,
                Course_name VARCHAR(50) NOT NULL,
                Duration FLOAT NOT NULL,
                Lecture_Weeks INTEGER NOT NULL,
                Stage_id INTEGER NOT NULL,
                User_id INTEGER NOT NULL,
                User_assistant_id INTEGER,
                Is_LAB BOOLEAN DEFAULT 0,
                Association_Link VARCHAR(50),
                FOREIGN KEY (Stage_id) REFERENCES Stages(Stage_id),
                FOREIGN KEY (User_id) REFERENCES Users(User_id)
            )''')


# Create the Students table to store information about the students
Cursor.execute('''CREATE TABLE Students (
                Student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                Student_qr_code_id INTEGER NOT NULL,
                Student_name TEXT NOT NULL,
                Student_email TEXT NOT NULL,
                Stage_id INTEGER NOT NULL,
                FOREIGN KEY (Stage_id) REFERENCES Stages(Stage_id)
            )''')

# Create the Attendance table to store the attendance information
Cursor.execute('''CREATE TABLE Attendance (
                Attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                Student_id INTEGER NOT NULL,
                Student_name TEXT NOT NULL,
                Student_email TEXT NOT NULL,
                Student_qr_code_id INTEGER NOT NULL,
                Stage_id INTEGER NOT NULL,
                Stage_description TEXT NOT NULL,
                Lecture_id INTEGER NOT NULL,
                Lecture_name VARCHAR(50) NOT NULL,
                Lecture_week INTEGER NOT NULL,
                State VARCHAR(20) NOT NULL DEFAULT 'Absent',
                Record_Date DATE NOT NULL,
                FOREIGN KEY (Student_id) REFERENCES Students(Student_id),
                FOREIGN KEY (Lecture_id) REFERENCES Lectures(Lecture_id),
                FOREIGN KEY (Stage_id) REFERENCES Stages(Stage_id)
            )''')



# Data Entry

# Inserting data into the Users table
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Dr. Reem Razzaq', 'admiral@gmail.com', 'ism_admiral', '111', '1970-01-01', 'ISM Admiral', 1)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('A.A. Ahmed Sami', 'co_admiral@gmail.com', 'ism_co_admiral', '222', '1970-01-01', 'ISM Co-Admiral', 2)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Muthana Jabbar', 'muthana.jabbar@gmail.com', 'muthana.jabbar', '333', '1975-01-01', 'ISM Teacher', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Ali Nafaa', 'ali.nafaa@gmail.com', 'ali.nafaa', '333', '1980-01-01', 'ISM Teacher', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Ali Munther', 'ali.munther@gmail.com', 'ali.munther', '333', '1990-01-01', 'ISM Teacher', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Mustafa Nafaa', 'mustafa.nafaa@gmail.com', 'mustafa.nafaa', '333', '1992-01-01', 'ISM Lecturer', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Dr. Ban', 'dr.ban@gmail.com', 'dr.ban', '333', '1970-01-01', 'ISM Professor', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Dr. Mahdi Nassif', 'dr.mahdi@gmail.com', 'dr.mahdi', '333', '1960-01-01', 'ISM Professor', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Dr. Reem Razzaq', 'admiral@gmail.com', 'dr.reem', '333', '1970-01-01', 'ISM Professor', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Dr. Raja Kadim', 'raja.kadim@gmail.com', 'dr.raja', '333', '1970-01-01', 'ISM Professor', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Weam Saadi', 'weam.saadi@gmail.com', 'weam.saadi', '333', '1990-01-01', 'ISM Teacher', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Tahera', 'tahera@gmail.com', 'tahera', '333', '1980-01-01', 'ISM Teacher', 3)")
Cursor.execute(
    "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) VALUES ('Dr. Haitham', 'dr.haitham@gmail.com', 'dr.haitham', '333', '19850-01-01', 'ISM Professor', 3)")

# Inserting data into the Stages table
Cursor.execute("INSERT INTO Stages (Stage_description) VALUES ('1st Stage')")
Cursor.execute("INSERT INTO Stages (Stage_description) VALUES ('2nd Stage')")
Cursor.execute("INSERT INTO Stages (Stage_description) VALUES ('3rd Stage')")
Cursor.execute("INSERT INTO Stages (Stage_description) VALUES ('4th Stage')")

# Inserting data into the Lectures table
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Cloud Computing LAB', 'Course 1', 1.5, 15, 4, 3, 5, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Cloud Computing LAB (B)', 'Course 1', 1.5, 15, 4, 3, 5, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Cloud Computing LAB (C)', 'Course 1', 1.5, 15, 4, 3, 5, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('IS Project Management LAB', 'Course 1', 1.5, 15, 4, 5, 4, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('IS Project Management LAB (B)', 'Course 1', 1.5, 15, 4, 5, 4, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('IS Project Management LAB (C)', 'Course 1', 1.5, 15, 4, 5, 4, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('IT Security and Risk Management LAB', 'Course 1', 1.5, 15, 4, 5, 3, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('IT Security and Risk Management LAB (B)', 'Course 1', 1.5, 15, 4, 5, 3, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('IT Security and Risk Management LAB (C)', 'Course 1', 1.5, 15, 4, 5, 3, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Social Media Networks and the Society LAB', 'Course 1', 1.5, 15, 4, 6, 5, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Social Media Networks and the Society LAB (B)', 'Course 1', 1.5, 15, 4, 6, 3, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Social Media Networks and the Society LAB (C)', 'Course 1', 1.5, 15, 4, 6, 3, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('IS Project Management', 'Course 1', 2.0, 15, 4, 7, 3, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Cloud Computing', 'Course 1', 3.0, 15, 4, 8, 3, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Decision Support System', 'Course 1', 3.0, 15, 4, 9, 3, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('IT Security and Risk Management', 'Course 1', 2.0, 15, 4, 10, 8, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Social Media Networks and the Society', 'Course 1', 2.0, 15, 4, 10, 8, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('English IV', 'Course 1', 2.0, 15, 4, 11, 10, 0)")
Cursor.execute(
    "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_Weeks, Stage_id, User_id, User_assistant_id, Is_LAB) VALUES ('Project I', 'Course 1', 2.0, 15, 4, 12, 8, 0)")



Connection.commit()
Connection.close()
