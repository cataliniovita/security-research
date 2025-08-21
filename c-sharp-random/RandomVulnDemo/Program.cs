using System.Text;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => "OK");

// Vulnerable endpoint: uses time-seeded PRNG per request
// This intentionally demonstrates the weakness described in the Doyensec article.
app.MapGet("/password-reset", (HttpContext context, int? min, int? max) =>
{
    int minValue = min ?? 100000;
    int maxValue = max ?? 999999;
    if (maxValue <= minValue)
    {
        maxValue = minValue + 1;
    }

    // Per-request new Random() with default constructor (time-based seed inside)
    var rng = new Random();
    int tokenNumber = rng.Next(minValue, maxValue);

    string tokenString = tokenNumber.ToString();

    context.Response.ContentType = "text/html; charset=utf-8";
    var html = new StringBuilder()
        .Append("<html><head><title>Password Reset</title></head><body>")
        .Append("<h1>Password Reset Token</h1>")
        .Append($"<p><strong>Token</strong>: <code>{tokenString}</code></p>")
        .Append($"<p><strong>Timestamp (UTC)</strong>: {DateTime.UtcNow:O}</p>")
        .Append("<hr/>")
        .Append("<p style='color:#b00'><strong>Warning:</strong> This endpoint intentionally uses <code>new Random()</code> per request and is cryptographically unsafe. It is for reproduction of the vulnerability only. Do not use in production.</p>")
        .Append("</body></html>")
        .ToString();

    return Results.Content(html);
});

app.Run("http://0.0.0.0:8080");


