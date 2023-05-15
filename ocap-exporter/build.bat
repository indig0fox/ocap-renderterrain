$ENV:GOARCH = 386
$ENV:CGO_ENABLED = 1
go build -o ocap_exporter.dll -buildmode=c-shared .

$ENV:GOARCH = "amd64"
$ENV:CGO_ENABLED = 1
go1.16.4 build -o ocap_exporter_x64.dll -buildmode=c-shared .