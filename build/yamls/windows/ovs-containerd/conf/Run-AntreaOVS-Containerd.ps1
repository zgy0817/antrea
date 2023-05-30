$ErrorActionPreference = "Stop"
$mountPath = $env:CONTAINER_SANDBOX_MOUNT_POINT
$mountPath = ($mountPath.Replace('\', '/')).TrimEnd('/')
$newPath = $env:PATH + ";$mountPath/Windows/System32;$mountPath/openvswitch/usr/bin;$mountPath/openvswitch/usr/sbin"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "User")
$OVS_DB_SCHEMA_PATH = "$mountPath/openvswitch/usr/share/openvswitch/vswitch.ovsschema"
$OVSInstallDir = "C:\openvswitch"
$OVS_DB_PATH = "$OVSInstallDir\etc\openvswitch\conf.db"
if ($(Test-Path $OVS_DB_SCHEMA_PATH) -and !$(Test-Path $OVS_DB_PATH)) {
    ovsdb-tool create "$OVS_DB_PATH" "$OVS_DB_SCHEMA_PATH"
}
ovsdb-server $OVS_DB_PATH -vfile:info --remote=punix:db.sock --log-file=/var/log/antrea/openvswitch/ovsdb-server.log --pidfile --detach
ovs-vsctl --no-wait init

# Set OVS version.
$OVS_VERSION=$(Get-Item $mountPath\openvswitch\driver\OVSExt.sys).VersionInfo.ProductVersion
ovs-vsctl --no-wait set Open_vSwitch . ovs_version=$OVS_VERSION

ovs-vswitchd --log-file=/var/log/antrea/openvswitch/ovs-vswitchd.log --pidfile -vfile:info --detach

$SleepInterval = 30
while ($true) {
    if ( !( Get-Process ovsdb-server ) ) {
        ovsdb-server $OVS_DB_PATH -vfile:info --remote=punix:db.sock --log-file=/var/log/antrea/openvswitch/ovsdb-server.log --pidfile --detach
    }
    if ( !( Get-Process ovs-vswitchd ) ) {
        ovs-vswitchd --log-file=/var/log/antrea/openvswitch/ovs-vswitchd.log --pidfile -vfile:info --detach
    }
    Start-Sleep -Seconds $SleepInterval
}
