from concurrent.futures import ThreadPoolExecutor


def _stream_node(node_id: str, chunks: list[str]) -> list[tuple[str, str]]:
    return [(node_id, chunk) for chunk in chunks]


def parallel_streaming_with_node_id_preservation() -> dict:
    nodes = {
        "parallel_node_1": ["node1-chunk1", "node1-chunk2", "node1-chunk3"],
        "parallel_node_2": ["node2-chunk1", "node2-chunk2", "node2-chunk3"],
    }
    outputs: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(_stream_node, node_id, chunks) for node_id, chunks in nodes.items()]
        for future in futures:
            outputs.extend(future.result())

    node_counts: dict[str, int] = {}
    for node_id, _ in outputs:
        node_counts[node_id] = node_counts.get(node_id, 0) + 1
    return {"total_chunks": len(outputs), "node_counts": node_counts, "outputs": outputs}


def main() -> None:
    print(parallel_streaming_with_node_id_preservation())


if __name__ == "__main__":
    main()
