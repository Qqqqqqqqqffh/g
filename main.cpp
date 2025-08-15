
#include <algorithm>
#include <vector>
#include <chrono>
#include <iostream>

int main() {
    std::vector<int> arr = {5, 3, 8, 4, 2};
    auto start = std::chrono::high_resolution_clock::now();

    // Пузырьковая сортировка
    for (size_t i = 0; i < arr.size(); ++i) {
        for (size_t j = 0; j < arr.size() - i - 1; ++j) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
            }
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    std::cout << "Sorted array: ";
    for (int x : arr) std::cout << x << " ";
    std::cout << "\nExecution time: " << duration.count() << " seconds\n";

    return 0;
}
