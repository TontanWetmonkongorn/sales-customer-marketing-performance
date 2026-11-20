(folder as text, file as text, columnTypes as list) as table =>
let
    Source = Csv.Document(
        File.Contents(folder & Character.FromNumber(92) & file),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Headers, columnTypes, "en-US")
in
    Typed
