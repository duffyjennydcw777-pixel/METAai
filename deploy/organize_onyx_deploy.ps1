$base = "C:\Users\Gigabyte\ONYX\deploy"

# Создаём папки
@("scripts","sql","systemd","nginx","ps","archive","data") | ForEach-Object {
    New-Item -ItemType Directory -Path "$base\$_" -Force | Out-Null
}

# SQL
@("activate_server1.sql","add_vpn_server.sql","check_keys.sql","check_missing.sql",
  "emergency_fix.sql","grant_ultra.sql","reset_db_pass.sql",
  "switch_to_server2.sql","update_creds.sql") |
ForEach-Object { if (Test-Path "$base\$_") { Move-Item "$base\$_" "$base\sql\" -Force } }

# SYSTEMD
@("iron055-api.service","onyx-watchdog.service","onyx-watchdog.timer",
  "onyx-watchdog-daily.service","onyx-watchdog-daily.timer") |
ForEach-Object { if (Test-Path "$base\$_") { Move-Item "$base\$_" "$base\systemd\" -Force } }

# NGINX
@("nginx-iron055.conf","nginx.conf") |
ForEach-Object { if (Test-Path "$base\$_") { Move-Item "$base\$_" "$base\nginx\" -Force } }

# DATA
@("cluster_stats.json","template.json") |
ForEach-Object { if (Test-Path "$base\$_") { Move-Item "$base\$_" "$base\data\" -Force } }

# ARCHIVE (one-time fix/debug/reset + logs)
@("debug_forgebot.py","disable_iron.py","fix_db_and_port.py","fix_dupes.py",
  "fix_env.py","fix_env_remote.py","fix_forgebot_2fa.py","fix_meta.py",
  "fix_nginx_landing.py","fix_payment_token.py","fix_stuck_payments.py",
  "fix_sylectus_nginx.py","fix_vpn_expiry.py","fix_vpn_nodes.ps1","fix_wwnnni.py",
  "fix_critical.ps1","reset_forgebot.py","reset_panel.sh","activate_forgebot.py",
  "find_panel.sh","check_panel.sh","check_bot_delivery.ps1","find_dupes.py",
  "iron_audit_output.txt","iron_audit_post.txt","do_auto_fix.py","remote_fix.py",
  "setup_forgebot_vless.py","setup_3proxy.py","add_cluster_to_db.py","cluster_setup.py",
  "create_cherny_key.py","gen_friend_key.py","get_creds.py","get_inbounds.py",
  "get_inbounds_safe.py","get_schema.py","get_settings_keys.py","get_stuck_users.py",
  "get_template.py","get_xui_creds.py","deploy_fix.ps1","run_fix_meta.ps1",
  "run_meta.ps1","run_reminder.ps1","run_schema.ps1") |
ForEach-Object { if (Test-Path "$base\$_") { Move-Item "$base\$_" "$base\archive\" -Force } }

# PS (PowerShell runners)
@("infra_check.ps1","run_audit.ps1","run_xui_audit.ps1","vpn_diag.ps1",
  "vpn_tune.ps1","deploy.ps1","deploy.sh","deploy_fix.ps1") |
ForEach-Object { if (Test-Path "$base\$_") { Move-Item "$base\$_" "$base\ps\" -Force } }

# SCRIPTS - все оставшиеся .py и .sh
Get-ChildItem "$base\*.py","$base\*.sh" | ForEach-Object {
    Move-Item $_.FullName "$base\scripts\" -Force
}

Write-Host ""
Write-Host "Done! Structure:"
Get-ChildItem $base -Directory | ForEach-Object {
    $count = (Get-ChildItem $_.FullName).Count
    Write-Host ("  " + $_.Name + "/ = " + $count + " files")
}
