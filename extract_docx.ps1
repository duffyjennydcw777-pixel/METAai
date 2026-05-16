Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead('C:\Users\Gigabyte\Downloads\Phone Link\ai_product_strategy_session.docx')
$entry = $zip.Entries | Where-Object { $_.FullName -eq 'word/document.xml' }
$stream = $entry.Open()
$reader = New-Object System.IO.StreamReader($stream)
$xml = [xml]$reader.ReadToEnd()
$reader.Close()
$stream.Close()
$zip.Dispose()

$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')

$paragraphs = $xml.SelectNodes('//w:p', $ns)
$text = foreach ($p in $paragraphs) {
    $runs = $p.SelectNodes('.//w:t', $ns)
    ($runs | ForEach-Object { $_.InnerText }) -join ''
}
$text -join "`n" | Out-File -FilePath 'c:\Dev\METAai\session_text.txt' -Encoding UTF8
Write-Host "Done! Extracted $($paragraphs.Count) paragraphs"
