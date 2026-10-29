param(
    [Parameter(Mandatory = $true)][string]$InputDocx,
    [Parameter(Mandatory = $true)][string]$OutputPdf
)

$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($InputDocx, $false, $true)
    # 17 is Word's wdExportFormatPDF constant.
    $document.ExportAsFixedFormat($OutputPdf, 17)
}
finally {
    if ($document) { $document.Close([ref]$false) }
    if ($word) { $word.Quit() }
}
