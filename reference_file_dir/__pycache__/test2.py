# from locale import currency
# from tkinter.messagebox import NO


# class node:
#       def __init__(self):
#             self.prev = None
#             self.data = None
#             self.next = None
      
#       def insert(self, data):
#             self.data = data

# class cal:
#       def __init__(self):
#             self.head_node = node()
#             self.tail_node = node()
#         #    self.node_cnt = 1
      
#       def search(self, data, order):
#             if order == True:
#                   current_node = self.head_node
#                   while(True):
#                         if current_node.data == data:
#                               break

#                         if self.head_node.next ==None:
#                               return "값이 존재하지 않습니다."
                        
#                         current_node = current_node.next


            
#             else:
#                   current_node = self.tail_node
#                   while(True):
#                         if current_node.data == data:
#                               break

#                         if self.head_node.prev ==None:
#                               return "값이 존재하지 않습니다."
                        
#                         current_node = current_node.next


                  
                  

#       def insert(self, num, order):
#             if order == True:
#                   add_node = node()
#                   current_node = self.head_node
#                   for i in range(num):
#                         if current_node.next == None:
#                               return "노드가 존재하지 않습니다.."
#                         current_node = current_node.next
#                   prev_node = current_node.prev
#                   next_node = current_node
#                   add_node.prev = prev_node
#                   add_node.next = next_node
#                   prev_node.next = add_node
#                   next_node.prev = add_node
#             else:
#                   for i in range(num):
#                         current_node = self.tail_node
#                         if current_node.prev == None:
#                               return "노드가 존재하지 않습니다.."
#                         current_node = current_node.prev

def test():
      a = 20
      for i in range(1,a,3):
            if i == 10:
                  return "??"
            print(i)
                  
      print("나옴?")


print(test())
# print(a)
