# import heapq
#
#
# class Event:
#     def __init__(self, time, count, event_type):
#         self.time = time
#         self.count = count
#         self.event_type = event_type
#
#     def __lt__(self, other):
#         # Comparing float equality here is not really optimal, but the actual game code probably does the same.
#         # Best option would probably be to discretize time and use ints.
#         if self.time != other.time:
#             return self.time < other.time
#         elif self.count != other.count:
#             return self.count < other.count
#         else:
#             raise ValueError(f'__lt__: compared objects have the same time and count')
#
#     def __repr__(self):
#         return f'time={self.time}, count={self.count}, event_type={self.event_type}'
#
#
# # print(Event(0.0, 0, 0) < Event(1.0, 0, 0))
# # print(Event(0.0, 0, 0) < Event(0.0, 1, 0))
# # print(Event(0.0, 0, 0) < Event(0.0, 0, 1))
#
# # event_queue = []
# # heapq.heappush(event_queue, Event(0.0, 1, 0))
# # heapq.heappush(event_queue, Event(1.0, 0, 0))
# # heapq.heappush(event_queue, Event(0.0, 0, 0))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
#
# # event_queue = []
# # heapq.heappush(event_queue, Event(1.0, 1, 0))
# # heapq.heappush(event_queue, Event(0.0, 0, 0))
# # heapq.heappush(event_queue, Event(1.1, 2, 0))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
#
# # Due to what I consider a coincidence, in this simple example, the order comes out right even without calling sort.
# # event_queue = []
# # heapq.heappush(event_queue, Event(1.0, 1, 0))
# # heapq.heappush(event_queue, Event(0.0, 0, 0))
# # event = Event(1.1, 2, 0)
# # heapq.heappush(event_queue, event)
# # event.time = 0.9
# # event_queue.sort()
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
#
# # In this example, there is no coincidence like above and the sort call is mandatory.
# event_queue = []
# event_1 = Event(1.0, 1, 0)
# heapq.heappush(event_queue, event_1)
# event_2 = Event(0.0, 0, 0)
# heapq.heappush(event_queue, event_2)
# event_3 = Event(1.1, 2, 0)
# heapq.heappush(event_queue, event_3)
# event_1.time = 0.8
# event_2.time = 1.0
# event_3.time = 0.9
# event_queue.sort()
# print(heapq.heappop(event_queue))
# print(heapq.heappop(event_queue))
# print(heapq.heappop(event_queue))


import random





for _ in range(10000):
    print(sample_fight_duration(180.0, 20.0))
