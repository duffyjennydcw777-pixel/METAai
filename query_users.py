import subprocess
q = """
SELECT u.id, u.first_name, u.username, s.plan, s.status, s.expires_at,
       (SELECT COUNT(*) FROM payments p WHERE p.user_id = u.id AND p.status='succeeded') as paid_count,
       (SELECT COALESCE(SUM(p.amount),0) FROM payments p WHERE p.user_id = u.id AND p.status='succeeded') as total_paid
FROM users u
LEFT JOIN subscriptions s ON s.user_id = u.id AND s.service='vpn'
ORDER BY total_paid ASC, u.id;
"""
result = subprocess.run(
    ['psql', '-h', 'localhost', '-U', 'iron055', '-d', 'iron055', '-t', '-A', '-F', '|', '-c', q],
    capture_output=True, text=True,
    env={"PGPASSWORD": "iron055pass2026", "PATH": "/usr/bin:/usr/local/bin"}
)
print(result.stdout)
if result.stderr:
    print("ERR:", result.stderr)
