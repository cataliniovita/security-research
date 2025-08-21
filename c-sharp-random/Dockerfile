# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY RandomVulnDemo/RandomVulnDemo.csproj RandomVulnDemo/
RUN dotnet restore RandomVulnDemo/RandomVulnDemo.csproj

COPY RandomVulnDemo/ RandomVulnDemo/
WORKDIR /src/RandomVulnDemo
RUN dotnet publish -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://0.0.0.0:8080
ENTRYPOINT ["dotnet", "RandomVulnDemo.dll"]


