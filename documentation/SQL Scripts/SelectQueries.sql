/* SELECT ALL QUERIES */
SELECT * FROM UniversityMember;
SELECT * FROM Student;
SELECT * FROM Instructor;
SELECT * FROM Professor;
SELECT * FROM TeachingAssistant;
SELECT * FROM Semester;
SELECT * FROM Location;
SELECT * FROM Course;
SELECT * FROM CourseTopic;
SELECT * FROM Class;
SELECT * FROM Registration;
SELECT * FROM Assignment;
SELECT * FROM AssignmentTopic;
SELECT * FROM OfficeHourSession;
SELECT * FROM OfficeHourQuestion;
SELECT * FROM OfficeHourQuestionTopic;

/* SELECT WITH CRITERIA */

-- Lists all office hours that were held online for more than 2 hours.
SELECT
        UM.UnivMem_FirstName || ' ' || UM.UnivMem_LastName as 'Instructor Name',
        L.Loc_Name as 'Held at',
        strftime('%Y/%m/%d', OHS.OHS_StartDateTime) as 'Held on',
        (strftime('%s', OHS.OHS_EndDateTime) - strftime('%s', OHS.OHS_StartDateTime)) / 3600.0 AS 'Held for [n] Hrs.',
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Held for',
        S.Sem_Name || ' ' || S.Sem_Year as 'Held during'
    FROM OfficeHourSession OHS
    JOIN Location L USING (Loc_ID) 
    JOIN UniversityMember UM USING (UnivMem_ID)
    JOIN Class CLS USING (Class_ID)
    JOIN Course CRS USING (Crs_ID)
    JOIN Semester S USING (Sem_ID)
    WHERE 
        Loc_Name LIKE '%online%' AND
        "Held for [n] Hrs." > 2;
        
-- Lists all office hours where there were more than 2 (exclusive) questions asked.
SELECT
        UM.UnivMem_FirstName || ' ' || UM.UnivMem_LastName as 'Instructor Name',
        L.Loc_Name as 'Held at',
        strftime('%Y/%m/%d', OHS.OHS_StartDateTime) as 'Held on',
        (strftime('%s', OHS.OHS_EndDateTime) - strftime('%s', OHS.OHS_StartDateTime)) / 3600.0 AS 'Held for [n] Hrs.',
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Held for',
        S.Sem_Name || ' ' || S.Sem_Year as 'Held during',
        "Questions asked"
    FROM OfficeHourSession OHS
    JOIN (
        SELECT OHS_ID, COUNT(*) as 'Questions asked' FROM OfficeHourQuestion GROUP BY OHS_ID
    ) USING (OHS_ID)
    JOIN UniversityMember UM USING (UnivMem_ID)
    JOIN Class CLS USING (Class_ID)
    JOIN Location L USING (Loc_ID)
    JOIN Course CRS USING (Crs_ID)
    JOIN Semester S USING (Sem_ID)
    WHERE "Questions asked" > 2;

-- Lists all topics for CS courses
SELECT 
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Course',
        group_concat(CT.CrsTopic_Name, ', ') as 'Topics'
    FROM CourseTopic CT
    JOIN Course CRS USING (Crs_ID) 
    WHERE Crs_Subject LIKE 'CS'
    GROUP BY Crs_ID;
    
-- Lists all university members who are enrolled in more than one course
SELECT
        UM.UnivMem_FirstName || ' ' || UM.UnivMem_LastName as 'Name',
        UM.UnivMem_CompID as 'Computing ID',
        count(UnivMem_ID) as 'Number Enrolled'
    FROM Registration R
    JOIN UniversityMember UM USING (UnivMem_ID)
    GROUP BY UnivMem_ID
    HAVING "Number Enrolled" > 1
    ORDER BY UnivMem_FirstName, UnivMem_LastName;

-- Lists all assignments which were linked more than once in office hour questions
SELECT 
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Course',
        S.Sem_Name || ' ' || S.Sem_Year as 'Semester',
        Assign_Name as 'Assignment', 
        COUNT(OHQ_ID) as 'Question Appearances'
    FROM Assignment
    JOIN OfficeHourQuestion USING (Assign_ID)
    JOIN Class CLS USING (Class_ID)
    JOIN Course CRS USING (Crs_ID)
    JOIN Semester S USING (Sem_ID)
    GROUP BY Assign_ID
    HAVING "Question Appearances" > 1;



/* SELECT SUMMARIZATIONS */

-- Shows all the CourseTopics for a course.
SELECT
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Course',
        group_concat(CT.CrsTopic_Name, ',  ') as 'Topics'
    FROM CourseTopic CT
    JOIN Course CRS Using(Crs_ID)
    GROUP BY CT.Crs_ID;

-- Shows the cumulative number of times a course topic has appeared in office hour questions (removing those which do not appear). 
SELECT    
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Course',
        CT.CrsTopic_Name as "Course Topic", 
        SUM(OCCURRENCES) as 'Direct and Indirect Question Linkages'
    FROM (    
        SELECT
                StudentLinkedTopics.CrsTopic_ID,
                Count(DISTINCT OHQ.OHQ_ID) as OCCURRENCES
            FROM OfficeHourQuestion OHQ
            JOIN OfficeHourQuestionTopic QT USING (OHQ_ID)
            JOIN CourseTopic StudentLinkedTopics ON StudentLinkedTopics.CrsTopic_ID=QT.CrsTopic_ID
            GROUP BY StudentLinkedTopics.CrsTopic_ID
        UNION 
        SELECT
                AssignmentLinkedTopics.CrsTopic_ID,
                Count(DISTINCT OHQ.OHQ_ID) as OCCURRENCES
            FROM OfficeHourQuestion OHQ
            JOIN Assignment A USING (Assign_ID)
            JOIN AssignmentTopic AT USING (Assign_ID)
            JOIN CourseTopic AssignmentLinkedTopics ON AssignmentLinkedTopics.CrsTopic_ID=AT.CrsTopic_ID
            GROUP BY AssignmentLinkedTopics.CrsTopic_ID
    ) 
    JOIN CourseTopic CT USING (CrsTopic_ID)
    JOIN Course CRS USING (Crs_ID)
    GROUP BY CrsTopic_ID
    ORDER BY "Course";
    
-- List All Instructors
SELECT 
        U.UnivMem_FirstName || ' ' || U.UnivMem_LastName as 'Instructor Name', 
        R.Reg_Type as 'Instructor Type', 
        Crs.Crs_Subject || ' ' || Crs.Crs_CatalogNumber as 'Course',
        S.Sem_Name || ' ' || S.Sem_Year as 'Semester'
    FROM Registration R
    JOIN UniversityMember U USING (UnivMem_ID)
    JOIN Class Cls USING (Class_ID)
    JOIN Course Crs USING (Crs_ID)
    JOIN Semester S USING (Sem_ID)
    WHERE R.Reg_Type in ('PROF', 'TA')
    ORDER BY R.Reg_Type, U.UnivMem_FirstName, U.UnivMem_LastName;

-- Shows the number of questions answered per instructor for a particular class
SELECT
        UM.UnivMem_FirstName || ' ' || UM.UnivMem_LastName as 'Instructor Name', 
        COUNT(OHQ_ID) as 'Answered Questions',
        Crs.Crs_Subject || ' ' || Crs.Crs_CatalogNumber as 'Course',
        S.Sem_Name || ' ' || S.Sem_Year as 'Semester'
    FROM OfficeHourSession OHS
    JOIN OfficeHourQuestion OHQ USING (OHS_ID)
    JOIN UniversityMember UM Using (UnivMem_ID)
    JOIN Class CLS USING (Class_ID)
    JOIN Course CRS USING (Crs_ID)
    JOIN Semester S USING (Sem_ID)
    GROUP BY CLS.Class_ID
    ORDER BY UM.UnivMem_FirstName, UM.UnivMem_LastName;

-- Shows information about OfficeHourQuestions: Student, Instructor, question comments, Assignment, and student linked topics
SELECT
        Student.UnivMem_FirstName || ' ' || Student.UnivMem_LastName as 'Student Name',
        Instructor.UnivMem_FirstName || ' ' || Instructor.UnivMem_LastName as 'Instructor Name',
        OHQ.OHQ_StudentComment as 'Student Comments',
        OHQ.OHQ_InstructorComment as 'Instructor Comments',
        A.Assign_Name as 'Assignment Name',
        group_concat(CrsTopic_Name, ', ') as 'Student Linked Topics'
    FROM OfficeHourQuestion OHQ
    JOIN OfficeHourSession OHS USING (OHS_ID)
    JOIN UniversityMember Student ON Student.UnivMem_ID=OHQ.UnivMem_ID
    JOIN UniversityMember Instructor ON Instructor.UnivMem_ID=OHS.UnivMem_ID
    LEFT JOIN Assignment A USING (Assign_ID)
    LEFT JOIN OfficeHourQuestionTopic OHQT USING (OHQ_ID)
    LEFT JOIN CourseTopic CT USING (CrsTopic_ID)
    GROUP BY OHQ_ID
    ORDER BY "Student Name", "Instructor Name";
    


/* 
SELECT ASSOCIATIVE ENTITIES: 
    Class (Course-Semester)
    Registration (Class-UniversityMember)
    AssignmentTopic (Assignment-CourseTopic)
    OfficeHourQuestionTopic (OfficeHourQuestion-CourseTopic)
*/

-- Class: shows course and semester
SELECT 
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Course',
        S.Sem_Name || ' ' || S.Sem_Year as 'Semester'
    FROM Class CLS
    JOIN Course CRS USING (Crs_ID)
    JOIN Semester S USING (Sem_ID);

-- Registration: shows UniversityMember, registration type, and class
SELECT 
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Course', 
        S.Sem_Name || ' ' || S.Sem_Year as 'Semester',
        UM.UnivMem_FirstName || ' ' || UM.UnivMem_LastName as 'University Member Name', 
        R.Reg_Type as 'Registered as'
    FROM Registration R
    JOIN UniversityMember UM USING (UnivMem_ID)
    JOIN Class CLS USING (Class_ID)
    JOIN Course CRS USING (Crs_ID)
    JOIN Semester S USING (Sem_ID)
    ORDER BY "University Member Name";
    
-- AssignmentTopic: shows class, assignment name, and related assignment topics
SELECT 
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Course',
        S.Sem_Name || ' ' || S.Sem_Year as 'Semester',
        A.Assign_Name as 'Assignment Name',
        group_concat(CT.CrsTopic_Name, ',  ') as 'Assignment Topics'
    FROM AssignmentTopic AT
    JOIN Assignment A USING (Assign_ID)
    JOIN CourseTopic CT USING (CrsTopic_ID)
    JOIN Class CLS USING (Class_ID)
    JOIN Course CRS USING (Crs_ID)
    JOIN Semester S USING (Sem_ID)
    GROUP BY Assign_ID
    ORDER BY "Course", "Semester", "Assignment Name";

-- OfficeHourQuestionTopic: shows course, the student who asked the question, and the linked topics
SELECT
        Crs_Subject || ' ' || Crs_CatalogNumber as 'Course',
        UM.UnivMem_FirstName || ' ' || UM.UnivMem_LastName as 'Question By',
        group_concat(CrsTopic_Name, ',  ') as 'Linked Topics'
    FROM OfficeHourQuestionTopic
    JOIN OfficeHourQuestion OHQ USING (OHQ_ID)
    JOIN UniversityMember UM USING (UnivMem_ID)
    JOIN CourseTopic CT USING (CrsTopic_ID)
    JOIN Course USING (Crs_ID)
    GROUP BY OHQ_ID
    ORDER BY UM.UnivMem_FirstName, UM.UnivMem_LastName;
    


/* SELECT MASTER REPORT */

--Lists all Questions: their student, their instructor, their course, their semester, their location, their comments, their topics (12 tables joined out of 16)
SELECT
        Student.UnivMem_FirstName || ' ' || Student.UnivMem_LastName as 'Student Name',
        Instructor.UnivMem_FirstName || ' ' || Instructor.UnivMem_LastName || ' (' || R.Reg_Type || ')' as 'Instructor Name',
        CRS.Crs_Subject || ' ' || CRS.Crs_CatalogNumber as 'Course',
        S.Sem_Name || ' ' || S.Sem_Year as 'Semester',
        L.Loc_Name as 'Location',
        OHQ.OHQ_StudentComment as 'Student Comment',
        OHQ.OHQ_InstructorComment as 'Instructor Comment',
        SUBQUERY1.STUD_LINKED_TOPICS as 'Student Linked Topics',
        SUBQUERY2.ASSIGN_LINKED_TOPICS as 'Assignment Linked Topics',
        SUBQUERY2.Assign_Name as 'Assignment Name'
    FROM OfficeHourQuestion OHQ
    JOIN OfficeHourSession OHS USING (OHS_ID)
    JOIN Location L USING (Loc_ID)
    JOIN UniversityMember Instructor ON Instructor.UnivMem_ID=OHS.UnivMem_ID
    JOIN UniversityMember Student ON Student.UnivMem_ID=OHQ.UnivMem_ID
    JOIN Class CLS USING (Class_ID)
    JOIN Course CRS USING (Crs_ID)
    JOIN Semester S USING (Sem_ID)
    LEFT JOIN (
        SELECT 
                OHQ_SUBQUERY.OHQ_ID,
                group_concat(DISTINCT CT.CrsTopic_Name) as STUD_LINKED_TOPICS
            FROM OfficeHourQuestion OHQ_SUBQUERY
            JOIN OfficeHourQuestionTopic QT USING(OHQ_ID)
            JOIN CourseTopic CT USING(CrsTopic_ID)
            GROUP BY OHQ_SUBQUERY.OHQ_ID
        ) SUBQUERY1 ON SUBQUERY1.OHQ_ID=OHQ.OHQ_ID
     LEFT JOIN (
        SELECT
                OHQ_SUBQUERY.OHQ_ID,
                QA.Assign_Name,
                group_concat(DISTINCT CT.CrsTopic_Name) as ASSIGN_LINKED_TOPICS
            FROM OfficeHourQuestion OHQ_SUBQUERY
            JOIN Assignment QA USING(Assign_ID)
            JOIN AssignmentTopic QAT USING (Assign_ID)
            JOIN CourseTopic CT USING(CrsTopic_ID)
            GROUP BY OHQ_SUBQUERY.OHQ_ID
        ) SUBQUERY2 ON SUBQUERY2.OHQ_ID=OHQ.OHQ_ID
    JOIN Registration R ON R.UnivMem_ID=Instructor.UnivMem_ID AND R.Class_ID=OHS.Class_ID;
    