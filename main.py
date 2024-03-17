from flask import Flask, request, jsonify

app = Flask(__name__)

stocks = {
    'C1': {'A': 3, 'B': 2, 'C': 8},
    'C2': {'D': 12, 'E': 25, 'F': 15},
    'C3': {'G': 0.5, 'H': 1, 'I': 2},
}

graph = {
    'C1': {'C2': 4, 'L1': 3},
    'C2': {'C1': 4, 'C3': 3, 'L1': 2.5},
    'C3': {'C2': 3, 'L1': 2},
    'L1': {'C1': 3, 'C2': 2.5, 'C3': 2}
}


def initialize_weights(data, stocks):
    weights = {'C1': 0, 'C2': 0, 'C3': 0, 'L1': 0}
    for prod, count in data.items():
        if prod in ['A', 'B', 'C']:
            weights['C1'] += count * stocks['C1'][prod]
        elif prod in ['D', 'E', 'F']:
            weights['C2'] += count * stocks['C2'][prod]
        elif prod in ['G', 'H', 'I']:
            weights['C3'] += count * stocks['C3'][prod]
    return weights


def get_cost(weight, distance):
    return (10 + 8 * (weight // 5)) * (distance)


def min_cost(weights):
    min_cost = [float('inf')]

    n = 0
    for c in weights:
        if c:
            n += 1

    visited = set()

    def backtrack(u, prev_weight, total_cost):
        if total_cost >= min_cost[0]:
            return

        if not any(weights.values()):  # all weights become zero => collected all items
            min_cost[0] = min(min_cost[0], total_cost)
            return

        if u != 'L1':
            visited.add(u)
            prev_weight += weights[u]
        else:
            prev_weight = 0

        temp = weights[u]
        weights[u] = 0

        for neigh in graph[u]:
            if neigh == 'L1' or (weights[neigh] != 0 and neigh not in visited):
                backtrack(neigh, prev_weight, total_cost + get_cost(prev_weight, graph[u][neigh]))

        visited.remove(u) if u != 'L1' else None
        weights[u] = temp
        prev_weight -= temp if u != 'L1' else 0

    for u in stocks.keys():
        backtrack(u, 0, 0)
    return min_cost[0]


@app.route('/calculate_cost', methods=['POST'])
def calculate_cost():
    data = request.get_json()

    # Check if data is valid JSON and not empty
    if not data:
        return jsonify({'error': 'Missing data'}), 400

    # Directly use the request data instead of accessing through 'body' key
    weights = initialize_weights(data, stocks)
    result = min_cost(weights)
    return jsonify({'minimum_cost': result})


if __name__ == '__main__':
    app.run(debug=True)
