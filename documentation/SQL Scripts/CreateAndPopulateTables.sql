-- Drops all tables
DROP TABLE if exists OfficeHourQuestionTopic;
DROP TABLE if exists OfficeHourQuestion;
DROP TABLE if exists OfficeHourSession;
DROP TABLE if exists AssignmentTopic;
DROP TABLE if exists Assignment;
DROP TABLE if exists CourseTopic;
DROP TABLE if exists Registration;
DROP TABLE if exists Class;
DROP TABLE if exists Course;
DROP TABLE if exists Location;
DROP TABLE if exists Semester;
DROP TABLE if exists Professor;
DROP TABLE if exists TeachingAssistant;
DROP TABLE if exists Instructor;
DROP TABLE if exists Student;
DROP TABLE if exists UniversityMember;



-- Creates all tables
CREATE TABLE UniversityMember (
    UnivMem_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    UnivMem_FirstName TEXT NOT NULL,
    UnivMem_LastName TEXT NOT NULL,
    UnivMem_CompID TEXT UNIQUE NOT NULL
        CHECK (length(UnivMem_CompID) <= 8),
    UnivMem_IsStudent BOOLEAN NOT NULL,
    UnivMem_IsInstructor BOOLEAN NOT NULL
);

CREATE TABLE Student (
    UnivMem_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT 
        REFERENCES UniversityMember(UnivMem_ID) ON DELETE CASCADE
);

CREATE TABLE Instructor (
    UnivMem_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT 
        REFERENCES UniversityMember(UnivMem_ID) ON DELETE CASCADE,
    Instructor_Type TEXT NOT NULL
        CHECK (Instructor_Type in ('TA', 'PROF'))
);

CREATE TABLE Professor (
    UnivMem_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT
        REFERENCES Instructor(UnivMem_ID) ON DELETE CASCADE
);

CREATE TABLE TeachingAssistant (
    UnivMem_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT
        REFERENCES Instructor(UnivMem_ID) ON DELETE CASCADE
);

CREATE TABLE Semester (
    Sem_ID INTEGER NOT NULL
        PRIMARY KEY AUTOINCREMENT,
    Sem_Name TEXT NOT NULL
	CHECK (Sem_Name IN ('SPRING', 'SUMMER', 'FALL')),
    Sem_Year DATE NOT NULL
	CHECK (Sem_Year >= 1900)
);

CREATE TABLE Location (
    Loc_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    Loc_Name TEXT UNIQUE NOT NULL
);

CREATE TABLE Course (
    Crs_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    Crs_Subject TEXT NOT NULL CHECK (length(Crs_Subject) <= 4),
    Crs_CatalogNumber TEXT NOT NULL
        CHECK (Crs_CatalogNumber >= 0 and Crs_CatalogNumber <= 9999),
    UNIQUE(Crs_Subject, Crs_CatalogNumber) ON CONFLICT ABORT
);

CREATE TABLE CourseTopic (
    CrsTopic_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    Crs_ID INTEGER NOT NULL 
        REFERENCES Course(Crs_ID) ON DELETE CASCADE,
    CrsTopic_Name TEXT NOT NULL,
    UNIQUE(Crs_ID, CrsTopic_Name) ON CONFLICT ABORT
);

CREATE TABLE Class (
    Class_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    Crs_ID INTEGER NOT NULL 
        REFERENCES Course(Crs_ID) ON DELETE CASCADE,
    Sem_ID INTEGER NOT NULL 
        REFERENCES Semester(Sem_ID) ON DELETE CASCADE,
        UNIQUE (Crs_ID, Sem_ID) ON CONFLICT ABORT
);

CREATE TABLE Registration (
    Reg_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    Class_ID INTEGER NOT NULL 
        REFERENCES Class(Class_ID) ON DELETE CASCADE,
    UnivMem_ID INTEGER NOT NULL 
        REFERENCES UniversityMember(UnivMem_ID) ON DELETE CASCADE,
    Reg_Type TEXT NOT NULL
        CHECK (Reg_Type in ('TA', 'STUD', 'PROF')),
        UNIQUE (Class_ID, UnivMem_ID) ON CONFLICT ABORT
);

CREATE TABLE Assignment (
    Assign_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    Class_ID INTEGER NOT NULL 
        REFERENCES Class(Class_ID) ON DELETE CASCADE,
    Assign_Name TEXT NOT NULL,
        UNIQUE (Class_ID, Assign_Name) ON CONFLICT ABORT
);

CREATE TABLE AssignmentTopic (
    AssignTopic_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    Assign_ID INTEGER NOT NULL 
        REFERENCES Assignment(Assign_ID) ON DELETE CASCADE,
    CrsTopic_ID INTEGER NOT NULL 
        REFERENCES CourseTopic(CrsTopic_ID) ON DELETE CASCADE,
    UNIQUE (Assign_ID, CrsTopic_ID) ON CONFLICT ABORT
);

CREATE TABLE OfficeHourSession (
    OHS_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    Class_ID INTEGER NOT NULL 
        REFERENCES Class(Class_ID) ON DELETE CASCADE,
    UnivMem_ID INTEGER NOT NULL 
        REFERENCES Instructor(UnivMem_ID) ON DELETE CASCADE,
    Loc_ID INTEGER NOT NULL 
        REFERENCES Location(Loc_ID) ON DELETE CASCADE,
    OHS_StartDateTime DATE NOT NULL,
    OHS_EndDateTime DATE NOT NULL,
    OHS_Status TEXT NOT NULL,
        CHECK (OHS_EndDateTime > OHS_StartDateTime)
);

CREATE TABLE OfficeHourQuestion (
    OHQ_ID INTEGER NOT NULL 
        PRIMARY KEY AUTOINCREMENT,
    OHS_ID INTEGER NOT NULL 
        REFERENCES OfficeHourSession(OHS_ID) ON DELETE CASCADE,
    Assign_ID INTEGER 
        REFERENCES Assignment(Assign_ID) ON DELETE CASCADE,
    UnivMem_ID INTEGER NOT NULL
        REFERENCES Student(UnivMem_ID) ON DELETE CASCADE,
    OHQ_Status TEXT NOT NULL,
    OHQ_StudentComment TEXT NOT NULL,
    OHQ_InstructorComment TEXT NOT NULL,
    OHQ_OpenedAt DATE NOT NULL,
    OHQ_ClosedAt DATE
);

CREATE TABLE OfficeHourQuestionTopic (
    OHQT_ID INTEGER NOT NULL
        PRIMARY KEY AUTOINCREMENT,
    OHQ_ID INTEGER NOT NULL 
        REFERENCES OfficeHourQuestion(OHQ_ID),
    CrsTopic_ID INTEGER NOT NULL 
        REFERENCES CourseTopic(CrsTopic_ID),
        UNIQUE (OHQ_ID, CrsTopic_ID) ON CONFLICT ABORT
);



-- Creates triggers
CREATE TRIGGER IF NOT EXISTS VerifyInstructorOnOHSInsert
    BEFORE INSERT ON OfficeHourSession 
    WHEN NOT EXISTS(
        SELECT 1 FROM Registration R 
            WHERE R.UnivMem_ID=NEW.UnivMem_ID 
                AND R.Reg_Type in ('PROF', 'TA') 
                AND R.Class_ID=NEW.Class_ID
    )
    BEGIN
        SELECT RAISE(ABORT, 'Error the UniversityMember must be registered as either a professor or a TA in that class to hold office hours.');
    END;
    
CREATE TRIGGER IF NOT EXISTS VerifyInstructorOnOHSUpdate
    BEFORE UPDATE ON OfficeHourSession 
    WHEN NOT EXISTS(
        SELECT 1 FROM Registration R 
            WHERE R.UnivMem_ID=NEW.UnivMem_ID 
                AND R.Reg_Type in ('PROF', 'TA') 
                AND R.Class_ID=NEW.Class_ID
    )
    BEGIN
        SELECT RAISE(ABORT, 'Error the UniversityMember must be registered as either a professor or a TA in that class to hold office hours.');
    END;
    

CREATE TRIGGER IF NOT EXISTS VerifyStudentOnOHQUpdate
    BEFORE UPDATE ON OfficeHourQuestion 
    WHEN NOT EXISTS(
        SELECT 1 FROM Registration R
            JOIN OfficeHourSession OHS ON OHS.OHS_ID = NEW.OHS_ID
            WHERE R.UnivMem_ID=NEW.UnivMem_ID 
                AND R.Reg_Type == 'STUD' 
                AND R.Class_ID=OHS.Class_ID
    )
    BEGIN
        SELECT RAISE(ABORT, 'Error the UniversityMember must be registered as a student in that class to ask a question.');
    END;
    
CREATE TRIGGER IF NOT EXISTS VerifyStudentOnOHQInsert
    BEFORE INSERT ON OfficeHourQuestion 
    WHEN NOT EXISTS(
        SELECT 1 FROM Registration R
            JOIN OfficeHourSession OHS ON OHS.OHS_ID = NEW.OHS_ID
            WHERE R.UnivMem_ID=NEW.UnivMem_ID 
                AND R.Reg_Type == 'STUD' 
                AND R.Class_ID=OHS.Class_ID
    )
    BEGIN
        SELECT RAISE(ABORT, 'Error the UniversityMember must be registered as a student in that class to ask a question.');
    END;
    


-- Populates all tables

--University Member:
INSERT INTO UniversityMember (
    UnivMem_FirstName, 
    UnivMem_LastName, 
    UnivMem_CompID, 
    UnivMem_IsStudent, 
    UnivMem_IsInstructor
) VALUES
    ('Jonah', 'Kim', 'crd3vm', TRUE, TRUE),
    ('Yuxi', 'Yang', 'yy6znb', TRUE, FALSE),
    ('Tammy', 'Ngo', 'bsy6pq', TRUE, FALSE),
    ('Mary', 'Smith', 'mls4aa', FALSE, TRUE),
    ('Ishan', 'Mathur', 'anm3hh', FALSE, TRUE),
    ('John', 'Doe', 'aaa1aa', TRUE, TRUE),
    ('Jane', 'Doe', 'jnd6a', TRUE, FALSE),
    ('Richard', 'Ngyuen', 'rcng1', FALSE, TRUE),
    ('William', 'McBurney', 'wb288', FALSE, TRUE);


--Student:
INSERT INTO Student 
    (UnivMem_ID) 
    VALUES (1), (2), (3), (6), (7);
    
--Instructor:
INSERT INTO Instructor 
    (UnivMem_ID, Instructor_Type)
    VALUES 
        (1, 'TA'),
        (4, 'PROF'),
        (5, 'TA'),
        (6, 'PROF'),
        (8, 'PROF'),
        (9, 'PROF');
    
--Professor:
INSERT INTO Professor 
    (UnivMem_ID) 
    VALUES 
        (4), 
        (6),
        (8),
        (9);

--TeachingAssistant:
INSERT INTO TeachingAssistant 
    (UnivMem_ID) 
    VALUES 
        (1), 
        (5);

--Semester:
INSERT INTO Semester
    (Sem_Name, Sem_Year)
    VALUES 
        ('SPRING', 2023), 
        ('SUMMER', 2023), 
        ('FALL', 2023);

--Location:
INSERT INTO Location 
    (Loc_Name) 
    VALUES 
        ('Online'), 
        ('Rice 130'), 
        ('Thornton Stacks');
        
--Course:
INSERT INTO Course
    (Crs_Subject, Crs_CatalogNumber)
    VALUES 
        ('CS', '3140'), 
        ('APMA', '3100'), 
        ('CS', '4750');
    
--CourseTopic:
INSERT INTO CourseTopic
    (Crs_ID, CrsTopic_Name)
    VALUES 
        (1, 'Design Patterns'),
        (1, 'Architecture'),
        (1, 'JDBC'),
        (1, 'General'),
        (1, 'Logistics'),
        (2, 'Hypothesis Testing'),
        (2, 'Combinatorics'),
        (2, 'Probability Distributions'),
        (3, 'SQL'),
        (3, 'Normalization'),
        (3, 'General'),
        (3, 'Logistics'),
        (3, 'Project'),
        (3, 'Data Redundancy'),
        (3, 'Specialization Hierarchies'),
        (1, 'GitHub'),
        (1, 'JavaFX');
    
--Class:
INSERT INTO Class
    (Crs_ID, Sem_ID) 
    VALUES
        (1, 1), 
        (1, 3),
        (2, 2), 
        (3, 2);

--Registration:
INSERT INTO Registration
     (Class_ID, UnivMem_ID, Reg_Type)
     VALUES
         (1, 1, 'TA'), -- Jonah
         (2, 1, 'TA'), -- Jonah
         (1, 8, 'PROF'), -- Richard Nguyen 
         (2, 9, 'PROF'), -- William McBurney
         (2, 6, 'STUD'), -- John Doe
         (3, 1, 'STUD'),
         (3, 2, 'STUD'),
         (3, 3, 'STUD'),
         (4, 4, 'PROF'), -- Mary Smith
         (4, 5, 'TA'), -- Ishan
         (3, 6, 'STUD'), -- John Doe
         (3, 7, 'STUD'), -- Jane Doe
         (1, 6, 'STUD'), -- John Doe
         (4, 1, 'STUD'),-- Jonah
         (1, 2, 'STUD'),--Yuxi
         (1, 7, 'STUD'); --Jane Doe
         
INSERT INTO Assignment
    (Class_ID, Assign_Name)
    VALUES
        (1, 'HW1 A/B Apportionment'),
        (1, 'HW1 C Apportionment'),
        (1, 'HW2 Wordle Debugging'),
        (1, 'HW3 Apportionment Refactoring'),
        (2, 'HW1 A/B Apportionment'),
        (2, 'HW1 C Apportionment'),
        (2, 'HW2 Wordle Debugging'),
        (2, 'HW3 Apportionment Refactoring'),
        (4, 'Practice Chapter 6'),
        (4, 'Practice Chapter 7'),
        (4, 'Project Report 1'),
        (4, 'Project Report 2'),
        (4, 'Project Final Report'),
        (4, 'Quiz 1'),
        (4, 'Quiz 2');
        
INSERT INTO AssignmentTopic
    (Assign_ID, CrsTopic_ID)
    VALUES
        (1,4),
        (2, 1),
        (2, 4),
        (3, 1),
        (4, 1),
        (4, 2),
        (5, 4),
        (6, 1),
        (6, 4),
        (7, 1),
        (8, 1),
        (8, 2),
        (9, 10),
        (10, 9),
        (11, 3),
        (12, 13),
        (13, 13),
        (13, 14),
        (13, 15),
        (14, 11),
        (14, 12),
        (15, 11),
        (15, 12);
        
INSERT INTO OfficeHourSession
    (   
        Class_ID, 
        UnivMem_ID, 
        Loc_ID,
        OHS_StartDateTime, 
        OHS_EndDateTime,
        OHS_Status
    )
    VALUES
        (4, 5, 1, '2023-06-29 13:00:00', '2023-06-29 15:00:00', 'OPEN'),
        (1, 1, 1, '2023-02-03 10:00:00', '2023-02-03 12:30:00', 'OPEN'), --Jonah CS 3140
        (1, 1, 1, '2023-03-03 10:00:00', '2023-03-03 14:30:00', 'OPEN'); --Jonah CS 3140

INSERT INTO OfficeHourQuestion
    (
        OHS_ID, 
        Assign_ID, 
        UnivMem_ID, 
        OHQ_Status,
        OHQ_StudentComment, 
        OHQ_InstructorComment,
        OHQ_OpenedAt,
        OHQ_ClosedAt
    )
    VALUES
        (1, NULL, 1, 'PENDING', 'Wanted clarification on a topic', 'The student wanted help since the textbook did not explain it very well', '2023-06-29 13:00:00', NULL),
        (2, 1, 2, 'ANSWERED', 'How to resolve conflict on Github', 'The issue was experiencing an issue with their repository where the name was already taken.', '2023-02-03 10:03:00', '2023-02-03 10:14:00'),
        (2, 1, 2, 'UNANSWERED', 'There are issues with my repository on Github', 'They did not name their repository correctly.', '2023-02-03 10:10:00', '2023-02-03 10:18:00'),
        (2, 8, 6, 'ANSWERED', 'I updated my mac to the latest java version but when running the initial HW3.java file I am getting the error. How to resolve it?', 'They needed to install an upadted jdk', '2023-02-03 10:12:00', '2023-02-03 10:20:00'),
        (3, 7, 7, 'ANSWERED', 'JavaFX Runtime library issues', 'They needed the M1 JavaFX library for Mac.', '2023-03-03 10:03:00', '2023-03-03 10:10:00'),
        (3, 8, 7, 'UNANSWERED', 'How to create build dependencies?', 'They wanted help with gradl.build', '2023-03-03 10:06:00', '2023-03-03 10:10:00');

INSERT INTO OfficeHourQuestionTopic
    (OHQ_ID, CrsTopic_ID)
    VALUES
        (1, 11),
        (2, 16),
        (3, 16),
        (4, 4),
        (5, 4),
        (6,4);
