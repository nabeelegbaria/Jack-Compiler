class Tokenizer:
    """ A Tokenizer class """

    Keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
                'void', 'true'
        , 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
    Symbols = ['(', ')', '{', '}', '[', ']', ',', ';', '.', '+', '-', '*', '/', '&', '|', '>', '<', '=', '~']
    XML = {'<': '&lt', '>': '&gt', '"': '&quot', '&': '&amp'}
    identifier_parts = ['>', '<', '=', '|', '&', '+', '-', '*', '/', '~', '\n', ' ', '(', ')','{','}',';','.',','
                        ,'[',']']

    def __init__(self, file):
        """ A constructor which initialize the members of the class """
        self.file = file
        self.inputfile = ''
        self.remove_comment()
        self.current_line = ''
        self.all_tokens = []
        self.build_arr()
        self.counter=0
        self.current_token = self.all_tokens[self.counter]

    def remove_comment(self):
        """ This function remove the comments from each line """
        reader = open(self.file, 'r')
        line = reader.readline()
        while (line):
            comment = line.find("//")
            if (comment >= 0):
                line = line[:comment]
            comment=line.find("/**")
            if (comment >= 0):
                line = line[:comment]
            comment = line.find("/*")
            if (comment >= 0):
                line = line[:comment]
            line = line.strip()
            if(line.startswith("*")):
                line=reader.readline()
                continue
            line=line+' '
            self.inputfile += line
            line = reader.readline()
        reader.close()

    def hasMoreTokens(self):
        """ This function checks if there is more tokens in the file or not """
        if(self.counter < len(self.all_tokens)-1):
            return True
        return False

    def advance(self):
        """ This function advances the current token to the next one if it is existed """
        if(self.hasMoreTokens()):
                self.current_token = self.all_tokens[self.counter+1]
                self.counter+=1
        else:
            self.counter += 1

    def tokenType(self):
        """ This function writes the current token into the output file """
        if (self.current_token  in self.Keywords):
            return self.keyWord()
        elif (self.current_token in self.Symbols):
            return self.symbols()
        elif (self.current_token.startswith('"')):
            return self.strConst()
        elif (self.current_token.isdigit()):
            return self.IntConst()
        elif (self.current_token.startswith('&')):
            return self.symbols()
        else:
            return self.Identifier()

    def return_typetoken(self):
        """ This function returns the type of the current token """
        if (self.current_token  in self.Keywords):
            return "keyword"
        elif (self.current_token in self.Symbols):
            return "symbols"
        elif (self.current_token.startswith('"')):
            return "stringconstant"
        elif (self.current_token.isdigit()):
            return "integerconstant"
        elif (self.current_token.startswith('&')):
            return "symbols"
        else:
            return "identifier"

    def keyWord(self):
        """ This function writes into the output file """
        return '<' + "keyword" + '> ' + self.current_token + ' <' +  "/keyword" + '>'

    def symbols(self):
        """ This function writes into the output file """
        if (self.current_token in self.XML.values()):
            return '<' + "symbol" + '> ' + self.current_token + ';' + ' <' + "/symbol" + '>'
        return '<' + "symbol" + '> ' + self.current_token + ' <' + "/symbol" + '>'

    def strConst(self):
        """ This function writes into the output file """
        return '<' + "stringConstant" + '> ' + self.current_token[1:len(self.current_token)-1] +\
               '<' + "/stringConstant" + '>'

    def IntConst(self):
        """ This function writes into the output file """
        return '<' + "integerConstant" + '> ' + self.current_token + ' <' + "/integerConstant" + '>'

    def Identifier(self):
        """ This function writes into the output file """
        return '<' + "identifier" + '> ' + self.current_token + ' <' + "/identifier" + '>'

    def build_arr(self):
        """ This function enters all the token of the given file into an array """
        begin_token = 0
        i = 0
        strflag = True
        while (i <= len(self.inputfile)):
            res = self.inputfile[begin_token:i]
            res.split()
            if(res==' ' ):
                begin_token = i
                i+=1
                continue
            elif(res=='-'):
                self.all_tokens.append(res)
                begin_token = i
                i+=1

            elif res in self.Keywords and self.inputfile[i] == ' ':
                self.all_tokens.append(res)
                begin_token = i
                i += 1
            elif res in self.Symbols:
                if res in self.XML.keys():
                    self.all_tokens.append(self.XML[res])
                    begin_token = i
                    i += 1
                else:
                    self.all_tokens.append(res)
                    begin_token = i
                    i += 1
            # string
            elif (res == '"' and strflag):
                strflag = False
                i += 1
            elif (self.inputfile[i] == '"' and not strflag):
                res = self.inputfile[begin_token:i+1]
                self.all_tokens.append(res)
                strflag = True
                begin_token = i+1
                i += 2
            # int
            elif (res.isdigit() and self.inputfile[i].isdigit()):
                i += 1
            elif (self.inputfile[i].isdigit() and self.inputfile[i].isdigit() == False and strflag):
                res = self.current_line[begin_token:i]
                self.all_tokens.append(res)
                begin_token = i
                i += 1
            elif (res.startswith('-') and self.inputfile[i].isdigit()):
                i+=1
                #identifier
            elif (self.inputfile[i] in self.identifier_parts and res != ''):
                if(strflag):
                    #identefier case
                    self.all_tokens.append(res)
                    begin_token = i
                    i += 1
                else:
                    i+=1
                    continue
            else:
                i += 1