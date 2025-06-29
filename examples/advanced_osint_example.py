from app.services.advanced_osint_service import (
    hibp_breaches,
    social_searcher_mentions,
    build_relation_graph,
)


if __name__ == "__main__":
    email = "test@example.com"
    hibp_key = "YOUR_HIBP_KEY"
    breaches = hibp_breaches(email, hibp_key)
    print("HIBP breaches:", breaches)

    mentions = social_searcher_mentions("test", "DEMO_KEY")
    print("Mentions found:", len(mentions))

    graph = build_relation_graph([
        {"platform": "twitter", "username": "alice"},
        {"platform": "github", "username": "alice"},
        {"platform": "facebook", "username": "bob"},
    ])
    print("Graph nodes:", graph.number_of_nodes())
    print("Graph edges:", graph.number_of_edges())
