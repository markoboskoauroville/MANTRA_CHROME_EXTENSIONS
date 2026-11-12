func average(_ xs: [Double]) -> Double? {
    if xs.isEmpty {
        return nil
    }
    let sum = xs.reduce(0, +)
    return sum / Double(xs.count)
}

let result = average([1.0, 2.0, 3.0, 4.0])
if let avg = result {
    print(avg)
} else {
    print("nil")
}
