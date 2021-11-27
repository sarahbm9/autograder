from optparse import OptionParser
import os
import sys
import unicodecsv as csv
import subprocess
import traceback

class AutoGrader(object):
    # Initialize the Autograder with arguments specific to an assignment
    def __init__(self, path, first_student, last_student, cpp_files, exe_file, input_string,
                 display_files, skip_compilation):

        # User inputs
        self.path = path
        self.first_student = first_student
        self.last_student = last_student
        self.cpp_files = cpp_files
        self.exe_file = exe_file
        self.input_string = input_string
        self.display_files = display_files
        self.skip_compilation = skip_compilation

        # Private Variables
        self.can_run = True
        self.compiled_students = []
        self.failed_students = []
        self.students_to_grade = []

        # Determine the list of students
        self.known_students = []
        with open('PID.csv','rb') as csvfile:
            timeReader = csv.reader(csvfile, delimiter = ',')
            for row in timeReader:
                self.known_students.append(row[1])
        self.known_students = sorted(self.known_students)

        # Thin down the students to just the ones that are being graded
        if self.first_student not in self.known_students:
            print("Error: First student does not exist as a known student")
            self.can_run = False
        if self.last_student not in self.known_students:
            print("Error: Last student does not exist as a known student")
            self.can_run = False

        if self.can_run:
            first_index = self.known_students.index(self.first_student)
            last_index = self.known_students.index(self.last_student)
            if first_index > last_index:
                print("Error: First and last students not specified in alphabetical order")
                self.can_run = False
            self.students_to_grade = self.known_students[first_index:last_index+1]

        # Display Inputs
        print("----------------- AutoGrader Inputs -----------------")
        print("Path: " + str(self.path))
        print("CPP Files: " + str(self.cpp_files))
        print("EXE Files: " + str(self.exe_file))
        print("Display Files: " + str(self.display_files))
        print("Skip Compilation: " + str(self.skip_compilation))
        print("------------------------------------------\n")

    # Main class processing method
    def run(self):
        # Do the compilation
        print("----------------- Compile -----------------")
        if not skip_compilation:
            self.compileAll()
        else:
            print("Skipping Compilation")
        print("-------------------------------------------\n")

        input("Compilation complete:" + \
              "\n\tStudents to Grade: " + str(len(self.students_to_grade)) + \
              "\n\tSuccessfully Compiled: " + str(len(self.compiled_students)) + \
              "\n\tFailed to Compile: " + str(len(self.failed_students)) + \
              "\nPress Enter to continue...")

        print("------------ Interactive Execute -----------")
        self.interactiveExecute()
        print("--------------------------------------------\n")

    # Compile all of the code for all of the students
    def compileAll(self):
        # Full path to all of the student directories that will be graded
        student_dirs = [f.path for f in os.scandir(self.path) if f.is_dir() and os.path.basename(f.path) in self.students_to_grade]

        # Print out the students that do not have a folder created
        for nonexistent in [s for s in self.students_to_grade if s not in [os.path.basename(d) for d in student_dirs]]:
            print ("Error: " + nonexistent + ": Student did not sumbit source code")

        # For every student
        for dir in student_dirs:
            print("Compiling code for student: " + os.path.basename(dir))

            # Figure out what cpp files to compile and whether they exist
            student_cpp_files = [os.path.join(dir, cpp) for cpp in self.cpp_files]
            if not all([os.path.exists(f) for f in student_cpp_files]):
                print("Error: " + os.path.basename(dir) + ": A specified .cpp file does not exist")
                print("---------------------------------------------")
                continue

            # Figure out the studuent executable file name
            student_exe_file = os.path.join(dir, self.exe_file)

            # Compile the files
            x = subprocess.getoutput("cl /EHsc /Fe\"" + student_exe_file + "\" " + " ".join(student_cpp_files))

            # If the executable doesn't exist, the compilation failed
            if not os.path.exists(student_exe_file):
                print("Error: " + os.path.basename(dir) + ": Could not compile for reason:\n" + str(x))
                print("---------------------------------------------")
                continue

            # Record the student as being successfully compiled
            self.compiled_students.append(os.path.basename(dir))

        # Determine the students that failed compilation
        self.failed_students = [s for s in self.students_to_grade if s not in self.compiled_students]

    # Execute the student's code for interactive grading
    def interactiveExecute(self):
        # Full path to all of the student directories that will be graded, if they compiled
        student_dirs = [f.path for f in os.scandir(self.path) if f.is_dir() and os.path.basename(f.path) in self.compiled_students]

        # For every student
        for dir in student_dirs:
            print("============================================================")
            print("Executing code for student: " + os.path.basename(dir))

            # Figure out the studuent executable file name
            student_exe_file = os.path.join(dir, self.exe_file)

            # Execute the file
            try:
                out = err = None
                proc = subprocess.Popen(student_exe_file, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                if self.input_string is not None:
                    (out, err) = proc.communicate(self.input_string.encode('utf-8') + "\n".encode('utf-8'))
                else:
                    (out, err) = proc.communicate()
                print("Program Output:\n" + str(out))
            except:
                print("Error: Failed to run file: " + str(student_exe_file))
                print("Traceback:\n " + str(traceback.format_exc()))

            # Ask the grader if the output is correct
            output_good = input("\n\nDoes the output look good? (y/n): ")

            # Display the required files if necessary
            if self.display_files is not None:
                student_display_files = [os.path.join(dir, disp) for disp in self.display_files]
                for f in student_display_files:
                    print("-------------------------------------------------------------")
                    if not os.path.exists(f):
                        print("Error: " + os.path.basename(dir) + ": Display File does not exist: " + str(f))
                    else:
                       print(open(f, 'r').read())

                    display_good = input("Does file " + os.path.basename(f) + " look good? (y/n): ")

if __name__ == "__main__":
    # Parse input parameters
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path",
                      help="Path to top-level directory for grading")
    parser.add_option("-f", "--first", dest="first_student",
                      help="First student (alphabetical by last name) to start grading for")
    parser.add_option("-l", "--last", dest="last_student",
                      help="Last student (alphabetical by last name) to stop grading for")
    parser.add_option("-c", "--cpp", dest="cpp_files",
                      help="Comma delimited list of .cpp files needed to compile the desired .exe")
    parser.add_option("-e", "--exe", dest="exe_file",
                      help="Desired name of .exe file")
    parser.add_option("-i", "--input", dest="input_string",
                      help="An input string to be passed into the student's program")
    parser.add_option("-d", "--display", dest="display_files",
                      help="Comma delimited list of .cpp files that you would like to look at")
    parser.add_option("-s", "--skip",
                      action="store_true", dest="skip_compilation", default=False,
                      help="Skip compilation of .cpp files")
    (options, args) = parser.parse_args()

    # Erorr check
    if not options.path:
        print("Error: path is None")
        sys.exit(1)
    if not options.first_student:
        print("Error: first_student is None")
        sys.exit(1)
    if not options.last_student:
        print("Error: last_student is None")
        sys.exit(1)
    if not options.cpp_files:
        print("Error: cpp_files is None")
        sys.exit(1)
    if not options.exe_file:
        print("Error: exe_file is None")
        sys.exit(1)

    # Ensure valid path
    path = str(options.path)
    if not os.path.exists(path):
        print("Error: Path does not exist: " + path)
        sys.exit(1)

    # Get the first student
    first_student = options.first_student

    # Get the last student
    last_student = options.last_student

    # Ensure valid .cpp files specified
    cpp_files = str(options.cpp_files)
    if "," in cpp_files:
        cpp_files = cpp_files.split(",")
    else:
        cpp_files = [cpp_files]
    if not len(cpp_files):
        print("Error: List of .cpp files is empty")
        sys.exit(1)

    # Get name of desired .exe file
    exe_file = str(options.exe_file)

    # Get the input string
    input_string = options.input_string

    # Get the list of files that should be displayed
    display_files = None
    if options.display_files:
        display_files = str(options.display_files)
        if "," in display_files:
            display_files = display_files.split(",")
        else:
            display_files = [display_files]
        if not len(display_files):
            print("List of display files is empty")
            sys.exit(1)

    # Chech whether or not file compilation should be skipped
    skip_compilation = options.skip_compilation

    # Run the AutoGrader
    AG = AutoGrader(path,
                    first_student,
                    last_student,
                    cpp_files,
                    exe_file,
                    input_string,
                    display_files,
                    skip_compilation)
    AG.run()
