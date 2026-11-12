import Foundation

func average(_ xs: [Double]) -> Double? {
    guard !xs.isEmpty else { return nil }
    let sum = xs.reduce(0, +)
    return sum / Double(xs.count)
}

let numbers: [Double] = [1, 2, 3, 4]
if let avg = average(numbers) {
    print(avg)
} else {
    print("No average (empty array)")
}
