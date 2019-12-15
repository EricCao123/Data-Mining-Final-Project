#imports for the different libraries needed
import os
import re
import csv
from operator import itemgetter
import copy
import random

# This class contains everything for reading books, writing to csv files, and anything not graph related
class Hash:
    #we intialize the class with the required varibles to be used later
    def __init__(self):
        self.complete = {}
        self.books = {}
        self.authors = {}
        self.sortedComplete = {}
        self.sortedCompleteBefore = {}
        self.sortedCompleteAfter = {}
        self.sortedBooks = {}
        self.sortedBooksBefore = {}
        self.sortedBooksAfter = {}
        self.sortedAuthors = {}
        self.sortedAuthorsBefore = {}
        self.sortedAuthorsAfter = {}
        self.listOfBooks = {}
        self.listOfAuthors = {}
        self.listOfComplete = {"hate":0,"adult":0,"function":0,"total":0, "before":{}, "after":{}}
        self.valid_words = []
        self.adult_words = []
        self.hate_words = []
        self.function_words = []
        self.authorAmounts = {}
        
    # a function to load dictionary files
    def loadDictionaries(self):
        cwd = os.getcwd()
        os.chdir(cwd+"/Dictionaries")
        cwd = os.getcwd()
        with open('all_words.txt') as word_file:
            self.valid_words = set(word_file.read().split())
        with open('adult_words.txt') as word_file:
            self.adult_words = set(word_file.read().split())
        with open('hate_words.txt') as word_file:
            self.hate_words = set(word_file.read().split())
        with open('function_words.txt') as word_file:
            self.function_words = set(word_file.read().split())
        os.chdir(os.path.dirname(cwd))
        cwd = os.getcwd()
        
    # a function to read all the books and save them to variables
    def scanBooks(self):
        cwd = os.getcwd()
        os.chdir(cwd+"/Books")
        cwd = os.getcwd()
        books = os.listdir()
        
        for currBook in books:
            titleFound = False
            authorFound = False
            start = False
            title = ""
            author = ""
            if(currBook != '.ipynb_checkpoints'):
                with open(currBook, 'r', errors='ignore') as f:
                    previousWord=""
                    for line in f:
                        if start == True:
                            if line.find("*** END OF THIS PROJECT GUTENBERG EBOOK") == 0:
                                start = False;
                            else:
                                line = re.sub("-", " ", line)
                                for word in line.split():
                                    word = re.sub("^[\W]+|[\W]+$", "", word).lower()
                                    if word in self.valid_words:
                                        self.addWord(title, author, word)
                                        self.increaseNumber(title, author, "total")
                                        if previousWord in self.valid_words:
                                            self.addBeforeAfter(title, author, previousWord, word)
                                    if word in self.adult_words:
                                        self.increaseNumber(title, author, "adult")
                                    if word in self.hate_words:
                                        self.increaseNumber(title, author, "hate")
                                    if word in self.function_words:
                                        self.increaseNumber(title, author, "function")
                                    previousWord=word
                        elif line.find("Title:") == 0:
                            for word in line[7:]:
                                if word != ';':
                                    title+= word
                            titleFound = True
                            title = title.strip()
                        elif line.find("Author:") == 0:
                            for word in line[8:]:
                                if word != ';':
                                    author+= word
                            authorFound = True
                            author = author.strip()
                        elif line.find("*** START OF THIS PROJECT GUTENBERG EBOOK") == 0:
                            start = True
        os.chdir(os.path.dirname(cwd))
        cwd = os.getcwd()
    
    # This function creates csv files for every book based on word counts
    def writeData(self):
        cwd = os.getcwd()
        os.chdir(cwd+"/Data")
        cwd = os.getcwd()
        with open('data.csv', mode = 'w') as data:
            completeData = self.getCompleteData()
            data_writer = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            data_writer.writerow(["word type","number"])
            data_writer.writerow(["everything",completeData["total"]])
            data_writer.writerow(["adult",completeData["adult"]])
            data_writer.writerow(["hate",completeData["hate"]])
            data_writer.writerow(["function",completeData["function"]])
            data_writer.writerow(["normal","number"])
            q = 0
            for key in self.getComplete():
                data_writer.writerow([key[0],key[1]])
        authorsData = self.getListOfAuthors()
        authors = self.getAuthors()
        
        for author in authors:
            if os.path.isdir(author) == False:
                os.mkdir(author)
            os.chdir(cwd+"/"+author)
            cwd = os.getcwd()
            #make a new file and overrite it if it already exists
            with open(author+'.csv', mode = 'w') as data:
                authorData = self.getAuthorData(author)
                data_writer = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow(["word type","number"])
                data_writer.writerow(["everything",authorData["total"]])
                data_writer.writerow(["adult",authorData["adult"]])
                data_writer.writerow(["hate",authorData["hate"]])
                data_writer.writerow(["function",authorData["function"]])
                data_writer.writerow(["normal","number"])
                for key in authors[author]:
                    data_writer.writerow([key[0],key[1]])
            os.chdir(os.path.dirname(cwd))
            cwd = os.getcwd()
            
        booksData = self.getListOfBooks()
        books = self.getBooks()
        for book in books:
            bookData = self.getBookData(book)
            os.chdir(cwd+"/"+bookData['author'])
            cwd = os.getcwd()
            if os.path.isdir(book) == False:
                os.mkdir(book)
            os.chdir(cwd+"/"+book)
            cwd=os.getcwd()
            #make a new file and overrite it if it already exists
            with open(book+'.csv', mode = 'w') as data:
                data_writer = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow(["word type","number"])
                data_writer.writerow(["everything",bookData["total"]])
                data_writer.writerow(["adult",bookData["adult"]])
                data_writer.writerow(["hate",bookData["hate"]])
                data_writer.writerow(["function",bookData["function"]])
                data_writer.writerow(["normal","number"])
                for key in books[book]:
                    data_writer.writerow([key[0],key[1]])
            os.chdir(os.path.dirname(cwd))
            cwd = os.getcwd()
            os.chdir(os.path.dirname(cwd))
            cwd = os.getcwd()
        os.chdir(os.path.dirname(cwd))
        cwd = os.getcwd()      
        #call writeBeforeAfter to finish writing all csv files
        self.writeBeforeAfter()
        
    # this function loads before and after into self variables    
    def addBeforeAfter(self,title,author,previousWord,word):
        completeData = self.getCompleteData()
        completeBefore = completeData["before"]
        if not(word in completeBefore):
            completeBefore[word] = {}
        before = completeBefore[word]
        completeAfter = completeData["after"]
        if not(previousWord in completeAfter):
            completeAfter[previousWord] = {}
        after = completeAfter[previousWord]
        
        if not(previousWord in before):
            before.update( {previousWord : 0} )
        
        if not(word in after):
            after.update( {word : 0} )
        
        before[previousWord] = before[previousWord]+1
        after[word] = after[word]+1

        
        bookData = self.getBookData(title)
        bookBefore = bookData["before"]
        if not(word in bookBefore):
            bookBefore[word] = {}
        before = bookBefore[word]
        bookAfter = bookData["after"]
        if not(previousWord in bookAfter):
            bookAfter[previousWord] = {}
        after = bookAfter[previousWord]
        
        if not(previousWord in before):
            before.update( {previousWord : 0} )
        
        if not(word in after):
            after.update( {word : 0} )
        
        before[previousWord] = before[previousWord]+1
        after[word] = after[word]+1
        
        
        authorData = self.getAuthorData(author)
        authorBefore = authorData["before"]
        if not(word in authorBefore):
            authorBefore[word] = {}
        before = authorBefore[word]
        authorAfter = authorData["after"]
        if not(previousWord in authorAfter):
            authorAfter[previousWord] = {}
        after = authorAfter[previousWord]
        
        if not(previousWord in before):
            before.update( {previousWord : 0} )
        
        if not(word in after):
            after.update( {word : 0} )
        
        before[previousWord] = before[previousWord]+1
        after[word] = after[word]+1
        
    #this function writes the before and after files
    def writeBeforeAfter(self):
        cwd = os.getcwd()
        os.chdir(cwd+"/Data")
        cwd = os.getcwd()

        totalKeys = {}
        with open('before.csv', mode = 'w') as data:
            data_writer = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            data_writer.writerow(["word","First Choice", "Percentage", "Second Choice", "Percentage", "Third Choice", "Percentage"])
            for word in self.sortedCompleteBefore:
                totalKeys[word] = 0
                for key in self.sortedCompleteBefore[word]:
                    totalKeys[word]=totalKeys[word]+key[1]
            for word in self.sortedCompleteBefore:
                line = [word]
                counter = 0;
                for key in self.sortedCompleteBefore[word]:
                    line.append(key[0])
                    line.append(str(round((key[1]/totalKeys[word])*100,2))+"%")
                    if(counter > 1):
                        break;
                    counter=counter+1;
                if totalKeys[word] > 1000:
                    data_writer.writerow(line)
        
        totalKeys = {}
        with open('after.csv', mode = 'w') as data:
            data_writer = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            data_writer.writerow(["word","First Choice", "Percentage", "Second Choice", "Percentage", "Third Choice", "Percentage"])
            for word in self.sortedCompleteAfter:
                totalKeys[word] = 0
                for key in self.sortedCompleteAfter[word]:
                    totalKeys[word]=totalKeys[word]+key[1]
            for word in self.sortedCompleteAfter:
                line = [word]
                counter = 0;
                for key in self.sortedCompleteAfter[word]:
                    line.append(key[0])
                    line.append(str(round((key[1]/totalKeys[word])*100,2))+"%")
                    if(counter > 1):
                        break;
                    counter=counter+1;
                if totalKeys[word] > 1000:
                    data_writer.writerow(line)
        
        
        authorsData = self.getListOfAuthors()
        authors = self.getAuthors()
        for author in authors:
            if os.path.isdir(author) == False:
                os.mkdir(author)
            os.chdir(cwd+"/"+author)
            cwd = os.getcwd()
            
            totalKeys = {}
            with open('before.csv', mode = 'w') as data:
                data_writer = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow(["word","First Choice", "Percentage", "Second Choice", "Percentage", "Third Choice", "Percentage"])
                for word in self.sortedAuthorsBefore[author]:
                    totalKeys[word] = 0
                    for key in self.sortedAuthorsBefore[author][word]:
                        totalKeys[word]=totalKeys[word]+key[1]
                for word in self.sortedAuthorsBefore[author]:
                    line = [word]
                    counter = 0;
                    for key in self.sortedAuthorsBefore[author][word]:
                        line.append(key[0])
                        line.append(str(round((key[1]/totalKeys[word])*100,2))+"%")
                        if(counter > 1):
                            break;
                        counter=counter+1;
                    if totalKeys[word] > 50 * self.authorAmounts[author]['books']:
                        data_writer.writerow(line)

            totalKeys = {}
            with open('after.csv', mode = 'w') as data:
                data_writer = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow(["word","First Choice", "Percentage", "Second Choice", "Percentage", "Third Choice", "Percentage"])
                for word in self.sortedAuthorsAfter[author]:
                    totalKeys[word] = 0
                    for key in self.sortedAuthorsAfter[author][word]:
                        totalKeys[word]=totalKeys[word]+key[1]
                for word in self.sortedAuthorsAfter[author]:
                    line = [word]
                    counter = 0;
                    for key in self.sortedAuthorsAfter[author][word]:
                        line.append(key[0])
                        line.append(str(round((key[1]/totalKeys[word])*100,2))+"%")
                        if(counter > 1):
                            break;
                        counter=counter+1;
                    if totalKeys[word] > 50 * self.authorAmounts[author]['books']:
                        data_writer.writerow(line)
                    
            os.chdir(os.path.dirname(cwd))
            cwd = os.getcwd()
        
        
        booksData = self.getListOfBooks()
        books = self.getBooks()
        for book in books:
            bookData = self.getBookData(book)
            os.chdir(cwd+"/"+bookData['author'])
            cwd = os.getcwd()
            if os.path.isdir(book) == False:
                os.mkdir(book)
            os.chdir(cwd+"/"+book)
            cwd=os.getcwd()
            totalKeys = {}
            with open('before.csv', mode = 'w') as data:
                data_writer = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow(["word","First Choice", "Percentage", "Second Choice", "Percentage", "Third Choice", "Percentage"])
                for word in self.sortedBooksBefore[book]:
                    totalKeys[word] = 0
                    for key in self.sortedBooksBefore[book][word]:
                        totalKeys[word]=totalKeys[word]+key[1]
                for word in self.sortedBooksBefore[book]:
                    line = [word]
                    counter = 0;
                    for key in self.sortedBooksBefore[book][word]:
                        line.append(key[0])
                        line.append(str(round((key[1]/totalKeys[word])*100,2))+"%")
                        if(counter > 1):
                            break;
                        counter=counter+1;
                    if totalKeys[word] > 50:
                        data_writer.writerow(line)

            totalKeys = {}
            with open('after.csv', mode = 'w') as data:
                data_writer = csv.writer(data, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                data_writer.writerow(["word","First Choice", "Percentage", "Second Choice", "Percentage", "Third Choice", "Percentage"])
                for word in self.sortedBooksAfter[book]:
                    totalKeys[word] = 0
                    for key in self.sortedBooksAfter[book][word]:
                        totalKeys[word]=totalKeys[word]+key[1]
                for word in self.sortedBooksAfter[book]:
                    line = [word]
                    counter = 0;
                    for key in self.sortedBooksAfter[book][word]:
                        line.append(key[0])
                        line.append(str(round((key[1]/totalKeys[word])*100,2))+"%")
                        if(counter > 1):
                            break;
                        counter=counter+1;
                    if totalKeys[word] > 50:
                        data_writer.writerow(line)
        #this part changes the directory back to the original
            os.chdir(os.path.dirname(cwd))
            cwd = os.getcwd()
            os.chdir(os.path.dirname(cwd))
            cwd = os.getcwd()
        os.chdir(os.path.dirname(cwd))
        cwd = os.getcwd() 
    #this function returns a book dictionary given a title and author
    def getBookDictionary(self,title, author):
        if title in self.books:
            return self.books[title]
        else:
            return self.createBookDictionary(title, author)
        
    #this function creates a new book dictionary
    def createBookDictionary(self, title, author):
        self.books[title] = {}
        self.listOfBooks[title]={"author":author,"hate":0,"adult":0,"function":0,"total":0, "before":{}, "after":{}}
        return self.books[title]
    
    #this function returns a author dictionary given an author
    def getAuthorDictionary(self,author):
        if author in self.authors:
            return self.authors[author]
        else:
            return self.createAuthorDictionary(author)

    # this function creates a new author dictionary
    def createAuthorDictionary(self, author):
        self.authors[author] = {}
        self.listOfAuthors[author]={"hate":0,"adult":0,"function":0,"total":0, "before":{}, "after":{}}
        return self.authors[author]
    
    #this function adds a word into self variables
    def addWord(self, title, author, word):
        bookDict = self.getBookDictionary(title, author)
        if word in bookDict:
            bookDict[word] = bookDict[word]+1
        else:
            bookDict[word] = 1
            
        authorDict = self.getAuthorDictionary(author)
        if word in authorDict:
            authorDict[word] = authorDict[word]+1
        else:
            authorDict[word] = 1
            
        if word in self.complete:
            self.complete[word] = self.complete[word] + 1
        else:
            self.complete[word] = 1
    
    #this function sorts all the self variables
    def sortEverything(self):
        completeData = self.getCompleteData()
        
        for before in completeData["before"]:
            self.sortedCompleteBefore[before] = sorted(completeData["before"][before].items(), key=lambda kv: kv[1], reverse=True)
        for after in completeData["after"]:
            self.sortedCompleteAfter[after] = sorted(completeData["after"][after].items(), key=lambda kv: kv[1], reverse=True)
            

        for book in self.books: 
            bookData = self.getBookData(book)
            self.sortedBooksBefore[book]={}
            for before in bookData["before"]:
                self.sortedBooksBefore[book][before] = sorted(bookData["before"][before].items(), key=lambda kv: kv[1], reverse=True)
            self.sortedBooksAfter[book]={}
            for after in bookData["after"]:
                self.sortedBooksAfter[book][after] = sorted(bookData["after"][after].items(), key=lambda kv: kv[1], reverse=True)
                
        for author in self.authors:
            authorData = self.getAuthorData(author)
            self.sortedAuthorsBefore[author]={}
            for before in authorData["before"]:
                self.sortedAuthorsBefore[author][before] = sorted(authorData["before"][before].items(), key=lambda kv: kv[1], reverse=True)
            self.sortedAuthorsAfter[author]={}
            for after in authorData["after"]:
                self.sortedAuthorsAfter[author][after] = sorted(authorData["after"][after].items(), key=lambda kv: kv[1], reverse=True)
        
        
        self.sortedComplete = sorted(self.complete.items(), key = lambda kv: kv[1], reverse=True)
        for book in self.books:
            self.sortedBooks[book] = sorted(self.books[book].items(), key=lambda kv: kv[1], reverse=True)
        for author in self.authors:
            self.sortedAuthors[author] = sorted(self.authors[author].items(), key=lambda kv: kv[1], reverse=True)
            
    #this function returns a sorted complete list of all words
    def getComplete(self):
        return self.sortedComplete
    
    #this function returns all the sorted books
    def getBooks(self):
        return self.sortedBooks
    
    #this function returns all the sorted authors
    def getAuthors(self):
        return self.sortedAuthors

    #this function returns a list of books
    def getListOfBooks(self):
        return self.listOfBooks
    
    #this function returns  a list of authors
    def getListOfAuthors(self):
        return self.listOfAuthors
    
    #this function returns a book given a title
    def getBookData(self, title):
        return self.listOfBooks[title]
    
    #this function returns an author given an author
    def getAuthorData(self, author):
        return self.listOfAuthors[author]
    
    #this function returns a complete list of words
    def getCompleteData(self):
        return self.listOfComplete
    
    #this function increases the appropriate number based on the name field for hate/adult
    def increaseNumber(self, title, author, name):
        bookData = self.getBookData(title)
        bookData[name] = bookData[name]+1
        
        authorData = self.getAuthorData(author)
        authorData[name] = authorData[name]+1
        
        completeData = self.getCompleteData()
        completeData[name] = completeData[name]+1
        
    #this function trains and tests over data set for hate and adult
    def trainTestHateAdult(self):
        completeData = self.getCompleteData()
        
        books = self.getBooks()
        
        i = 0;
        
        bookHate = []
        bookAdult = []
        
        while i < len(books):
            bookHate.append(self.getBookData(list(books)[i])["hate"])
            bookAdult.append(self.getBookData(list(books)[i])["adult"])
            i+=1;
        i = 0;
        iterations = 1000;
        hateCorrectPercentage = 0.0;
        adultCorrectPercentage = 0.0;
        while i < iterations:
            
            random.shuffle(bookHate)
            random.shuffle(bookAdult)

            trainHate = bookHate[:50]
            testHate = bookHate[50:]

            trainAdult = bookAdult[:50]
            testAdult = bookAdult[50:]

            adultPercentage = 0.0
            hatePercentage = 0.0

            for num in trainHate:
                if num > 0:
                    hatePercentage+=1
            for num in trainAdult:
                if num > 0:
                    adultPercentage+=1

            hatePercentage = hatePercentage/len(trainHate)
            adultPercentage = adultPercentage/len(trainAdult)

            hateCorrect = 0.0
            adultCorrect = 0.0

            for num in testHate:
                if hatePercentage >= 50 and num > 0:
                    hateCorrect+=1
                elif hatePercentage < 50 and num == 0:
                    hateCorrect+=1
            for num in testAdult:
                if adultPercentage >= 50 and num > 0:
                    adultCorrect+=1
                elif adultPercentage < 50 and num == 0:
                    adultCorrect+=1

            hateCorrect = hateCorrect/len(testHate)
            adultCorrect = adultCorrect/len(testAdult)

            
            hateCorrectPercentage += hateCorrect
            adultCorrectPercentage += adultCorrect
            i+=1;
        
        print("Percentage for "+str(iterations)+" rounds of random split testing")
        print("Hate correct percentage: " + str(round((hateCorrectPercentage/iterations)*100,2))+"%")
        print("Adult correct percentage: " + str(round((adultCorrectPercentage/iterations)*100,2))+"%")
        
    # this function returns the author percentage for every author
    def getAuthorPercentage(self):
        authors = self.authorAmounts
        for author in authors:
            print("Author "+author+" has a " + str(round((authors[author]['hate']/authors[author]['books'])*100.0,2))+"% chance of releasing a Hate book")
            print("Author "+author+" has a " + str(round((authors[author]['adult']/authors[author]['books'])*100.0,2))+"% chance of realeasing a Adult book")
    
    # this function initializes the different amounts for all authors
    def initializeAmountsPerAuthor(self):
        books = self.getBooks()
        authors = {}
        for book in books:
            bookData = self.getBookData(book)
            if not (bookData["author"] in authors):
                authors[bookData["author"]]={"hate":0,"adult":0,"books":0}
            authors[bookData["author"]]["books"]+=1
            if(bookData["hate"] > 0):
                authors[bookData["author"]]["hate"]+=1
            if(bookData["adult"] > 0):
                authors[bookData["author"]]["adult"]+=1
        self.authorAmounts = authors