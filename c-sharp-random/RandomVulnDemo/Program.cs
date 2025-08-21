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

    string tokenString = TokenEncoder.MakePasswordResetToken(tokenNumber);

    context.Response.ContentType = "text/html; charset=utf-8";
    var html = new StringBuilder()
        .Append("<html><head><title>Password Reset</title></head><body>")
        .Append("<h1>Password Reset Token</h1>")
        .Append($"<p><strong>Token</strong>: <code>{tokenString}</code></p>")
        .Append($"<p><small>Derived from Random.Next(min,max) value.</small></p>")
        .Append($"<p><strong>Timestamp (UTC)</strong>: {DateTime.UtcNow:O}</p>")
        .Append("<hr/>")
        .Append("<p style='color:#b00'><strong>Warning:</strong> This endpoint intentionally uses <code>new Random()</code> per request and is cryptographically unsafe. It is for reproduction of the vulnerability only. Do not use in production.</p>")
        .Append("</body></html>")
        .ToString();

    return Results.Content(html);
});

app.Run("http://0.0.0.0:8080");


static class TokenEncoder
{
    private const string Base62Alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

    public static string MakePasswordResetToken(int numericCode)
    {
        string payload = ToBase62(numericCode);
        string checksum = ComputeChecksum(numericCode);
        // Typical-looking token format
        return $"pr-{payload}-{checksum}";
    }

    private static string ToBase62(int value)
    {
        if (value == 0)
        {
            return "0";
        }

        var sb = new StringBuilder();
        long v = value;
        while (v > 0)
        {
            int index = (int)(v % 62);
            sb.Insert(0, Base62Alphabet[index]);
            v /= 62;
        }
        // pad to at least 6 chars to look more realistic
        while (sb.Length < 6)
        {
            sb.Insert(0, '0');
        }
        return sb.ToString();
    }

    private static string ComputeChecksum(int value)
    {
        // Non-cryptographic, deterministic checksum derived solely from numeric code
        // Keeps exploitability intact while making token look realistic
        unchecked
        {
            uint c = (uint)value;
            c ^= 0xA5A5A5A5u;
            c *= 2654435761u; // Knuth multiplicative hash
            return (c & 0xFFFFu).ToString("x4");
        }
    }
}


