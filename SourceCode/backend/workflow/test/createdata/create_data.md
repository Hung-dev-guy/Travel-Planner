## Tạo phường 
MATCH (p:Province {name: "Lạng Sơn"})
MERGE (w:Ward {slug: "dong-king-ls"})
ON CREATE SET 
    w.name = "Đông Kinh"
ON MATCH SET 
    w.name = "Đông Kinh"
MERGE (p)-[:HAS]->(w)
RETURN p.name AS Tinh, w.name AS Phuong, w.slug AS Slug

## Tạo khoảng cách
UNWIND [
    {n1: "Kỳ Lừa", n2: "Chi Lăng", dist: 8},
    {n1: "Chi Lăng", n2: "Đồng Đăng", dist: 10},
    {n1: "Đồng Đăng", n2: "Mẫu Sơn", dist: 45},
    {n1: "Mẫu Sơn", n2: "Nhân Lý", dist: 35},
    {n1: "Nhân Lý", n2: "Đông Kinh", dist: 25},
    {n1: "Đông Kinh", n2: "Tam Thanh", dist: 1.5}
] AS rel
MATCH (w1:Ward {name: rel.n1})
MATCH (w2:Ward {name: rel.n2})
MERGE (w1)-[r:CONNECTED_TO]-(w2)
SET r.distance_km = rel.dist;