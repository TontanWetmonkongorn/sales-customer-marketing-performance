$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot
$raw = Import-Csv (Join-Path $project 'data/raw/orders.csv')
$expected = Import-Csv (Join-Path $project 'data/processed/monthly_sales.csv')
$excel = New-Object -ComObject Excel.Application
$excel.DisplayAlerts = $false
$book = $null
try {
    $book = $excel.Workbooks.Add(-4167)
    $summary = $book.Worksheets.Item(1)
    $summary.Name = 'Monthly Sales'
    $data = $book.Worksheets.Add([Type]::Missing, $summary)
    $data.Name = 'Order Values'
    $values = New-Object 'object[,]' ($raw.Count + 1), 2
    $values[0, 0] = 'Month'
    $values[0, 1] = 'Reported Order Value'
    for ($i = 0; $i -lt $raw.Count; $i++) {
        $values[($i + 1), 0] = $raw[$i].order_date.Substring(0, 7)
        $values[($i + 1), 1] = [double]::Parse($raw[$i].order_total, [cultureinfo]::InvariantCulture)
    }
    $last = $raw.Count + 1
    $data.Range("A2:A$last").NumberFormat = '@'
    $data.Range("A1:B$last").Value2 = $values
    $table = $data.ListObjects.Add(1, $data.Range("A1:B$last"), [Type]::Missing, 1)
    $table.Name = 'OrderValues'
    $data.Range("B2:B$last").NumberFormat = '#,##0.00'
    $data.Columns.AutoFit() | Out-Null
    $summary.Range('A1').Value2 = 'Monthly sales | Excel reconciliation'
    $summary.Range('A1').Font.Size = 18
    $summary.Range('A1').Font.Bold = $true
    $summary.Range('A2').Value2 = 'Order value uses the reported total. Currency is unspecified.'
    $summary.Range('A3').Value2 = 'March 2023 and November 2024 are partial months.'
    $cache = $book.PivotCaches().Create(1, 'OrderValues')
    $pivot = $cache.CreatePivotTable($summary.Range('A5'), 'MonthlyOrders')
    $pivot.PivotFields('Month').Orientation = 1
    $field = $pivot.PivotFields('Reported Order Value')
    $pivot.AddDataField($field, 'Total reported value', -4157).NumberFormat = '#,##0.00'
    $pivot.AddDataField($field, 'Orders', -4112).NumberFormat = '#,##0'
    $pivot.TableStyle2 = 'PivotStyleMedium9'
    $summary.Columns.Item('A').ColumnWidth = 15
    $summary.Columns.Item('B').ColumnWidth = 24
    $summary.Columns.Item('C').ColumnWidth = 14
    $summary.Activate()
    foreach ($row in $expected) {
        $value = $pivot.GetPivotData('Total reported value', 'Month', $row.month).Value2
        $count = $pivot.GetPivotData('Orders', 'Month', $row.month).Value2
        if ([math]::Abs($value - [double]$row.reported_order_value) -gt 0.01 -or $count -ne [int]$row.orders) {
            throw "PivotTable and SQL differ for $($row.month)"
        }
    }
    if ($pivot.GetPivotData('Orders').Value2 -ne $raw.Count) { throw 'Unexpected order count' }
    $folder = Join-Path $project 'outputs/excel-reconciliation'
    New-Item -ItemType Directory -Force $folder | Out-Null
    $target = Join-Path $folder 'Monthly Sales Reconciliation.xlsx'
    $book.SaveAs($target, 51)
    Write-Output "Verified $($expected.Count) months and $($raw.Count) orders against SQL. Saved $target"
} finally {
    if ($book) { $book.Close($false) }
    $excel.Quit()
}

