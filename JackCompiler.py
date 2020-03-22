from symbolTable import symbolTable
from VMWriter import VMWriter
import sys
import os
class JackCompiler:
    Operators = ['+', '-', '*', '/', '|', '&gt', '&amp', '&lt']
    methods=["constructor","function","method"]
    def __init__(self,file):
        self.symbolTable = symbolTable(file)
        self.output_file = self.openfile(file)
        self.vmwriter = VMWriter(self.output_file)
        self.left_arrflag = False
        self.right_arrflag = False
        self.eq_flag = False
        self.letflag=False
        self.class_name=''
        self.argscounter=0
        self.left_counter=0
        self.right_counter=0
        self.name_methods=[]
        self.findmethods()
    def findmethods(self):
        for i in range(len(self.symbolTable.tekonizer.all_tokens)):
            if self.symbolTable.tekonizer.all_tokens[i] == "method":
                self.name_methods.append(self.symbolTable.tekonizer.all_tokens[i+2])
    def openfile(self, file):
        """ This function opens a file to write """
        point = file.find('.')
        new_path = file[:point] + '.vm'
        output_file = open(new_path, 'w')
        return output_file

    def compileClass(self):
        if (self.symbolTable.tekonizer.current_token == "class"):
            self.symbolTable.tekonizer.advance()
            self.class_name+=self.symbolTable.tekonizer.current_token
            self.symbolTable.tekonizer.advance()
            self.symbolTable.tekonizer.advance()
            self.symbolTable.compile_classvarDec()
            while(self.symbolTable.tekonizer.current_token in self.methods):
                if(self.symbolTable.tekonizer.current_token == "constructor"):
                    self.compile_constructor()
                elif(self.symbolTable.tekonizer.current_token == "function"):
                    self.compile_function()
                elif (self.symbolTable.tekonizer.current_token == "method"):
                    self.compile_method()

    def compile_constructor(self):
        self.symbolTable.clear_subroutineTable()
        self.symbolTable.tekonizer.advance()  # name
        constructur_name=self.symbolTable.tekonizer.current_token
        self.symbolTable.tekonizer.advance()  # new
        self.symbolTable.tekonizer.advance()  # (
        self.symbolTable.tekonizer.advance()
        if (self.symbolTable.tekonizer.current_token != ')'):
            self.symbolTable.compile_arguments()
        self.symbolTable.tekonizer.advance()  # )
        self.symbolTable.tekonizer.advance()  # {
        self.symbolTable.compile_subroutine()
        self.vmwriter.write_function(constructur_name + '.new' , str(self.symbolTable.local_cunter))
        self.output_file.write("push constant " + str(self.symbolTable.field_counter) + '\n')
        self.output_file.write("call Memory.alloc 1" + '\n')
        self.output_file.write("pop pointer 0" + '\n') # this
        self.compile_statements()
        self.symbolTable.tekonizer.advance()

    def compile_function(self):
        self.symbolTable.clear_subroutineTable()
        self.symbolTable.tekonizer.advance()
        self.symbolTable.tekonizer.advance()
        name=self.symbolTable.tekonizer.current_token
        self.symbolTable.tekonizer.advance()
        self.symbolTable.tekonizer.advance()
        if (self.symbolTable.tekonizer.current_token != ')'):
            self.symbolTable.compile_arguments()
        self.symbolTable.tekonizer.advance()
        self.symbolTable.tekonizer.advance()
        self.symbolTable.compile_subroutine()
        self.vmwriter.write_function(self.class_name+'.'+name,self.symbolTable.local_cunter)
        self.compile_statements()
        self.symbolTable.tekonizer.advance()

    def compile_method(self):
        self.symbolTable.clear_subroutineTable()
        self.symbolTable.tekonizer.advance()
        self.symbolTable.tekonizer.advance()
        name=self.symbolTable.tekonizer.current_token
        self.symbolTable.tekonizer.advance()
        self.symbolTable.tekonizer.advance()
        self.symbolTable.Table_subroutinevarDec.append(["argument",self.class_name,"this",self.symbolTable.argument_counter])
        self.symbolTable.argument_counter+=1
        if (self.symbolTable.tekonizer.current_token != ')'):
            self.symbolTable.compile_arguments()
        self.symbolTable.tekonizer.advance()
        self.symbolTable.tekonizer.advance()
        self.symbolTable.compile_subroutine()
        self.vmwriter.write_function(self.class_name + '.' + name, self.symbolTable.local_cunter)
        self.vmwriter.write_push("argument",0)
        self.vmwriter.write_pop("pointer",0)
        self.compile_statements()
        self.symbolTable.tekonizer.advance()

    def compile_excpression(self):
        self.compile_term()
        while(self.symbolTable.tekonizer.current_token in self.Operators or self.symbolTable.tekonizer.current_token == '='):
            operator=self.symbolTable.tekonizer.current_token
            self.symbolTable.tekonizer.advance()
            self.compile_term()
            self.vmwriter.writeArthimetcs(operator)

    def compile_term(self):
        if(self.symbolTable.tekonizer.return_typetoken() == "integerconstant"):
            self.vmwriter.write_push("constant", self.symbolTable.tekonizer.current_token)
            self.symbolTable.tekonizer.advance()
        elif(self.symbolTable.tekonizer.return_typetoken() == "stringconstant"):
            self.handle_str()
            self.symbolTable.tekonizer.advance()
        elif (self.symbolTable.tekonizer.return_typetoken() == "keyword"):
            if(self.symbolTable.tekonizer.current_token == "null" or self.symbolTable.tekonizer.current_token == "false"):
                self.vmwriter.write_push("constant",0)
                self.symbolTable.tekonizer.advance()
            elif(self.symbolTable.tekonizer.current_token == "this"):
                self.vmwriter.write_push("pointer",0)
                self.symbolTable.tekonizer.advance()
            elif(self.symbolTable.tekonizer.current_token == "true"):
                self.vmwriter.write_push("constant",0)
                self.vmwriter.writeArthimetcs('not')
                self.symbolTable.tekonizer.advance()
        elif(self.symbolTable.tekonizer.current_token == '('):
            self.symbolTable.tekonizer.advance()
            self.compile_excpression()
            self.symbolTable.tekonizer.advance()
        elif (self.symbolTable.tekonizer.return_typetoken() == "identifier"):
            var_name=self.symbolTable.tekonizer.current_token
            if(self.symbolTable.tekonizer.all_tokens[self.symbolTable.tekonizer.counter+1] == '['):
                if(self.eq_flag):
                    self.right_arrflag = True
                else:
                    self.left_arrflag = True
                if(self.right_arrflag):
                    self.right_counter+=1
                else:
                    self.left_counter+=1
                self.compile_arr(var_name)
                if(not self.letflag):
                    self.left_arrflag = False
            elif(self.symbolTable.tekonizer.all_tokens[self.symbolTable.tekonizer.counter+1] == '.'):
                #handle_object
                self.handle_point(var_name)
            elif (self.symbolTable.tekonizer.all_tokens[self.symbolTable.tekonizer.counter + 1] == '('):
                #handle subroutine_call
                self.compile_subroutinecall(var_name)

            else:
                #only identifier
                row = self.symbolTable.return_row(var_name)
                self.vmwriter.write_push(row[0],row[3])
                self.symbolTable.tekonizer.advance()

        elif(self.symbolTable.tekonizer.current_token == '~' or self.symbolTable.tekonizer.current_token == '-'):
            operator=self.symbolTable.tekonizer.current_token
            self.symbolTable.tekonizer.advance()
            self.compile_term()
            if (operator == '~'):
                self.vmwriter.writeArthimetcs("not")
            else:
                self.vmwriter.writeArthimetcs("neg")


    def compile_subroutinecall(self,name):
        argscounter = 0
        if (name in self.name_methods):
            self.vmwriter.write_push("pointer",0)
            argscounter+=1
        self.symbolTable.tekonizer.advance()  # (
        self.symbolTable.tekonizer.advance()  # firstarg
        argscounter=self.handle_parameters(argscounter) #)
        self.vmwriter.write_call(self.class_name+'.'+name, argscounter)
        self.symbolTable.tekonizer.advance()  # after )

    def compile_statements(self):
        if (self.symbolTable.tekonizer.current_token == "let"):
            self.compile_let()
            self.compile_statements()
        if (self.symbolTable.tekonizer.current_token == "do"):
            self.compile_do()
            self.compile_statements()
        if (self.symbolTable.tekonizer.current_token == "return"):
            self.compile_return()
            self.compile_statements()
        if (self.symbolTable.tekonizer.current_token == "if"):
            self.compile_if()
            self.compile_statements()
        if (self.symbolTable.tekonizer.current_token == "while"):
            self.compile_while()
            self.compile_statements()


    def compile_let(self):
        self.letflag=True
        self.symbolTable.tekonizer.advance() #varname
        varname = self.symbolTable.tekonizer.current_token
        if (self.symbolTable.tekonizer.all_tokens[self.symbolTable.tekonizer.counter+1]== '['):
            self.left_arrflag=True
            self.left_counter+=1
            self.compile_arr(varname)
        else:
            self.symbolTable.tekonizer.advance()
        self.symbolTable.tekonizer.advance() #after =
        self.eq_flag = True
        self.compile_excpression()
        if (self.left_counter == 1 and self.left_arrflag):
            self.vmwriter.write_pop("temp", 0)
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("temp", 0)
            self.vmwriter.write_pop("that", 0)
            self.left_counter-=1
        if (self.left_arrflag == False):
            row = self.symbolTable.return_row(varname)
            self.vmwriter.write_pop(row[0],row[3])
        self.left_arrflag = False

        self.symbolTable.tekonizer.advance()  # after ;
        self.eq_flag = False
        self.letflag=False

    def compile_do(self):
        self.symbolTable.tekonizer.advance() #varname
        name = self.symbolTable.tekonizer.current_token
        if (self.symbolTable.tekonizer.all_tokens[self.symbolTable.tekonizer.counter+1] == '('):
            self.compile_subroutinecall(name)
        elif (self.symbolTable.tekonizer.all_tokens[self.symbolTable.tekonizer.counter + 1] == '.'):
            self.handle_point(name)
        self.symbolTable.tekonizer.advance()
        self.vmwriter.write_pop("temp",0)

    def compile_return(self):
        self.symbolTable.tekonizer.advance()
        if(self.symbolTable.tekonizer.current_token != ';'):
            self.compile_excpression()
            self.symbolTable.tekonizer.advance()
        else:
            self.symbolTable.tekonizer.advance()
            self.vmwriter.write_push("constant",0)
        self.vmwriter.write_return()

    def compile_if(self):
        counter=self.symbolTable.if_counter
        self.symbolTable.if_counter+=1
        self.symbolTable.tekonizer.advance()
        self.symbolTable.tekonizer.advance()
        self.compile_excpression()#)
        self.symbolTable.tekonizer.advance()#{
        #self.vmwriter.writeArthimetcs("not")
        self.vmwriter.write_ifgoto("IFTRUE_"+str(counter))
        self.vmwriter.write_goto("IFFALSE_"+str(counter))
        self.vmwriter.write_Label("IFTRUE_"+str(counter))
        self.symbolTable.tekonizer.advance()
        self.compile_statements()
        self.symbolTable.tekonizer.advance()
        self.vmwriter.write_goto("IFEND_" + str(counter))
        if (self.symbolTable.tekonizer.current_token != "else"):
            self.vmwriter.write_Label("IFFALSE_"+ str(counter))
            self.vmwriter.write_Label("IFEND_" + str(counter))
        elif(self.symbolTable.tekonizer.current_token == "else"):
            self.vmwriter.write_Label("IFFALSE_" + str(counter))
            self.symbolTable.tekonizer.advance()
            self.symbolTable.tekonizer.advance()
            self.compile_statements()
            self.vmwriter.write_Label("IFEND_" + str(counter))
            self.symbolTable.tekonizer.advance()
        #self.symbolTable.if_counter-=1

    def compile_while(self):
        counter = self.symbolTable.while_counter
        self.symbolTable.while_counter+=1
        self.vmwriter.write_Label("WHILE_STATEMENT_"+str(counter))
        self.symbolTable.tekonizer.advance()
        self.symbolTable.tekonizer.advance()
        self.compile_excpression()#)
        self.vmwriter.writeArthimetcs("not")
        self.symbolTable.tekonizer.advance()#{
        self.vmwriter.write_ifgoto("WHILE_END_" + str(counter))
        self.symbolTable.tekonizer.advance()
        self.compile_statements()
        self.vmwriter.write_goto("WHILE_STATEMENT_"+str(counter))
        self.vmwriter.write_Label("WHILE_END_"+str(counter))
        self.symbolTable.tekonizer.advance()
        #self.symbolTable.while_counter-=1


    def compile_arr(self,arr_name):
        row = self.symbolTable.return_row(arr_name)
        self.vmwriter.write_push(row[0], row[3])
        self.symbolTable.tekonizer.advance() #[
        self.symbolTable.tekonizer.advance()
        self.compile_excpression()
        self.vmwriter.writeArthimetcs('+')
        if (self.left_counter > 1 and self.left_arrflag and self.letflag):
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("that", 0)
            self.left_counter -= 1
        elif (self.left_counter > 0 and self.left_arrflag and not self.letflag):
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("that", 0)
            self.left_counter -= 1
        elif(self.right_counter > 0 and self.right_arrflag):
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("that", 0)
            self.right_counter -= 1
        self.arr_flag = False

        self.compile_term()

        self.symbolTable.tekonizer.advance()
        while (self.symbolTable.tekonizer.current_token in self.Operators):
            operator = self.symbolTable.tekonizer.current_token
            self.symbolTable.tekonizer.advance()
            self.compile_term()
            self.vmwriter.writeArthimetcs(operator)


    def handle_parameters(self,argscounter): #assume the current is the first argument ,foo(a,b) ; current=a
        # the argument for the callee is either a variable or a string(char) or an int
        if (self.symbolTable.tekonizer.current_token != ')'):
            argscounter += 1
            self.compile_term()
            while (self.symbolTable.tekonizer.current_token in self.Operators):
                operator = self.symbolTable.tekonizer.current_token
                self.symbolTable.tekonizer.advance()
                self.compile_term()
                self.vmwriter.writeArthimetcs(operator)
            if (self.symbolTable.tekonizer.current_token == ','):
                self.symbolTable.tekonizer.advance()
                argscounter=self.handle_parameters(argscounter)
        return argscounter

    def handle_point(self,name):
        row = self.symbolTable.return_row(name)
        if (row != None):  # an object
            self.vmwriter.write_push(row[0], row[3])
            self.symbolTable.tekonizer.advance()  # .
            self.symbolTable.tekonizer.advance()  # funcname
            func_cal = row[1] + "." + self.symbolTable.tekonizer.current_token
        else:  # the var name is class
            self.symbolTable.tekonizer.advance()  # .
            self.symbolTable.tekonizer.advance()  # funcname
            func_cal = name + "." + self.symbolTable.tekonizer.current_token
        self.symbolTable.tekonizer.advance()  # (
        self.symbolTable.tekonizer.advance()  # firstarg
        self.argscounter = 0
        argscounter=0
        argscounter=self.handle_parameters(0)  # after calling the function the current would be equal to )
        if (row != None):
            self.vmwriter.write_call(func_cal, argscounter + 1)
        else:
            self.vmwriter.write_call(func_cal, argscounter)
        self.symbolTable.tekonizer.advance()  # after )

    def handle_str(self):
        str = self.symbolTable.tekonizer.current_token[1:-1]
        self.vmwriter.write_push("constant", len(str))
        self.vmwriter.write_call("String.new", 1)
        for i in str:
            self.vmwriter.write_push("constant", ord(i))
            self.vmwriter.write_call("String.appendChar", 2)

def main():
    # if the argument is a directory
    if (os.path.isdir(sys.argv[1])):
        for filename in os.listdir(sys.argv[1]):
            if filename.endswith(".jack"):
                parser = JackCompiler(sys.argv[1] + "/" + filename)
                parser.compileClass()
                parser.output_file.close()

        # if the argument is a file
    else:
        parser = JackCompiler(sys.argv[1])
        parser.compileClass()
        parser.output_file.close()


if __name__ == '__main__':
    main()
