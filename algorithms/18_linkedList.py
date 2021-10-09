class Node:
    def __init__(self, data = None):
        self.data = data   # actual data that saved in linkedList
        self.next = None   # address to process data
        
class LinkedList:
    def __init__(self):
        self.count = 0     # the number of data saved in linkedList
        self.head = None   # starting point of linkedList

    # 3 ways to write data on linkedList
    # 1. add data on tail of linkedList
    # 2. add data on head of linkedList
    # 3. add data on else


    def appendLast(self, data):
        newNode = Node(data)
        print(newNode)
        self.count += 1
        if self.head is None:  # ask if empty linkedList
            self.head = newNode
            return
        start = self.head
        while start.next:
            start = start.next

        start.next = newNode


    def insertFirst(self, data):
        newNode = Node(data)
        self.count += 1
        newNode.next = self.head
        self.head = newNode


    def insertPosition(self, position, data):
        # inspects if the insertion is appropriate in position. => terminate process if inappropriate.
        if position < 1 or position > self.count - 1:
            print('Position {} is inappropriate for the data {}'.format(position, data))
            return
        newNode = Node(data)
        self.count += 1

        start = self.head
        for i in range(position - 1):
            start = start.next
        nowNode.next = start.next
        start.next = newNode


    def listPrint(self):
        start = self.head
        if start is None:
            print('No data saved in linkedList.')
        else:
            print('{} data saved in linkedList.'.format(self.count))
            for i in range(self.count):
                print(start.data, end=' ')
                # Access on next data
                start = start.next
            print()


    # Function that finds and removes data saved in linkedList
    def remove(self, data):
        start = self.head
        # Check if the linkedList is empty, and remove data in the linkedList
        if start is None:
            print('linkedList is empty. - remove()')
        else:
            # data saved in linkedList exists, find and remove the data.
            # In case of data to remove is 0th index
            if start.data == data:
                # put 1st index data 
                self.head = start.next
                self.count -= 1
                return

        while start is not None:
            if start.data == data:
                break
            prev = start
            start = start.next

        if start == None:
            print('{} does not exist in the linkedList.'.format(data))
            return

        prev.next = start.next
        self.count -= 1



print('Create linkedList.')
linkedList = LinkedList()
linkedList.listPrint()
linkedList.remove('A')
print('=' * 80)

print('Add data next to the head of linkedList.')
linkedList.appendLast('A')
linkedList.listPrint()
print('=' * 80)

print('Add data next to the tail of linkedList.')
linkedList.appendLast('B')
linkedList.listPrint()
linkedList.appendLast('C')
linkedList.listPrint()
linkedList.appendLast('D')
linkedList.listPrint()
print('=' * 80)

linkedList.insertFirst('E')
linkedList.listPrint()


linkedList.insertPosition(0, 'F')
linkedList.listPrint()

print('Remove an index 0 data in linkedList.')
linkedList.remove('A')
print('Remove an more than index 1 data in linkedList.')
print('Trying to remove data doesn\'t exist.')
linkedList.remove('G')
