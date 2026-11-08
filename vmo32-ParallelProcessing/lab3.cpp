#include "lab3.h"
#include <iostream>
#include <thread>
#include <vector>
#include <chrono>

using namespace lab3;
using namespace std;

void test_safe_queue() {
    SafeQueue<int> q;

    thread producer([&]() {
        for (int i = 1; i <= 5; i++) {
            q.push(i);
            cout << "[SafeQueue] push: " << i << endl;
            this_thread::sleep_for(chrono::milliseconds(50));
        }
    });

    thread consumer([&]() {
        for (int i = 1; i <= 5; i++) {
            int val = q.pop();
            cout << "[SafeQueue] pop: " << val << endl;
        }
    });

    producer.join();
    consumer.join();
}

void test_bounded_buffer() {
    BoundedBuffer buf(3);

    thread producer([&]() {
        for (int i = 1; i <= 5; i++) {
            buf.produce(i);
            cout << "[CV] produced: " << i << endl;
            this_thread::sleep_for(chrono::milliseconds(100));
        }
    });

    thread consumer([&]() {
        for (int i = 1; i <= 5; i++) {
            int val = buf.consume();
            cout << "[CV] consumed: " << val << endl;
            this_thread::sleep_for(chrono::milliseconds(150));
        }
    });

    producer.join();
    consumer.join();
}

void test_atomic_buffer() {
    AtomicBuffer buf;

    thread producer([&]() {
        for (int i = 1; i <= 5; i++) {
            buf.produce(i);
            cout << "[Atomic] produced: " << i << endl;
            this_thread::sleep_for(chrono::milliseconds(100));
        }
    });

    thread consumer([&]() {
        int val;
        for (int i = 1; i <= 5;) {
            if (buf.consume(val)) {
                cout << "[Atomic] consumed: " << val << endl;
                i++;
            }
        }
    });

    producer.join();
    consumer.join();
}

void test_reader_writer() {
    SharedData ATM;

    thread transaction1([&]() {
        ATM.add(10);
        cout << "ATM added 10" << endl;
        this_thread::sleep_for(chrono::milliseconds(100));
    });

    thread transaction2([&]() {
        ATM.add(10);
        cout << "ATM added 10" << endl;
        this_thread::sleep_for(chrono::milliseconds(100));
    });

    thread reader1([&]() {
        auto balance = ATM.read();
        cout << "Balance: " << balance << endl;
        this_thread::sleep_for(chrono::milliseconds(80));
    });

    transaction1.join();
    transaction2.join();
    reader1.join();
}

void test_barrier() {
    const int N = 5;
    Barrier barrier(N);

    auto worker = [&](int id) {
        cout << "[Barrier] Thread " << id << " before barrier\n";
        this_thread::sleep_for(chrono::milliseconds(100 * id));

        barrier.wait();

        cout << "[Barrier] Thread " << id << " after barrier\n";
    };

    vector<thread> threads;
    for (int i = 0; i < N; i++)
        threads.emplace_back(worker, i);

    for (auto& t : threads)
        t.join();
}

void test_parallel_reduce() {
    vector<float> data = {1, 2, 3, 4};

    float sum = parallel_reduce(data, 2, true);
    float prod = parallel_reduce(data, 2, false);

    cout << "[Reduce] sum = " << sum << endl;
    cout << "[Reduce] product = " << prod << endl;
}

void run3() {
    cout << "\n==== Reader/Writer ====\n" << endl;
    test_reader_writer();
}


namespace lab3 {

BoundedBuffer::BoundedBuffer(size_t size) : max_size(size) {}

void BoundedBuffer::produce(int value) {
    std::unique_lock<std::mutex> lock(m);
    not_full.wait(lock, [this]() { return buffer.size() < max_size; });

    buffer.push(value);
    not_empty.notify_one();
}

int BoundedBuffer::consume() {
    std::unique_lock<std::mutex> lock(m);
    not_empty.wait(lock, [this]() { return !buffer.empty(); });

    int value = buffer.front();
    buffer.pop();

    not_full.notify_one();
    return value;
}

AtomicBuffer::AtomicBuffer() : ready(false) {}

void AtomicBuffer::produce(int value) {
    {
        std::lock_guard<std::mutex> lock(m);
        buffer.push(value);
    }
    ready.store(true, std::memory_order_release);
}

bool AtomicBuffer::consume(int& value) {
    if (!ready.load(std::memory_order_acquire))
        return false;

    std::lock_guard<std::mutex> lock(m);
    if (buffer.empty())
        return false;

    value = buffer.front();
    buffer.pop();
    ready.store(false, std::memory_order_release);
    return true;
}

SharedData::SharedData() : data(0) {}

void SharedData::write(int value) {
    std::unique_lock<std::shared_mutex> lock(rw_mutex);
    data = value;
}

void SharedData::add(int value) {
    std::unique_lock<std::shared_mutex> lock(rw_mutex);
    data += value;
}

int SharedData::read() const {
    std::shared_lock<std::shared_mutex> lock(rw_mutex);
    return data;
}

Barrier::Barrier(int count_)
    : count(count_), initial(count_), generation(0) {}

void Barrier::wait() {
    std::unique_lock<std::mutex> lock(m);
    int gen = generation;

    if (--count == 0) {
        generation++;
        count = initial;
        cv.notify_all();
    } else {
        cv.wait(lock, [this, gen]() { return gen != generation; });
    }
}

float parallel_reduce(std::vector<float>& data,
                      int num_threads,
                      bool is_sum) {

    Barrier barrier(num_threads);
    std::vector<float> partial(num_threads, 0);

    auto worker = [&](int id) {
        int n = data.size();
        int chunk = n / num_threads;
        int start = id * chunk;
        int end = (id == num_threads - 1) ? n : start + chunk;

        if (is_sum) {
            float sum = 0;
            for (int i = start; i < end; i++)
                sum += data[i];
            partial[id] = sum;
        } else {
            float prod = 1;
            for (int i = start; i < end; i++)
                prod *= data[i];
            partial[id] = prod;
        }

        barrier.wait();

        if (id == 0) {
            float result = is_sum ? 0 : 1;
            for (float val : partial) {
                if (is_sum) result += val;
                else result *= val;
            }
            partial[0] = result;
        }

        barrier.wait();
    };

    std::vector<std::thread> threads;
    for (int i = 0; i < num_threads; i++)
        threads.emplace_back(worker, i);

    for (auto& t : threads)
        t.join();

    return partial[0];
}

} // namespace lab3