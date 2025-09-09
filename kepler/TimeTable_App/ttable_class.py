# insertion of timetable
from .models import *

class TimeTableProblem:
    """This class encapsulates the TimeTable Scheduling problem
    """

    def __init__(self, groupsAmount, slotsPerDay, hardConstraintPenalty):
        """
        :param hardConstraintPenalty: the penalty factor for a hard-constraint violation
        """
        self.hardConstraintPenalty = hardConstraintPenalty

        print('\n Teachers:')
        # list of teachers:
        self.teachers = []
        for item in Teachers.objects.all():
            self.teachers.append(item.id)
            print(self.teachers[-1], " ", item.name)

        print('\n  Subjects:')
        # list of subjects:
        self.subjects = []
        for item in Subjects.objects.all():
            self.subjects.append(item.id)
            print(self.subjects[-1], " ", item.title)

        print('\n Classrooms:')
        # list of classrooms:
        self.classrooms = []
        for item in Classrooms.objects.all():
            self.classrooms.append(item.id)
            print(self.classrooms[-1], " ", item.number)

        print('\n Teachers preference:')
        # list of teachers_preference:
        self.teachers_preference = []
        for item in Teachers.objects.all():
            self.teachers_preference.append(
                [item.available_on_monday, item.available_on_tuesday, item.available_on_wednesday,
                 item.available_on_thursday, item.available_on_friday])
            print(self.teachers_preference[-1])

        print('\nClassrooms_available:')
        # list of classrooms_available:
        self.classrooms_available = []
        for item in Classrooms.objects.all():
            self.classrooms_available.append(
                [item.available_on_monday, item.available_on_tuesday, item.available_on_wednesday,
                 item.available_on_thursday, item.available_on_friday])
            print(self.classrooms_available[-1])

        # number of groups we create a schedule for:
        self.groups = groupsAmount
        self.slotsPerDay = slotsPerDay
        self.daysPerWeek = 5

        self.teachersShift   = len(self.teachers)
        self.subjectShift    = len(self.subjects)
        self.classroomsShift = len(self.classrooms)


    def __len__(self):
        """
        :return: the number of slots in the schedule
        """
        return self.groups * self.daysPerWeek * self.slotsPerDay * len(self.classrooms)* len(self.teachers)

    def getCost(self, schedule):
        """
        Calculates the total cost of the various violations in the given schedule
        ...
        :param schedule: a list of binary values describing the given schedule
        :return: the calculated cost
        """

        if len(schedule) != self.__len__():
            raise ValueError("size of schedule list should be equal to ", self.__len__())

        # convert entire schedule into a dictionary with a separate schedule for each group:
        groupTtableDict = self.getGroupTtable(schedule)

        # count the various violations:
        LessonsNumberViolations = self.countLessonsNumberViolations(groupTtableDict)
        #print('LessonsNumberViolations')
        SameTeacherViolations = self.countSameTeacherViolations(groupTtableDict)
        #print('SameTeacherViolations')
        SameTimeInClassViolations = self.countSameTimeInClassViolations(groupTtableDict)
        #print('SameTimeInClassViolations')
        WrongLessonViolations = self.countWrongLessonViolations(groupTtableDict)
        #print('WrongLessonViolations')
        TeacherAvailabilityViolations = 0 #self.countTeacherAvailabilityViolations(groupTtableDict)
        ClassroomsAvailabilityViolations = 0 #self.countClassroomsAvailabilityViolations(groupTtableDict)

        # calculate the cost of the violations:
        hardContstraintViolations = LessonsNumberViolations + SameTeacherViolations + SameTimeInClassViolations + WrongLessonViolations
        softContstraintViolations = TeacherAvailabilityViolations + ClassroomsAvailabilityViolations

        priceValue = self.hardConstraintPenalty * hardContstraintViolations + softContstraintViolations
        # print('getCost', priceValue)

        return priceValue

    def getGroupTtable(self, schedule):
        """
        Converts the entire schedule into a dictionary with a separate schedule for each group
        :param schedule: a list of binary values describing the given schedule
        :return: a dictionary with each group as a key and the corresponding shifts as the value
        """
        slotsPerGroup = self.__len__() // self.groups
        groupTtableDict = {}
        shiftIndex = 0

        for group in range(1, self.groups + 1):
            groupTtableDict[group] = schedule[shiftIndex:shiftIndex + slotsPerGroup]
            shiftIndex += slotsPerGroup

        return groupTtableDict

    def countLessonsNumberViolations(self, groupTtableDict):
        """
        Counts the max-lesson number violations in the schedule
        :param groupTtableDict: a dictionary with a separate schedule for each group
        :return: count of violations found
        """
        violations = 0

        # Number of subject lessons (length od the array is triple time longer
        # then amount of subjects because of 3 types of lessons)

        subjectShift = self.subjectShift
        double_subjectShift = subjectShift * 2

        subjectsNumber = [0] * (3 * subjectShift + 1) # '+1' is for dummy lesson

        # iterate over the shifts of each group:
        for group in groupTtableDict.values():  # all shifts of a single group
            # iterate over the shifts of each group:
            for subject in Subjects.objects.all():
                for i in range(0, len(group)):
                    # count all the '1's over the week:
                    if group[i] == subject.id:
                        subjectsNumber[subject.id] += 1
                    elif group[i] == subject.id + subjectShift:
                        subjectsNumber[subject.id + subjectShift] += 1
                    elif group[i] == subject.id  + double_subjectShift:
                        subjectsNumber[subject.id + double_subjectShift] += 1
                    lesson_id = group[i]
                    if 1 <= lesson_id <= subjects_count:
                        subjectsNumber[lesson_id] += 1
                    elif subjectShift < lesson_id <= 2 * subjects_shift:
                        subjectsNumber[lesson_id] += 1
                    elif 2 * subjectShift < lesson_id <= 3 * subjects_shift:
                        subjectsNumber[lesson_id] += 1
                #print(len(group)," ",subject.id," ", subject.id + subjectShift, " ", subject.id + double_subjectShift, " ", len(Subjects.objects.all()))
                #print(subjectsNumber)
                if subjectsNumber[subject.id] != subject.lectures:
                    violations += 1
                if subjectsNumber[subject.id + subjectShift] != subject.studies:
                    violations += 1
                if subjectsNumber[subject.id + double_subjectShift] != subject.praktical_work:
                    violations += 1

        return violations

    def countSameTeacherViolations(self, groupTtableDict):
        """
        Counts the same teacher violations in the schedule
        :param groupTtableDict: a dictionary with a separate schedule for each group
        :return: count of violations found
        """
        violations = 0
        groupTtableDictCopy = groupTtableDict.copy()  # copy of dictionary for acceleration of calculations

        # iterate over the shifts of each group:
        for key, group1 in groupTtableDict.items():
            _ = groupTtableDictCopy.pop(key)
            for group2 in groupTtableDictCopy.values():
                if group1 != group2:
                    for i in range(0, len(group1)):
                        if group1[i] * group2[i] != 0:
                            violations += 1
        groups_list = list(groupTtableDict.values())
        for i, group1 in enumerate(groups_list):
            for group2 in groups_list[i+1:]:
                for j in range(len(group1)):
                    if group1[j] and group2[j]:
                        violations += 1

        return violations

    def countSameTimeInClassViolations(self, groupTtableDict):
        """
        Counts the same time in the class violations in the schedule
        :param groupTtableDict: a dictionary with a separate schedule for each group
        :return: count of violations found
        """
        violations = 0
        teachersShift = self.teachersShift
        groupTtableDictCopy = groupTtableDict.copy()  # copy of dictionary for acceleration of calculations

        # iterate over the shifts of each group:
        for key, group1 in groupTtableDict.items():
            _ = groupTtableDictCopy.pop(key)
            for group2 in groupTtableDictCopy.values():
                for i in range(0, len(group1), teachersShift):
                    sum1 = sum(group1[i:i + teachersShift])
                    sum2 = sum(group2[i:i + teachersShift])
                    if sum1 * sum2 != 0:
        groups_list = list(groupTtableDict.values())
        for i, group1 in enumerate(groups_list):
            for group2 in groups_list[i+1:]:
                for j in range(0, len(group1), teachersShift):
                    sum1 = sum(group1[j:j + teachersShift])
                    sum2 = sum(group2[j:j + teachersShift])
                    if sum1 and sum2:
                        violations += 1

        return violations

    def countWrongLessonViolations(self, groupTtableDict):
        """
        Counts the wrong lesson (classroom limitation) violations in the schedule
        :param groupTtableDict: a dictionary with a separate schedule for each group
        :return: count of violations found
        """
        violations: int = 0
        violations = 0
        classroomShift = self.teachersShift # смещение в массиве, соответствующее одной аудитории (т.е. перебор всех учителей)
        oneDayShift    = self.slotsPerDay*self.classroomsShift*self.teachersShift # смещение в массиве, соответствующее одному дню
        oneSlotShift   = self.classroomsShift*self.teachersShift  # смещение в массиве, соответствующее одному занятию


        subjectShift = self.subjectShift
        double_subjectShift = subjectShift * 2
        triple_subjectShift = subjectShift * 3

        # Pre-fetch classrooms to avoid multiple DB queries
        all_classrooms = list(Classrooms.objects.all())

        # iterate over the shifts of each group:
        for group1 in groupTtableDict.values():

            for i in range(0, len(group1), oneDayShift):
                for j in range(i, i+oneDayShift,oneSlotShift):
                    classroom_id = 0
                    for k in range(j, j+oneSlotShift, classroomShift):
                        sum1 = sum(group1[k:k + classroomShift])  # only one lesson value is inside this list
                        one_class_lessons = group1[k:k + classroomShift]
                        classroom_id += 1
                        Classroom = Classrooms.objects.get(id=classroom_id)
                        Classroom = all_classrooms[classroom_id - 1]
                        for m in one_class_lessons:
                            if m< subjectShift and Classroom.lectures != True:
                            if m and m <= subjectShift and not Classroom.lectures:
                                violations += 1
                            elif m< double_subjectShift and Classroom.studies != True:
                            elif m and m <= double_subjectShift and not Classroom.studies:
                                violations += 1
                            elif m< triple_subjectShift and Classroom.praktical_work != True:
                            elif m and m <= triple_subjectShift and not Classroom.praktical_work:
                                violations += 1

        return violations

    def countTeacherAvailabilityViolations(self, groupTtableDict):
        """
        Counts availability of teachers in the schedule
        :param groupTtableDict: a dictionary with a separate schedule for each group
        :return: count of violations found
        """
        violations = 0
        teacherShift = self.teachersShift
        oneDayShift  = self.slotsPerDay*self.classroomsShift*self.teachersShift

        # Pre-fetch teachers to avoid multiple DB queries
        all_teachers = list(Teachers.objects.all())

        # iterate over the shifts of each group:
        for group in groupTtableDict.values():
            dayNumber = 0
            for i in range(0, len(group), oneDayShift):
                dayNumber += 1
                for j in range (i, i+oneDayShift, teacherShift):
                    teacherID = 0
                    for k in range (j, j+teacherShift):
                        teacherID +=1
                        Teacher = Teachers.objects.get(id=teacherID)
                        if dayNumber ==1:
                            if group[k] != 0 and Teacher.available_on_monday == False:
                        Teacher = all_teachers[teacherID - 1]
                        if group[k] != 0:
                            if dayNumber == 1 and not Teacher.available_on_monday:
                                violations += 1
                        elif dayNumber ==2:
                            if group[k] != 0 and Teacher.available_on_tuesday == False:
                            elif dayNumber == 2 and not Teacher.available_on_tuesday:
                                violations += 1
                        elif dayNumber == 3:
                            if group[k] != 0 and Teacher.available_on_wednesday == False:
                            elif dayNumber == 3 and not Teacher.available_on_wednesday:
                                violations += 1
                        elif dayNumber == 4:
                            if group[k] != 0 and Teacher.available_on_thursday == False:
                            elif dayNumber == 4 and not Teacher.available_on_thursday:
                                violations += 1
                        elif dayNumber == 5:
                            if group[k] != 0 and Teacher.available_on_friday == False:
                            elif dayNumber == 5 and not Teacher.available_on_friday:
                                violations += 1

        return violations

    def countClassroomsAvailabilityViolations(self, groupTtableDict):
        """
        Counts availability of classrooms in the schedule
        :param groupTtableDict: a dictionary with a separate schedule for each group
        :return: count of violations found
        """
        violations = 0
        classroomsShift = self.teachersShift
        oneDayShift     = self.slotsPerDay * self.classroomsShift * self.teachersShift
        oneSlotShift    = self.classroomsShift * self.teachersShift

        # Pre-fetch classrooms to avoid multiple DB queries
        all_classrooms = list(Classrooms.objects.all())

        # iterate over the shifts of each group:
        for group in groupTtableDict.values():
            dayNumber = 0
            for i in range(0, len(group), oneDayShift):
                dayNumber += 1
                lessonNumber = 0
                for j in range(i, i + oneDayShift, oneSlotShift):
                    lessonNumber +=1
                    classRoomID   = 0
                    for k in range(j,j+oneSlotShift,classroomsShift):
                        classRoomID +=1
                        sum1 = 0
                        sum1 += sum(group[k:k + classroomsShift])

                        ClassRoom = Classrooms.objects.get(id=classRoomID)
                        if dayNumber == 1:
                            if sum1 != 0      and ClassRoom.available_on_monday == False:
                        sum1 = sum(group[k:k + classroomsShift])
                        ClassRoom = all_classrooms[classRoomID - 1]
                        if sum1 != 0:
                            if dayNumber == 1 and not ClassRoom.available_on_monday:
                                violations += 1
                            elif dayNumber == 2:
                                if sum1  != 0 and ClassRoom.available_on_tuesday == False:
                                    violations += 1
                            elif dayNumber == 3:
                                if sum1  != 0 and ClassRoom.available_on_wednesday == False:
                                    violations += 1
                            elif dayNumber == 4:
                                if sum1  != 0 and ClassRoom.available_on_thursday == False:
                                    violations += 1
                            elif dayNumber == 5:
                                if sum1  != 0 and ClassRoom.available_on_friday == False:
                                    violations += 1
                            elif dayNumber == 2 and not ClassRoom.available_on_tuesday:
                                violations += 1
                            elif dayNumber == 3 and not ClassRoom.available_on_wednesday:
                                violations += 1
                            elif dayNumber == 4 and not ClassRoom.available_on_thursday:
                                violations += 1
                            elif dayNumber == 5 and not ClassRoom.available_on_friday:
                                violations += 1

        return violations

    def printScheduleInfo(self, schedule):
        """
        Prints the schedule and violations details
        :param schedule: a list of binary values describing the given schedule
        """
        groupTtableDict = self.getGroupTtable(schedule)

        print("Schedule for each group:")
        for group in groupTtableDict:  # ttable of a single group
            print(group, ":", groupTtableDict[group])

        print("number of lessons violations = ", self.countLessonsNumberViolations(groupTtableDict))
        print()
        print("the same teacher violations = ", self.countSameTeacherViolations(groupTtableDict))
        print()
        print("the same time in class violations = ", self.countSameTimeInClassViolations(groupTtableDict))
        print()
        print("the wrong lesson violations = ", self.countWrongLessonViolations(groupTtableDict))
        print()
        print("the teachers schedule violations = ", self.countTeacherAvailabilityViolations(groupTtableDict))
        print()
        print("the classrooms schedule violations = ", self.countClassroomsAvailabilityViolations(groupTtableDict))
        print()

def tt_test():
    ttable = TimeTableProblem(4, 5,10)
    out = ""
    for item in ttable.teachers:
        out += f"{item};\n"

    return out
