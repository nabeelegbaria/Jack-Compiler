
class VMWriter:
    def __init__(self,outputfile):
        self.file = outputfile

    def write_push(self, type, counter , array=False):
        if (type == "field"):
            if (array):
                self.file.write("push that " + str(counter) + '\n')
            else:
                self.file.write("push this " + str(counter) + '\n')
        else:
            self.file.write("push " + type + ' '  + str(counter) + '\n')

    def write_pop(self, type, counter):
        if (type == "field"):
            self.file.write("pop this " + str(counter) + '\n')
        else:
            self.file.write("pop " + type + ' ' + str(counter) + '\n')

    def writeArthimetcs(self, op):
        if(op == '+'):
            self.file.write("add" + '\n')
        elif (op == '-'):
            self.file.write("sub" + '\n')
        elif (op == '*'):
            self.file.write("call Math.multiply 2" + '\n')
        elif (op == '/'):
            self.file.write("call Math.divide 2" + '\n')
        elif (op == '&amp'):
            self.file.write("and" + '\n')
        elif (op == '|'):
            self.file.write("or" + '\n')
        elif (op == '&lt'):
            self.file.write("lt" + '\n')
        elif (op == '&gt'):
            self.file.write("gt" + '\n')
        elif (op == '='):
            self.file.write("eq" + '\n')
        elif (op == 'neg'):
            self.file.write("neg" + '\n')
        elif (op == 'not'):
            self.file.write("not" + '\n')

    def write_Label(self, name):
        self.file.write("label " + name + '\n')

    def write_goto(self,labelname):
        self.file.write("goto " + labelname + '\n')

    def write_ifgoto(self, labelname):
        self.file.write("if-goto " + labelname + '\n')

    def write_call(self, funcname, funcargs):
        self.file.write("call " + funcname + ' ' + str(funcargs) +'\n')

    def write_function(self, funcname, localnum):
        self.file.write("function " + funcname + ' ' + str(localnum) +'\n')

    def write_return(self):
        self.file.write("return" +'\n')
