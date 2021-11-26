import sys, os, getopt, subprocess

def main(argv):
    cpp_file = ''
    exe_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:",["help",'ifile='])
    except getopt.GetoptError as err:
        # print help information and exit
        print(err)      
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--ifile"):
            #cpp_file = a + '.cpp Tokens.cpp Opcodes.cpp'
            cpp_file = a + '.cpp'
            exe_file = a + '.exe'
            filenames = ["fall21-assignment10.cpp", "Tokens.cpp"]
            #complie(cpp_file, exe_file)
            #directory = r"C:\Users\Sarah\Downloads\fall21-assignment10-11-01-2021-03-28-18-20211124T031910Z-001\fall21-assignment10-11-01-2021-03-28-18"
            run(cpp_file, exe_file)
            #for x in os.listdir(directory):
            #    print('student: '+str(x))
            #    os.chdir(directory+'/'+x)
            #    print(os.listdir())
            #    run(cpp_file, exe_file)
            #    misc(filenames)
            #    input()


def usage():
    print('run_cpp.py -i <filename> (without .cpp extension)')

def run(cpp_file, exe_file):
        temp = ''
        x = subprocess.getoutput('cl /EHsc ' + cpp_file)
        print("compile outout: "+str(x))
        try: 
            proc = subprocess.Popen([exe_file, temp],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            (out, err) = proc.communicate(b"3 \n")
            print("program output:", out)
        except FileNotFoundError:
            print("error compliling")

def misc(filenames):
    for f in filenames:
        log = open(f, "r")
        print(log.read())
        #os.system('cat '+f)

if __name__=='__main__':
    main(sys.argv[1:])
