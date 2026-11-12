func average(_ xs: [Double]) -> Double? {
    guard !xs.isEmpty else { return nil }
    return xs.reduce(0, +) / Double(xs.count)
}

guard let result = average([1, 2, 3, 4]) else {
    print("No average")
} else {
    print(result)
}
