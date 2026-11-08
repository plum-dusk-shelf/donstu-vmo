#ifndef PCDA_LAB3_H
#define PCDA_LAB3_H

#include <queue>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <vector>
#include <atomic>
#include <shared_mutex>

void run3();

namespace lab3 {

template<typename T>
class SafeQueue {
private:
    std::queue<T> q;
    std::mutex m;
    std::condition_variable cv;

public:
    void push(const T& value) {
        {
            std::lock_guard<std::mutex> lock(m);
            q.push(value);
        }
        cv.notify_one();
    }

    T pop() {
        std::unique_lock<std::mutex> lock(m);
        cv.wait(lock, [this]() { return !q.empty(); });

        T value = q.front();
        q.pop();
        return value;
    }

    bool empty() {
        std::lock_guard<std::mutex> lock(m);
        return q.empty();
    }
};

class BoundedBuffer {
private:
    std::queue<int> buffer;
    std::mutex m;
    std::condition_variable not_full, not_empty;
    size_t max_size;

public:
    explicit BoundedBuffer(size_t size);

    void produce(int value);
    int consume();
};

class AtomicBuffer {
private:
    std::queue<int> buffer;
    std::mutex m;
    std::atomic<bool> ready;

public:
    AtomicBuffer();

    void produce(int value);
    bool consume(int& value);
};

class SharedData {
private:
    int data;
    mutable std::shared_mutex rw_mutex;

public:
    SharedData();

    void write(int value);
    void add(int value);
    int read() const;
};

class Barrier {
private:
    std::mutex m;
    std::condition_variable cv;
    int count;
    int initial;
    int generation;

public:
    explicit Barrier(int count_);
    void wait();
};

float parallel_reduce(std::vector<float>& data,
                      int num_threads,
                      bool is_sum);

} // namespace lab3

#endif