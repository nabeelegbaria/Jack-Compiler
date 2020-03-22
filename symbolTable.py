from Tokenizer import Tokenizer
class symbolTable :
    Table_classvarDec = []
    Table_subroutinevarDec = []
    def __init__(self,file):
        self.tekonizer = Tokenizer(file)
        self.static_counter=0
        self.field_counter=0
        self.argument_counter=0
        self.local_cunter=0
        self.if_counter=0
        self.while_counter=0
        self.arr_flag = False


    def compile_classvarDec(self):
        if (self.tekonizer.current_token == "static"):
            x=[]
            x.append(self.tekonizer.current_token)#add static
            self.tekonizer.advance()
            x.append(self.tekonizer.current_token)#add tyoe
            self.tekonizer.advance()
            self.compile_varName(x,True,"static")
        if (self.tekonizer.current_token == "field"):
            x=[]
            x.append(self.tekonizer.current_token)#add field
            self.tekonizer.advance()
            x.append(self.tekonizer.current_token)#add tyoe
            self.tekonizer.advance()
            self.compile_varName(x,True,"field")

    def compile_varName(self,Table,flag,type):
        Table.append(self.tekonizer.current_token)  # add var nam
        if(type=="static"):
            Table.append(self.static_counter)
            self.static_counter+=1
        elif (type == "field"):
            Table.append(self.field_counter)
            self.field_counter += 1
        elif(type=="local"):
            Table.append(self.local_cunter)
            self.local_cunter+=1

        if(flag):
            self.Table_classvarDec.append(Table)
        else:
            self.Table_subroutinevarDec.append(Table)

        self.tekonizer.advance()
        if (self.tekonizer.current_token == ','):
            self.tekonizer.advance()
            new_table = Table[0:2]
            self.compile_varName(new_table,flag,new_table[0])
        if (self.tekonizer.current_token == ';'):
            self.tekonizer.advance()
            if(flag):
                self.compile_classvarDec()
            else:
                self.compile_subroutine()

    def compile_arguments(self):
        #assueme that the current is the first arg
        x=[]
        x.append("argument")
        x.append(self.tekonizer.current_token)
        self.tekonizer.advance()
        x.append(self.tekonizer.current_token)
        x.append(self.argument_counter)
        self.tekonizer.advance()
        self.argument_counter+=1
        self.Table_subroutinevarDec.append(x)
        if(self.tekonizer.current_token == ','):
            self.tekonizer.advance()
            self.compile_arguments()

    def compile_subroutine(self):
        if (self.tekonizer.current_token == "var"):
            x = []
            x.append("local")
            self.tekonizer.advance()
            x.append(self.tekonizer.current_token) #type
            self.tekonizer.advance()
            self.compile_varName(x,False,"local")

    def return_row(self, name):
        for row in self.Table_subroutinevarDec :
            if (row[2] == name):
                return row

        for row in self.Table_classvarDec :
            if (row[2] == name):

                return row
        return None

    def clear_subroutineTable(self):
        self.Table_subroutinevarDec = []
        self.local_cunter=0
        self.argument_counter=0

