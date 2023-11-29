from operator import itemgetter
import random
import time
import math
import json

class Similarity:

    def __init__(self):
        self.frozenset_list = list()
        self.number_of_documents = 0
        self.number_of_words = 0
        self.number_of_counters = 0
        self.num = 0  # number given by user
        self.k = 0
        self.sig_matrix = None
        self.file_to_open = ''

    def my_read_data_routine(self):

        f = open(self.file_to_open, "r")

        self.number_of_documents = int(f.readline())
        self.number_of_words = int(f.readline())
        self.number_of_counters = int(f.readline())
        if self.num > self.number_of_documents:
            print("Number entered is greater than total number of documents, terminating...")
            exit()

        temp_list = list()
        self.frozenset_list.clear() # if called again for different file
        for i in range(0, self.num):

            line = f.readline().split(" ")

            while (int(line[0]) - 1) == i:
                # append to temp_list()
                temp_list.append(int(line[1]))
                line = f.readline().split(" ")
                if line == [""]:
                    break

            # create frozenset() from temp_list()
            self.frozenset_list.append(frozenset(temp_list))
            temp_list = list()
            # append the first id if we exit the while loop
            if line != [""]:
                temp_list.append(int(line[1]))

    def slow_my_jac_sim_with_sets(self, doc1_id, doc2_id) -> float:  # naive implementation (for comparison)
        if not (1 <= doc1_id <= self.num) or not (
                1 <= doc2_id <= self.num):
            return -1

        len1 = len(self.frozenset_list[doc1_id - 1])
        len2 = len(self.frozenset_list[doc2_id - 1])

        intersection_counter = 0
        for word_id_1 in self.frozenset_list[doc1_id - 1]:
            for word_id_2 in self.frozenset_list[doc2_id - 1]:
                if word_id_1 == word_id_2:
                    intersection_counter += 1

        union_counter = len1 + len2 - intersection_counter

        return float(intersection_counter / union_counter)

    def my_jac_sim_with_ordered_lists(self, doc1_id, doc2_id) -> float:  # only used in testing to show how slow it is
        if not (1 <= doc1_id <= self.num) or not (
                1 <= doc2_id <= self.num):
            return -1
        l1 = sorted(self.frozenset_list[doc1_id - 1])
        l2 = sorted(self.frozenset_list[doc2_id - 1])

        intersection_counter = 0

        pos1 = 0
        pos2 = 0

        len1 = len(l1)
        len2 = len(l2)

        while pos1 < len1 and pos2 < len2:
            if l1[pos1] == l2[pos2]:
                intersection_counter += 1
                pos1 += 1
                pos2 += 1
            else:
                if l1[pos1] < l2[pos2]:
                    pos1 += 1
                else:
                    pos2 += 1

        union_counter = len1 + len2 - intersection_counter

        return float(intersection_counter / union_counter)

    # smart way to do it
    def fast_jac_sim_with_sets(self, doc1_id, doc2_id) -> float:  # (int, int) use the power of sets
        if not (1 <= doc1_id <= self.num) or not (
                1 <= doc2_id <= self.num):
            return -1

        intersection_counter = len((self.frozenset_list[doc1_id - 1]).intersection(self.frozenset_list[doc2_id - 1]))

        len1 = len(self.frozenset_list[doc1_id - 1])
        len2 = len(self.frozenset_list[doc2_id - 1])

        union_counter = len1 + len2 - intersection_counter

        return float(intersection_counter / union_counter)

    def create_rows_list(self):

        words_list = [[] for x in range(0,self.number_of_words)]  # the word list (id is the position in the array)

        for i in range(0, self.num):
            for wordId in self.frozenset_list[i]:
                words_list[wordId-1].append(i)  # because wordid >= 1

        return words_list

    def my_min_hash(self):
        start = time.time()
        rows_list = self.create_rows_list()
        random_hash_functions_list = list()
        self.sig_matrix = [[float('inf') for i in range(0, self.k)] for j in range(0, len(self.frozenset_list))]

        for i in range(0, self.k):
            h = self.create_random_hash_function()
            random_hash = {x: h(x) for x in range(self.number_of_words)}
            my_hash_keys_ordered_by_values = sorted(random_hash, key=random_hash.get)
            my_hash = {my_hash_keys_ordered_by_values[x]: x for x in range(self.number_of_words)}
            random_hash_functions_list.append(my_hash)
        for row in range(0, len(rows_list)):  # the number of all the words
            for col in rows_list[row]:  # this is different because now we don't check for ones or zeroes
                for i in range(0, len(random_hash_functions_list)):  # for every hash function
                    if random_hash_functions_list[i][row] < self.sig_matrix[col][i]:
                        self.sig_matrix[col][i] = random_hash_functions_list[i][row]
        end = time.time()
        print(f"min hash took: {end - start} seconds")
        return self.sig_matrix

    '''
    Just an experiment please ignore
    def new_min_hash(self):
        rows_list = self.create_rows_list()
        random_hash_functions_list = list()
        self.sig_matrix = [[float('inf') for i in range(0, self.k)] for j in range(0, len(self.frozenset_list))]

        for i in range(0, self.k):
            h = self.create_random_hash_function()
            random_hash = {x: h(x) for x in range(self.number_of_words)}
            my_hash_keys_ordered_by_values = sorted(random_hash, key=random_hash.get)
            my_hash = {my_hash_keys_ordered_by_values[x]: x for x in range(self.number_of_words)}
            random_hash_functions_list.append(my_hash)
        row_count = 0

        for h in range(0, len(random_hash_functions_list)):  # for every hash function
            for i in range(0, self.number_of_words):  # or len(hash) i is the initial position
                # to_check = hash[i] hash[i] is i after the randomization
                check_row = random_hash_functions_list[h][i]  # check_row is i after randomization
                for j in range(len(rows_list[check_row])):  # look at the row the hash points at and traverse it
                    doc_id = rows_list[check_row][j]  # the doc id for the M matrix
                    if self.sig_matrix[doc_id][h] == float('inf'):  # K times N
                        self.sig_matrix[doc_id][h] = i  # the initial position
                        row_count += 1
                        #print(row_count)
                    if row_count == self.num:  # if the row == number of documents is full              SOMETHING HERE
                        #print("breaking")
                        break
                else:
                    continue
                break
            row_count = 0 #for signature matrix
        # print(sig_matrix)
        return self.sig_matrix
    '''
    def create_random_hash_function(self,p=2**33-355, m=2**32-1):
        a = random.randint(1, p - 1)
        b = random.randint(0, p - 1)
        return lambda x: 1 + (((a * x + b) % p) % m)

    def my_sig_sim(self, docid1, docid2, num_of_permutations):

        docid1 = docid1 - 1
        docid2 = docid2 - 1
        signature1 = self.sig_matrix[docid1]
        signature2 = self.sig_matrix[docid2]

        # lengths should be equal
        sigL1 = num_of_permutations  # == sigL2

        intersection = 0
        for i in range(0, num_of_permutations):

            if signature1[i] == signature2[i]:
                intersection += 1

        union = sigL1 - intersection
        return float(intersection / sigL1)

    def brute_force_sig_sim(self,num_of_permutations):
        start = time.time()
        if num_of_permutations < 1 or num_of_permutations > self.k:
            print("number of permutations in brute force is out of bounds")
            exit()
        doc_sim_dict = {docid: [] for docid in range(1, self.num+1)}
        for docid1 in range(1, self.num+1):
            for docid2 in range(docid1+1, self.num+1):
                temp = 1-self.my_sig_sim(docid1, docid2, num_of_permutations)
                doc_sim_dict[docid1].append([docid2, temp])
                doc_sim_dict[docid2].append([docid1, temp])

        for x in doc_sim_dict:
            doc_sim_dict[x] = sorted(doc_sim_dict[x], key=itemgetter(1), reverse=False)

        print("starting similarity check")

        sum2 = 0
        for i in range(1,self.num+1):
            sum1 = 0
            for x in doc_sim_dict[i]:
                sum1 += 1-x[1]

            sum1 = float(sum1/self.num)
            sum2 += sum1
        total = sum2 / self.num
        print(f"average similarity {total}")
        end = time.time()
        print(f"brute force sig sim took: {end - start} seconds")
        return doc_sim_dict

    def brute_force_jac_sim(self):
        start = time.time()
        doc_sim_dict = {docid: [] for docid in range(1, self.num+1)}
        for docid1 in range(1, self.num+1):
            for docid2 in range(docid1+1, self.num+1):
                    temp = 1-self.fast_jac_sim_with_sets(docid1, docid2)
                    doc_sim_dict[docid1].append([docid2, temp])
                    doc_sim_dict[docid2].append([docid1, temp])

        for x in doc_sim_dict:
            doc_sim_dict[x] = sorted(doc_sim_dict[x], key=itemgetter(1), reverse=False)

        print("starting similarity check")

        sum2 = 0
        for i in range(1, self.num+1):
            sum1 = 0
            for x in doc_sim_dict[i]:
                sum1 += 1-x[1]
            sum1 = float(sum1 / self.num)
            sum2 += sum1
        total = sum2 / self.num
        print(f"average similarity {total}")
        end = time.time()
        print(f"brute force took: {end - start} seconds")
        return doc_sim_dict

    def lsh(self, rowsPerBands):
        start = time.time()
        num_bands = math.floor((self.k)/rowsPerBands)
        s = (1/num_bands)**(1/rowsPerBands)
        print(f"Threshold is {s}")
        lsh_dicts = []

        h2 = self.create_random_hash_function()
        for b in range(num_bands): #for every band
            lsh_dicts.append({})
            for i in range(self.num): #for every file
                h1 = hash(tuple(self.sig_matrix[i][rowsPerBands*b:rowsPerBands*(b+1)]))
                lsh_dicts[b][i+1] = h2(h1)
            lsh_dicts[b] = {k: v for k, v in sorted(lsh_dicts[b].items(), key=lambda item: item[1])}
            lsh_dicts[b] = list(lsh_dicts[b].items())
            #print(LSHdicts[b])

        neighbor = {i:list() for i in range(1,self.num+1)}
        seen_neighbor_set = {i:set() for i in range(1,self.num+1)}
        for lista in lsh_dicts:
            for i in range(self.num): #for every file
                for j in range(i + 1, self.num):
                    if lista[i][1] != lista[j][1]:
                        break
                    if lista[i][0] in seen_neighbor_set[lista[j][0]]:
                        continue

                    temp = self.fast_jac_sim_with_sets(lista[i][0], lista[j][0])

                    if temp>=s:
                        neighbor[lista[i][0]].append([lista[j][0], 1-temp])
                        neighbor[lista[j][0]].append([lista[i][0], 1-temp])

                        seen_neighbor_set[lista[i][0]].add(lista[j][0])
                        seen_neighbor_set[lista[j][0]].add(lista[i][0])

        for x in neighbor:
            neighbor[x] = sorted(neighbor[x], key=itemgetter(1), reverse=False)

        sum2 = 0
        for i in range(1, self.num + 1):
            sum1 = 0
            for x in neighbor[i]: # x is list
                sum1 += 1-x[1]

            sum1 = float(sum1 / self.num)
            sum2 += sum1
        total = sum2 / self.num
        print(f"average similarity {total}")
        end = time.time()
        print(f"lsh took: {end - start} seconds")
        return neighbor


    def lsh_signature_check(self, rowsPerBands):
        start = time.time()
        num_bands = math.floor((self.k)/rowsPerBands)
        s = (1/num_bands)**(1/rowsPerBands)
        print(s)
        lsh_dicts = []

        h2 = self.create_random_hash_function()
        for b in range(num_bands): #for every band
            lsh_dicts.append({})
            for i in range(self.num): #for every file
                h1 = hash(tuple(self.sig_matrix[i][rowsPerBands*b:rowsPerBands*(b+1)]))
                lsh_dicts[b][i+1] = h2(h1)
            lsh_dicts[b] = {k: v for k, v in sorted(lsh_dicts[b].items(), key=lambda item: item[1])}
            lsh_dicts[b] = list(lsh_dicts[b].items()) #actually a list
            #print(LSHdicts[b])

        neighbor = {i:list() for i in range(1,self.num+1)}
        seen_neighbor_set = {i:set() for i in range(1,self.num+1)}
        for lista in lsh_dicts:
            for i in range(self.num): #for every file
                for j in range(i + 1, self.num):
                    if lista[i][1] != lista[j][1]:
                        break
                    if lista[i][0] in seen_neighbor_set[lista[j][0]]:
                        continue

                    temp = self.my_sig_sim(lista[i][0], lista[j][0],self.k)

                    if temp>=s:
                        neighbor[lista[i][0]].append([lista[j][0], 1-temp])
                        neighbor[lista[j][0]].append([lista[i][0], 1-temp])

                        seen_neighbor_set[lista[i][0]].add(lista[j][0])
                        seen_neighbor_set[lista[j][0]].add(lista[i][0])

        for x in neighbor:
            neighbor[x] = sorted(neighbor[x], key=itemgetter(1), reverse=False)


        sum2 = 0
        for i in range(1, self.num + 1):
            sum1 = 0
            for x in neighbor[i]: # x is list
                sum1 += 1-x[1]

            sum1 = float(sum1 / self.num)
            sum2 += sum1
        total = sum2 / self.num
        print(f"average similarity {total}")
        end = time.time()
        print(f"lsh sig took: {end - start} seconds")
        return neighbor

    def compare_one_with_all(self, docid1):
        a_list = []
        for docid2 in range(1, self.num + 1):
            sim = self.fast_jac_sim_with_sets(docid1, docid2)
            a_list.append([docid2, sim])
        # for lists in a_list:
        new_list = sorted(a_list, key=itemgetter(1), reverse=True)
        print(new_list)




sim = Similarity()
sim.file_to_open = "DATA_1-docword.enron.txt" # document to open
sim.k = 128 # hash function number
sim.num = 39861 # document number
print("reading data...")
sim.my_read_data_routine()
print("calculating signature matrix...")
sim.my_min_hash()
print("calculating lsh...")
doc_sim_dict = sim.lsh(4)

with open('enron_similarity_dictionary.json', 'w') as convert_file:
    convert_file.write(json.dumps(doc_sim_dict))



''' CLI IMPLEMENTATION 
if __name__ == "__main__":

    random.seed(23452664345345345)  # this is useful for predictable results

    sim = Similarity()

    doc_sim_dict = None
    neighbor = None

    while True:
        sim.num = int(input("Enter number of documents: "))  # number of documents given by the user
        sim.k = int(input("Enter number of permutations: "))  # number of permutations
        sim.file_to_open = str(input("Enter file to open: "))  # the file
        sim.my_read_data_routine()
        option = int(input(f"1: brute force Jaccard Similarity\n2: brute force signature similarity"
                           f"\n3: lsh with Jaccard similarity"
              f"\n4: lsh with signature similarity\n5: test sig and jac similarity functions for two docid\n> "))
        if option != 1:

            sim.my_min_hash()

        if option == 1:

            doc_sim_dict = sim.brute_force_jac_sim()

        elif option == 2:

            new_k = int(input("insert number of permutations (smaller or equal to the original number of permutations): "))
            doc_sim_dict = sim.brute_force_sig_sim(new_k)

        elif option == 3:

            line_number = int(input("give the line number l (k/l must be an integer value): "))
            neighbor = sim.lsh(line_number)

        elif option == 4:

            line_number = int(input("give the line number l (k/l must be an integer value): "))
            neighbor = sim.lsh_signature_check(line_number)

        elif option == 5:

            docid1 = int(input("enter first docid (1..maxNumberOfDocuments)"))
            docid2 = int(input("enter second docid (1..maxNumberOfDocuments)"))
            perm = int(input("enter number of permutations for my_sig_sim"))
            print(f"slow jaccard result: {sim.slow_my_jac_sim_with_sets(docid1,docid2)}")
            print(f"fast jaccard result: {sim.fast_jac_sim_with_sets(docid1,docid2)}")
            print(f"signature result: {sim.my_sig_sim(docid1,docid2,perm)}")
        option2 = str(input("Do you want to print the neighbors of a specific doc_id?(Y/N): "))
        if option2.upper() == "Y":
            key = int(input("Please enter a doc_id key for the dictionary: "))
            if doc_sim_dict is None and neighbor is None:
                print("neighbor dictionary was not created, exiting...")
            elif doc_sim_dict is None and neighbor is not None:
                print(f"{key}:{neighbor[key]}")
            elif doc_sim_dict is not None and neighbor is None:
                print(f"{key}:{doc_sim_dict[key]}")

        option2 = str(input("Do you want to print Neighbor dictionary?(Y/N)(should be dumped in a file honestly): "))
        if option2.upper() == "Y":
            if doc_sim_dict is None and neighbor is None:
                print("neighbor dictionary was not created, exiting...")
            elif doc_sim_dict is None and neighbor is not None:
                for key in neighbor:  # this prints everything
                    print(f"{key}:{neighbor[key]}")
            elif doc_sim_dict is not None and neighbor is None:
                for key in doc_sim_dict:  # this prints everything
                    print(f"{key}:{doc_sim_dict[key]}")

        elif option2.upper() == "N":
            pass

        should_exit = str(input("Do you wish to exit?(Y/N): "))
        if should_exit.upper() == "Y":
            exit()
'''







