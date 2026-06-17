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

# Tìm phường 
MATCH (w:Ward {name: "Cẩm Phả"})
RETURN w.name, w.slug

# Tìm khoảng cách 
// 1. Dùng WITH để đảm bảo các node được tìm thấy trước khi tìm đường
MATCH (start:Ward) WHERE start.name CONTAINS "Hà Đông"
MATCH (end:Ward) WHERE end.name CONTAINS "Hải Vân"
WITH start, end
MATCH p = shortestPath((start)-[:CONNECTED_TO*..15]-(end))
RETURN p AS Duong_di, 
       reduce(dist = 0, r in relationships(p) | dist + r.distance_km) AS Tong_khoang_cach

MATCH (start:Ward {name: "Hà Đông"})
MATCH (end:Ward {name: "Hải Vân"})
MATCH p = shortestPath((start)-[:CONNECTED_TO*..15]-(end))
WITH p, reduce(dist = 0, r in relationships(p) | dist + r.distance_km) AS total_dist
RETURN total_dist AS Khoang_cach_km, 
       [n in nodes(p) | n.name] AS Lo_trinh