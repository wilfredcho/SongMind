class Node(object):
    def __init__(self, value, next=None):
        self.value = value
        self.next = next


class LinkedList(object):
    def __init__(self, sequence):
        self.head = Node(sequence[0])
        current = self.head
        for item in sequence[1:]:
            current.next = Node(item)
            current = current.next
