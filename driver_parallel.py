from multiprocessing import Pool

import time

work = list(range(0, 999))


def work_log(work_data):
    print(" Process %s waiting %s seconds" + str(work_data))
    for i in range(0, 1000000 * work_data):
        j = i + 1
    print(" Process %s Finished." % work_data)


def pool_handler():
    p = Pool(12)
    p.map(work_log, work)


if __name__ == '__main__':
    pool_handler()