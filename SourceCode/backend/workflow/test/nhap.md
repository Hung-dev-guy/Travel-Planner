// Tìm tỉnh và tạo phường 
MATCH (p:Province {name: "Tuyên Quang"})
MERGE (w:Ward {slug: "ha-giang-1"})
ON CREATE SET 
    w.name = "Phường Hà Giang 1"

// Tạo mối quan hệ giữa Tỉnh và Phường
MERGE (p)-[:HAS]->(w)
RETURN p.name, w.name
// Tìm 2 phường
MATCH (w1:Ward {slug: "ha-giang-1"})
MATCH (w2:Ward {slug: "vi-xuyen"})

// Tạo mối quan hệ giữa hai phường
MERGE (w1)-[r:CONNECTED_TO]->(w2)
SET r.distance_km = 20.0
RETURN w1.name, w2.name, r.distance_km

#Tạo slug
MATCH (w:Ward {name: "Gia Lâm"})
SET w.slug = "gia-lam"
RETURN w

# Kiểm tra phường có tồn tại 
MATCH (w:Ward)
WHERE w.name =~ '(?i)Hà Đông'
RETURN w.name AS Name, w.slug AS Slug

# Kiểm tra phường có thuộc tỉnh không
MATCH (w:Ward {name: "Hà Đông"})
MATCH (p:Province {name: "Hà Nội"})
MATCH (p)-[:HAS]->(w)
RETURN w.name, w.slug, p.name AS Province