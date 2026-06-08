"#most successful drivers in Formula 1 history based on the number of wins"
SELECT 
    d.forename,
    d.surname,
    COUNT(*) AS wins
FROM results r
JOIN drivers d ON r.driverId = d.driverId
WHERE r.position = 1
GROUP BY r.driverId
ORDER BY wins DESC
LIMIT 10;

"#Most dominant teams"
SELECT 
    c.name,
    COUNT(*) AS wins
FROM results r
JOIN constructors c ON r.constructorId = c.constructorId
WHERE r.position = 1
GROUP BY r.constructorId
ORDER BY wins DESC;

"3. Win rate per driver"
SELECT 
    d.forename,
    d.surname,
    COUNT(CASE WHEN r.position = 1 THEN 1 END) * 1.0 / COUNT(*) AS win_rate
FROM results r
JOIN drivers d ON r.driverId = d.driverId
GROUP BY r.driverId
ORDER BY win_rate DESC;

"4. Average finishing position per driver"
SELECT 
    d.forename,
    d.surname,
    AVG(r.positionOrder) AS avg_finish
FROM results r
JOIN drivers d ON r.driverId = d.driverId
GROUP BY r.driverId
ORDER BY avg_finish ASC;

"5. Drivers with most podiums (Top 3 finishes)"
SELECT 
    d.forename,
    d.surname,
    COUNT(*) AS podiums
FROM results r
JOIN drivers d ON r.driverId = d.driverId
WHERE r.position BETWEEN 1 AND 3
GROUP BY r.driverId
ORDER BY podiums DESC;

"6. Best performing circuits (most competitive races)"
SELECT 
    ci.name,
    AVG(r.positionOrder) AS avg_finish
FROM results r
JOIN races ra ON r.raceId = ra.raceId
JOIN circuits ci ON ra.circuitId = ci.circuitId
GROUP BY ci.circuitId
ORDER BY avg_finish ASC;

"7. Fastest drivers (based on average race time)"
SELECT 
    d.forename,
    d.surname,
    AVG(r.milliseconds) AS avg_time
FROM results r
JOIN drivers d ON r.driverId = d.driverId
WHERE r.milliseconds IS NOT NULL
GROUP BY r.driverId
ORDER BY avg_time ASC;

'8. Grid position vs finishing position (performance delta)'
SELECT 
    d.forename,
    d.surname,
    AVG(r.grid - r.positionOrder) AS avg_positions_gained
FROM results r
JOIN drivers d ON r.driverId = d.driverId
GROUP BY r.driverId
ORDER BY avg_positions_gained DESC;

'9. Drivers who improve the most during races'
SELECT 
    d.forename,
    d.surname,
    MAX(r.grid - r.positionOrder) AS best_race_recovery
FROM results r
JOIN drivers d ON r.driverId = d.driverId
GROUP BY r.driverId
ORDER BY best_race_recovery DESC;

'10. Pit stop frequency by driver'
SELECT 
    d.forename,
    d.surname,
    COUNT(p.pitStopId) AS pitstops
FROM pit_stops p
JOIN drivers d ON p.driverId = d.driverId
GROUP BY p.driverId
ORDER BY pitstops DESC;

'11. Most consistent drivers (low variance proxy)'
SELECT 
    d.forename,
    d.surname,
    AVG(r.positionOrder) AS avg_finish,
    COUNT(*) AS races
FROM results r
JOIN drivers d ON r.driverId = d.driverId
GROUP BY r.driverId
HAVING races > 50
ORDER BY avg_finish ASC;
'12. Top qualifying drivers → race correlation check'
SELECT 
    q.position AS qualifying_pos,
    r.positionOrder AS race_pos
FROM qualifying q
JOIN results r 
ON q.driverId = r.driverId 
AND q.raceId = r.raceId;


'13. Constructors consistency ranking'
SELECT 
    c.name,
    AVG(r.positionOrder) AS avg_finish
FROM results r
JOIN constructors c ON r.constructorId = c.constructorId
GROUP BY r.constructorId
ORDER BY avg_finish ASC;
'14. Best countries (driver nationality success)'
SELECT 
    d.nationality,
    COUNT(CASE WHEN r.position = 1 THEN 1 END) AS wins
FROM results r
JOIN drivers d ON r.driverId = d.driverId
GROUP BY d.nationality
ORDER BY wins DESC;
'15. Race competitiveness (closest finishing races)'
SELECT 
    raceId,
    MAX(positionOrder) - MIN(positionOrder) AS spread
FROM results
GROUP BY raceId
ORDER BY spread ASC;