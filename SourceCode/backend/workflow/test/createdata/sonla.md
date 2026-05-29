MATCH (p:Province {name: "Sơn La"})

// 1. Thành phố Sơn La (3 phường)
UNWIND [
    {slug: "xieng-mai-sl", name: "Xiêng Mải", destination: "Nhà tù Sơn La, Bảo tàng Sơn La"},
    {slug: "chieng-le-sl", name: "Chiềng Lề", destination: "Suối nước nóng bản Mòng"},
    {slug: "son-la-sl", name: "Sơn La", destination: ""}
] AS ward
MERGE (w:Ward {slug: ward.slug})
ON CREATE SET w.name = ward.name, w.tourist_destination = ward.destination
ON MATCH SET w.name = ward.name, w.tourist_destination = ward.destination
MERGE (p)-[:HAS]->(w)

// 2. Huyện Mộc Châu (2 phường + 5 xã)
UNWIND [
    {slug: "moc-chau-sl", name: "Mộc Châu", destination: "Cao nguyên Mộc Châu, Đồi chè Mộc Châu, Thác Dải Yếm, Happy Land, Cầu mây"},
    {slug: "do-son-sl", name: "Đồ Sơn", destination: "Rừng thông Bản Áng, Hang Dơi"},
    {slug: "chieng-hac-sl", name: "Chiềng Hắc", destination: "Ruộng bậc thang Mộc Châu, Thung lũng Mường La"},
    {slug: "tan-hop-sl", name: "Tân Hợp", destination: "Thác Bạc"},
    {slug: "dan-thau-sl", name: "Danh Thầu", destination: "Đồi hoa tam giác mạch"},
    {slug: "chieng-son-sl", name: "Chiềng Sơn", destination: "Đỉnh Pha Luông, Ruộng bậc thang"}
] AS ward2
MERGE (w2:Ward {slug: ward2.slug})
ON CREATE SET w2.name = ward2.name, w2.tourist_destination = ward2.destination
ON MATCH SET w2.name = ward2.name, w2.tourist_destination = ward2.destination
MERGE (p)-[:HAS]->(w2)

// 3. Huyện Sông Mã (1 xã)
UNWIND [
    {slug: "ta-xua-sl", name: "Tà Xùa", destination: "Tà Xùa, Sống lưng khủng long, Cây cô đơn, Thảo nguyên Tà Xùa, Hang Táu"}
] AS ward3
MERGE (w3:Ward {slug: ward3.slug})
ON CREATE SET w3.name = ward3.name, w3.tourist_destination = ward3.destination
ON MATCH SET w3.name = ward3.name, w3.tourist_destination = ward3.destination
MERGE (p)-[:HAS]->(w3)

// 4. Huyện Mường La (6 xã)
UNWIND [
    {slug: "it-ong-sl", name: "Ít Ong", destination: "Thủy điện Sơn La, Lòng hồ thủy điện Sơn La"},
    {slug: "ngoc-chien-sl", name: "Ngọc Chiến", destination: "Bản Lướt, Suối nước nóng bản Lướt, Cây samu nghìn năm, Lễ hội hoa sơn tra, Lễ hội Mừng cơm mới"},
    {slug: "muong-trai-sl", name: "Mường Trai", destination: "Du lịch nghỉ dưỡng sinh thái lòng hồ, Nuôi cá tầm sông Đà"},
    {slug: "hua-trai-sl", name: "Hua Trai", destination: "Du lịch cộng đồng bản làng"},
    {slug: "chieng-lao-sl", name: "Chiềng Lao", destination: "Du lịch cộng đồng, Lễ hội Nàng Han, Lễ hội đua thuyền"},
    {slug: "nam-hoat-sl", name: "Nậm Hoạt", destination: "Hang Dơi"}
] AS ward4
MERGE (w4:Ward {slug: ward4.slug})
ON CREATE SET w4.name = ward4.name, w4.tourist_destination = ward4.destination
ON MATCH SET w4.name = ward4.name, w4.tourist_destination = ward4.destination
MERGE (p)-[:HAS]->(w4)

RETURN p.name AS Tinh, count(DISTINCT w) + count(DISTINCT w2) + count(DISTINCT w3) + count(DISTINCT w4) AS TongSoPhuongXa;




UNWIND [
    {from: "moc-chau-sl", to: "viet-tri-pt", dist: 200}
] AS row
MATCH (w1:Ward {slug: row.from})
MATCH (w2:Ward {slug: row.to})
MERGE (w1)-[r:CONNECTED_TO]-(w2)
SET r.distance_km = toFloat(row.dist)
RETURN w1.name, w2.name, r.distance_km