from __future__ import annotations

import csv
import heapq
from typing import Any


class _Vertex:
    """A vertex in a graph."""
    item: Any
    neighbours: dict[_Vertex, int]  # Stores neighbors with weights

    def __init__(self, item: Any) -> None:
        """Initialize a new vertex with the given item."""
        self.item = item
        self.neighbours = {}


class Graph:
    """A graph data structure."""
    _vertices: dict[Any, _Vertex]
    popularity: dict[Any, int]  # Store popularity of each anime

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._vertices = {}
        self.popularity = {}

    def add_vertex(self, item: Any, popularity: int) -> None:
        """Add a vertex with the given item and store its popularity."""
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item)
            self.popularity[item] = popularity  # Store popularity

    def add_edge(self, item1: Any, item2: Any, weight: int) -> None:
        """Add a weighted edge between two vertices."""
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight

    def find_closest_anime(self, start: Any) -> Any:
        """Find the closest anime recommendation using Dijkstra's algorithm with popularity as a tiebreaker."""
        if start not in self._vertices:
            print("Anime not found in the dataset.")
            return None

        pq = [(0, start)]  # Priority queue with (distance, anime_id)
        distances = {vertex: float('inf') for vertex in self._vertices}
        distances[start] = 0
        visited = set()

        while pq:
            current_distance, current_anime = heapq.heappop(pq)

            if current_anime in visited:
                continue

            visited.add(current_anime)

            for neighbour, weight in self._vertices[current_anime].neighbours.items():
                if neighbour.item not in visited:
                    new_distance = current_distance + weight
                    if new_distance < distances[neighbour.item]:
                        distances[neighbour.item] = new_distance
                        heapq.heappush(pq, (new_distance, neighbour.item))

        # Find the closest anime with the shortest weighted distance
        closest_anime_candidates = []
        min_distance = float('inf')

        for anime, distance in distances.items():
            if anime != start and distance < min_distance:
                min_distance = distance
                closest_anime_candidates = [anime]
            elif anime != start and distance == min_distance:
                closest_anime_candidates.append(anime)

        # If multiple anime have the same closeness, return the most popular one (excluding popularity = 0)
        closest_anime_candidates = []
        min_distance = float('inf')

        for anime, distance in distances.items():
            if anime != start and distance < min_distance:
                min_distance = distance
                closest_anime_candidates = [anime]
            elif anime != start and distance == min_distance:
                closest_anime_candidates.append(anime)

        # Use a popularity similarity window (±1000 by default)
        original_popularity = self.popularity.get(start, float('inf'))
        popularity_window = 100

        filtered_candidates = [
            anime for anime in closest_anime_candidates
            if abs(self.popularity.get(anime, float('inf')) - original_popularity) <= popularity_window
        ]

        if filtered_candidates:
            return min(
                filtered_candidates,
                key=lambda anime: self.popularity.get(anime, float('inf'))
            )

        return None


def build_anime_graph(csv_filename: str) -> tuple[Graph, dict[str, str], dict[str, tuple]]:
    """Read AnimeList.csv and build a graph with weighted edges."""
    anime_graph = Graph()
    anime_data = {}
    genre_to_anime = {}
    studio_to_anime = {}
    title_to_id = {}

    with open(csv_filename, encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            anime_id = row["anime_id"]
            title = row["title"]
            title_english = row["title_english"]
            title_japanese = row["title_japanese"]
            title_synonyms = row["title_synonyms"].split(", ") if row["title_synonyms"] else []
            genres = row["genre"].split(", ") if row["genre"] else []
            studio = row["studio"]
            related = row["related"].split(", ") if row["related"] else []
            popularity = int(row["popularity"]) if row["popularity"].isdigit() else float('inf')

            anime_graph.add_vertex(anime_id, popularity)
            anime_data[anime_id] = (title, genres, studio, related)

            # Normalize and store titles (including official and alternative titles)
            normalized_titles = [title, title_english, title_japanese] + title_synonyms
            for norm_title in normalized_titles:
                normalized_title = norm_title.strip().lower()  # Ensure case-insensitive comparison
                title_to_id[normalized_title] = anime_id

            for genre in genres:
                if genre not in genre_to_anime:
                    genre_to_anime[genre] = set()
                genre_to_anime[genre].add(anime_id)

            if studio:
                if studio not in studio_to_anime:
                    studio_to_anime[studio] = set()
                studio_to_anime[studio].add(anime_id)

        # Build edges between anime in the same genre or studio
        for anime_list in genre_to_anime.values():
            anime_list = list(anime_list)
            for i in range(len(anime_list)):
                for j in range(i + 1, len(anime_list)):
                    anime_graph.add_edge(anime_list[i], anime_list[j], 2)

        for anime_list in studio_to_anime.values():
            anime_list = list(anime_list)
            for i in range(len(anime_list)):
                for j in range(i + 1, len(anime_list)):
                    anime_graph.add_edge(anime_list[i], anime_list[j], 3)

        # Add related anime as edges
        for anime_id, (_, _, _, related) in anime_data.items():
            for related_anime in related:
                if related_anime in anime_data:
                    anime_graph.add_edge(anime_id, related_anime, 1)

    return anime_graph, title_to_id, anime_data


if __name__ == "__main__":
    csv_file = "CleanedAnimeList.csv"  # Update with actual path
    anime_graph, title_to_id, anime_data = build_anime_graph(csv_file)

    anime_name = input("Enter an anime name for recommendations: ").strip().lower()

    while anime_name not in title_to_id:
        anime_name = (input("Anime not found in the dataset. Please check for spelling or enter a different anime: ")
                      .strip().lower())

    closest_anime_id = anime_graph.find_closest_anime(title_to_id[anime_name])
    if closest_anime_id:
        print(f"Recommended Anime: {anime_data[closest_anime_id][0]}")
    else:
        print("No recommendations found.")

    exit()
